from os.path import join, isfile
from pathlib import Path

from pygrammalecte import grammalecte_text
from pygrammalecte.pygrammalecte import GrammalecteSpellingMessage, GrammalecteGrammarMessage

from .checker import Checker

DIR_GRAMMAR_DESTINATION = 'grammar_result'
DIR_GRAMMAR_DICT = 'grammar_dict'


class FakeMessage:
    def __init__(self, line, message):
        self.line = line
        self.message = message


class GrammalecteChecker(Checker):
    def __init__(self, full=False):
        super(GrammalecteChecker, self).__init__(DIR_GRAMMAR_DESTINATION, full)

        self.personal_dict: Set[str] = set()
        self.code_open = False
        self.file_tag_open = False
        self.first_warn = False

    def parse(self, content):
        lines = Path('dict').read_text(encoding='UTF-8')

        specific_dict_path = join(
            DIR_GRAMMAR_DICT,
            self.root.replace('cache', ''),
            self._file.replace('.dokuwiki', '.txt')
        )
        if isfile(specific_dict_path):
            lines += Path(specific_dict_path).read_text(encoding='UTF-8')

        for line in lines.splitlines():
            word = line.strip()
            self.personal_dict.add(word.lower())
            self.personal_dict.add(word.title().lower())

        self.warnings = self._parse(content)
        try:
            self.warnings = self._parse(content)
        except Exception as e:
            self.write_error(e, content)
            return

    def _parse(self, content):
        warnings = ''
        content_list = content.splitlines()
        self.last_line = 0

        g_lines = grammalecte_text(content)
        try:
            warn = next(g_lines)
        except:
            return ''
        for key, line in enumerate(content_list):
            if warn.line == key + 1:
                warnings += self._set_warn(warn, content_list)
                try:
                    warn = next(g_lines)
                except StopIteration:
                    continue
                while warn.line == key + 1:
                    warnings += self._set_warn(warn, content_list)
                    try:
                        warn = next(g_lines)
                    except StopIteration:
                        break
                continue
            message = FakeMessage(key, line)
            warnings += self._set_warn(message, content_list)
        return warnings

    def __in_tag(self, target_line, word, start_tag, end_tag):
        start_index = target_line.find(start_tag)
        if start_index == -1:
            return False
        end_index = target_line[start_index].find(end_tag)
        if end_index == -1:
            return True
        word_index = target_line[start_index, end_index].find(word)
        if word_index == -1:
            return False
        return True

    '''Ne pas effectuer de vérifications orthographiques et grammaticales dans les tags de la page'''
    def __in_header_tags(self, target_line, word):
        return self.__in_tag(target_line, word, '{{tag>', '}}')

    '''Ne pas effectuer de vérifications orthographiques et grammaticales dans les balises d'images internes'''
    def __in_img(self, target_line, word):
        return self.__in_tag(target_line, word, '{{', '|')

    '''Ne pas effectuer de vérifications orthographiques et grammaticales dans les liens wikipédia'''
    def __in_wikipedia_link(self, target_line, word):
        return self.__in_tag(target_line, word, '[[wpfr>', '|')

    '''Ne pas effectuer de vérifications orthographiques et grammaticales dans les liens internes'''
    def __in_internal_link(self, target_line, word):
        return self.__in_tag(target_line, word, '[[:', '|')

    '''Ne pas effectuer de vérifications orthographiques et grammaticales dans les lignes de code'''
    def __in_code_tag(self, target_line, word):
        return self.__in_tag(target_line, word, '<code ', '</code>')

    '''Ne pas effectuer de vérifications orthographiques et grammaticales dans les lignes de code en ligne'''
    def __in_inline_code_tag(self, target_line, word):
        return self.__in_tag(target_line, word, "''", "''")

    '''Ne pas effectuer de vérifications orthographiques et grammaticales dans les suggestions de dépôts ppa'''
    def __in_ppa_repo(self, target_line, word):
        return self.__in_tag(target_line, word, "**ppa:", "**")

    '''Ne pas effectuer de vérifications orthographiques et grammaticales dans les balises <file>...</file>'''
    def __in_file_tag(self, target_line, word):
        return self.__in_tag(target_line, word, "<file>", "</file>")

    def _set_warn(self, message, content_list):
        cr = ''
        suggestions = ''

        target_line = content_list[message.line - 1]
        if type(message) == FakeMessage:
            target_line = content_list[message.line]

        elif self.first_warn and self.last_line != 0 and self.last_line != message.line:
            cr = '\n'
        self.last_line = message.line

        # open an close <code> on multi lines
        if target_line.find('<code') != -1:
            self.code_open = True
        if target_line.find('</code>') != -1:
            self.code_open = False
        if self.code_open or target_line.rstrip().endswith('</code>'):
            return ''

        # open an close <file> on multi lines
        if target_line.find('<file>') != -1:
            self.file_tag_open = True
        if target_line.find('</file>') != -1:
            self.file_tag_open = False
        if self.file_tag_open or target_line.rstrip().endswith('</file>'):
            return ''

        # dokuwiki rule : if a line start with 2 or more spaces, there is an equivalent of <code>
        if target_line.startswith('  ') and not target_line.startswith('  *'):
            return ''
        if (
            message.message == 'Espace(s) en début de ligne à supprimer : utilisez les retraits de paragraphe (ou les tabulations à la rigueur).'
            and target_line.startswith('  *')
        ):
            return ''

        if type(message) == FakeMessage:
            return ''

        if type(message) == GrammalecteSpellingMessage:
            word = str(message.word)
            word_l = word.lower()

        if type(message) == GrammalecteGrammarMessage:
            word = target_line[message.start:message.end]
            word_l = word.lower()

            if (
                message.message == 'Il manque un espace.'
                and message.suggestions == [' (']
                and target_line[message.start + 1] == '('
            ):
                return ''

            suggestions = ' => suggestions : ' + str(message.suggestions)


        if word_l in self.personal_dict:
            return ''

        if '[[utilisateurs:{0}'.format(word) in target_line:
            return ''
        if '[[:utilisateurs:{0}'.format(word) in target_line:
            return ''
        if '[[:tutoriel:{0}'.format(word) in target_line:
            return ''
        if '[[{0}>'.format(word) in target_line:
            return ''
        if '[[:{0}'.format(word) in target_line:
            return ''
        if '[[apt>{0}|'.format(word) in target_line:
            return ''
        if '|{0}]]'.format(word) in target_line:
            return ''
        if ':{0}]]'.format(word) in target_line:
            return ''

        # open an close <code> on same line
        index_start = target_line.find('<code')
        index_end = target_line.find('</code>')
        if index_start != -1 and index_end != -1:
            sub_str = target_line[index_start + 6:index_end]
            if word in sub_str:
                return ''

        # open an close <file> on same line
        index_start = target_line.find('<file')
        index_end = target_line.find('</file>')
        if index_start != -1 and index_end != -1:
            sub_str = target_line[index_start + 6:index_end]
            if word in sub_str:
                return ''

        if self.__in_header_tags(target_line, word_l):
            return ''
        if self.__in_img(target_line, word_l):
            return ''
        if self.__in_wikipedia_link(target_line, word_l):
            return ''
        if self.__in_internal_link(target_line, word_l):
            return ''
        if self.__in_code_tag(target_line, word_l):
            return ''
        if self.__in_inline_code_tag(target_line, word_l):
            return ''
        if self.__in_ppa_repo(target_line, word_l):
            return ''
        if self.__in_file_tag(target_line, word_l):
            return ''

        self.first_warn = True

        # TODO : à supprimer le jour ou dokuwiki supportera les espaces insécables
        if (
            message.message == 'Il manque un espace insécable.'
            or message.message == 'Avec une unité de mesure, mettez un espace insécable.'
            or message.message == 'Si “Go” est une unité de mesure, il manque un espace insécable. Si le nombre se rapporte au mot suivant, c’est aussi valable.'
        ):
            return ''

        warning = f"{cr}{message.line} {message.message} [[{message.start}:{message.end}]] => {target_line} <|> {word_l}{suggestions}\n"
        return warning
