from pathlib import Path
from os.path import join, isfile

from .checker import Checker

DIR_NOT_ALLOWED_DESTINATION = 'not_allowed_result'
DIR_NOT_ALLOWED_DICT = 'not_allowed_dict'


class NotAllowedChecker(Checker):
    allowed_values = {}
    specific_words = []

    def __init__(self, full=False):
        super(NotAllowedChecker, self).__init__(DIR_NOT_ALLOWED_DESTINATION, full)
        
        allowed_file = Path("allowed_list.txt").read_text(encoding="UTF-8")
        for line in allowed_file.splitlines():
            line = line.lower()
            if not line.startswith('< '):
                continue
            close_pattern_index = line.find(' >')
            close_score_index = line[close_pattern_index + 2:].find('>')
            exception_index = line[close_score_index:].find('< ')

            if exception_index == -1:
                self.allowed_values[line[2:close_pattern_index]] = {
                    'score': line[close_pattern_index + 3:close_pattern_index + 2 + close_score_index]
                }
                continue
            self.allowed_values[line[2:close_pattern_index]] = {
                'score': line[close_pattern_index + 3:close_pattern_index + 2 + close_score_index],
                'exception': line[exception_index:-1]
            }

    def _append(self, pos, v, s, line):
        if 'exception' in self.allowed_values[v] and self.allowed_values[v]['exception'] in line:
            return
        for l in self.specific_words:
            if l in line.lower():
                s_pos_start = line.find(l)
                s_pos_end = s_pos_start + len(l)
                if line.find(l) >= s_pos_start and (s_pos_start + len(v + s)) <= s_pos_end:
                    return
        self.warnings += f'{pos} {v + s} [[niveau : {self.allowed_values[v]["score"]}]]\n'

    def parse(self, content):
        specific_dict_path = join(
            DIR_NOT_ALLOWED_DICT,
            self.root.replace('cache', ''),
            self._file.replace('.dokuwiki', '.txt'),
        )
        if isfile(specific_dict_path):
            lines = Path(specific_dict_path).read_text(encoding='UTF-8')
            for line in lines.splitlines():
                word = line.strip()
                self.specific_words.append(word.lower())

        content_list = content.splitlines()
        
        suffixes = [' ', ',', ';', '!', '?']

        for pos, line in enumerate(content_list):
            for v in self.allowed_values:
                for s in suffixes:
                    if ' ' + v + s in line:
                        self._append(pos, v, s, line)
                    if '.' + v + s in line:
                        self._append(pos, v, s, line)
                    if line.startswith(v + s):
                        self._append(pos, v, s, line)

