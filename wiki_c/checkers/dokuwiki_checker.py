from .checker import Checker, DokuwikiTagInLine

DIR_DOKUWIKI_DESTINATION = 'dokuwiki_result'


class DokuwikiWarning:
    def __init__(self, pos, line):
        self.pos = pos
        self.line = line
        self.warnings = ''


class DokuwikiUnderlines(DokuwikiWarning):
    def _delete_tags(self, line):
        tag_inline = DokuwikiTagInLine(line)
        tags = tag_inline.give_all_tags()

        for tag in tags:
            line = line.replace(tag, '')

        return line

    def __init__(self, pos, line):
        super(DokuwikiUnderlines, self).__init__(pos, line)
        self.line = self._delete_tags(line)

    def detect(self):
        if self.line.count('__') % 2 != 0:
            self.warnings += f"{self.pos + 1} number of underlines __ is not equal on this line\n"
        return self.warnings


class DokuwikiWikipediaTag(DokuwikiWarning):
    def detect(self):
        pattern = 'https://fr.wikipedia.org/wiki/'
        line = self.line

        while True:
            url_pos = line.find(pattern)
            if url_pos == -1:
                break

            self.warnings += f'{self.pos} url wikipedia : "{line[url_pos:url_pos + len(pattern)]}..." à remplacer par [[wpfr>nom_page]]\n'
            line = line[url_pos + len(pattern):]
        return self.warnings


class DokuwikiChecker(Checker):
    def __init__(self, full=False):
        super(DokuwikiChecker, self).__init__(DIR_DOKUWIKI_DESTINATION, full)

    def parse(self, content):
        content_list = content.splitlines()

        el_open = 0
        last_open_pos = 0

        for pos, line in enumerate(content_list):
            open_el_count = line.count('<note ') + line.count('<note>')
            close_el_count = line.count('</note>')

            ratio = open_el_count - close_el_count
            if ratio == 0:
                continue

            el_open += ratio

            if el_open < 0:
                self.warnings += f'{pos} extra </note>\n'
                el_open = 0
                continue

            if el_open == 1:
                last_open_pos = pos + 1

        if el_open > 0:
            self.warnings += f'{last_open_pos} extra <note>\n'

        for pos, line in enumerate(content_list):
            # open and close <code> on multi lines
            if line.find('<code') != -1:
                self.code_open = True
            if line.find('</code>') != -1:
                self.code_open = False
            if self.code_open or line.rstrip().endswith('</code>'):
                continue

            # open and close <file> on multi lines
            if line.find('<file') != -1:
                self.file_tag_open = True
            if line.find('</file>') != -1:
                self.file_tag_open = False
            if self.file_tag_open or line.rstrip().endswith('</file>'):
                continue
            
            u = DokuwikiUnderlines(pos, line)
            self.warnings += u.detect()
            
            w = DokuwikiWikipediaTag(pos, line)
            self.warnings += w.detect()

            pattern = line.find("''--")
            if pattern == -1:
                pattern = line.find("**--")
            suffix_pattern =  line[pattern + 4: pattern + 5]
            if pattern != -1 and suffix_pattern not in [" ", '-']:
                self.warnings += f"{pos + 1} -- rather than %%--%%\n"

        nb_of_code_open = content.count('<code>') + content.count('<code/')
        nb_of_code_open += content.count('<code ') + content.count('<code|')
        nb_of_code_open += content.count('<code=') + content.count('<code-')
        nb_of_code_open -= content.count('%%<code>%%')

        nb_of_code_close = content.count('</code>')

        if nb_of_code_open != nb_of_code_close:
            self.warnings += f"number of <code ({nb_of_code_open}) and </code> ({nb_of_code_close}) is different\n"
