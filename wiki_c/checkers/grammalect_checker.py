from pathlib import Path

from pygrammalecte import grammalecte_text
from pygrammalecte.pygrammalecte import GrammalecteSpellingMessage

from .checker import Checker

DIR_GRAMMAR_DESTINATION = 'grammar_result'


class GrammalecteChecker(Checker):
    def __init__(self, full=False):
        super(GrammalecteChecker, self).__init__(DIR_GRAMMAR_DESTINATION, full)

        self.personal_dict: Set[str] = set()
        self.code_open = False
        self.first_warn = False
        lines = Path('dict').read_text(encoding='UTF-8')

        for line in lines.splitlines():
            word = line.strip()
            self.personal_dict.add(word.lower())
            self.personal_dict.add(word.title().lower())

    def parse(self, content):
        try:
            self._parse(content)
        except Exception as e:
            self.write_error(e, content)
            return

    def _parse(self, content):
        warnings = ''
        content_list = content.splitlines()
        self.last_line = 0

        g_lines = grammalecte_text(content)
        warn = next(g_lines)
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

    def _set_warn(self, message, content_list):
        cr = ''
        target_line = content_list[message.line - 1]
        if type(message) == FakeMessage:
            target_line = content_list[message.line]

        elif self.first_warn and self.last_line != 0 and self.last_line != message.line:
            cr = '\n'
        self.last_line = message.line

        if target_line.find('<code') != -1:
            self.code_open = True
        if target_line.find('</code>') != -1:
            self.code_open = False
        if self.code_open:
            return ''

        if type(message) == FakeMessage:
            return ''

        if type(message) == GrammalecteSpellingMessage:
            word = str(message.word)
            word_l = word.lower()
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
            index_start = target_line.find('<code')
            index_end = target_line.find('</code>')
            if index_start != -1 and index_end != -1:
                sub_str = target_line[index_start + 6:index_end]
                if word in sub_str:
                    return ''

        self.first_warn = True
        warning = "{0}{1} {2} => {3}\n".format(
            cr,
            message.line,
            message.message,
            target_line
        )
        return warning
