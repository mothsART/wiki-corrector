from .checker import Checker

DIR_DOKUWIKI_DESTINATION = 'dokuwiki_result'


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
            pattern = line.find("''--")
            suffix_pattern =  line[pattern + 4: pattern + 5]
            if pattern != -1 and suffix_pattern not in [" ", '-']:
                self.warnings += f"{pos} ''-- rather than ''​%%--%%\n"
