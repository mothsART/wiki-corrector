import toml

from os.path import join, isfile
from pathlib import Path

from pygrammalecte import grammalecte_text
from pygrammalecte.pygrammalecte import GrammalecteSpellingMessage, GrammalecteGrammarMessage

from .checker import Checker, DokuwikiTagInLine

DIR_GRAMMAR_DESTINATION = 'grammar_result'
DIR_GRAMMAR_DICT = 'grammar_dict'
DIR_GRAMMAR_BLACKLIST = 'grammar_blacklist'


class FakeMessage:
    def __init__(self, line, message):
        self.line = line
        self.message = message


class GrammalecteChecker(Checker):
    def __init__(self, full=False):
        super(GrammalecteChecker, self).__init__(DIR_GRAMMAR_DESTINATION, full)

        self.personal_dict: Set[str] = set()
        self.first_warn = False
        self.blacklist = {}

    def parse(self, content):
        lines = Path('dict').read_text(encoding='UTF-8')

        specific_dict_path = join(
            DIR_GRAMMAR_DICT,
            self.root.replace('cache', ''),
            self._file.replace('.dokuwiki', '.txt'),
        )
        if isfile(specific_dict_path):
            lines += Path(specific_dict_path).read_text(encoding='UTF-8')

        for line in lines.splitlines():
            word = line.strip()
            self.personal_dict.add(word.lower())
            self.personal_dict.add(word.title().lower())

        blacklist_path = join(
            DIR_GRAMMAR_BLACKLIST,
            self.root.replace('cache', ''),
            self._file.replace('.dokuwiki', '.toml'),
        )
        if isfile(blacklist_path):
            self.blacklist = toml.loads(
                Path(blacklist_path).read_text(encoding='UTF-8')
            )

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

    def is_blacklisted(self, message):
        if self.blacklist == {}:
            return False

        for inc in self.blacklist['falsepositive']:
            if message.line != int(self.blacklist['falsepositive'][inc]['line']):
                continue
            if message.start != int(self.blacklist['falsepositive'][inc]['col_start']):
                continue
            if message.end != int(self.blacklist['falsepositive'][inc]['col_end']):
                continue
            if message.message.replace(u'\xa0', u' ') != self.blacklist['falsepositive'][inc]['message']:
                continue
            return True
        return False

    def _set_warn(self, message, content_list):
        cr = ''
        suggestions = ''

        target_line = content_list[message.line - 1]
        if type(message) == FakeMessage:
            target_line = content_list[message.line]

        elif self.first_warn and self.last_line != 0 and self.last_line != message.line:
            cr = '\n'
        self.last_line = message.line

        # open and close <code> on multi lines
        if target_line.find('<code') != -1:
            self.code_open = True
        if target_line.find('</code>') != -1:
            self.code_open = False
        if self.code_open or target_line.rstrip().endswith('</code>'):
            return ''

        # open and close <file> on multi lines
        if target_line.find('<file') != -1:
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

        if self.is_blacklisted(message):
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

            suggestions = ' => suggestions : ' + str(message.suggestions.sort())

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

        tag_inline = DokuwikiTagInLine(target_line)
        if tag_inline.is_in_all_tags(word_l):
            return ''

        #if tag_inline.is_in_underline_expression(target_line, word_l):
        #    return True

        # underline
        if target_line.startswith('__') and target_line.endswith('__'):
            return ''

        # dokuwiki table
        if (
            (target_line.startswith('| ') or target_line.startswith('^ '))
            and message.message == 'Espace(s) surnuméraire(s) à supprimer.'
        ):
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
