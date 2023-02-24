import os
from os.path import join, isfile
from pathlib import Path
from datetime import datetime

from ..state import State


class DokuwikiTagInLine:
    def __init__(self, line):
        self.line = line

    def __is_in_tag(self, word, start_tag, end_tag):
        start_index = self.line.find(start_tag)
        if start_index == -1:
            return False
        end_index = self.line[start_index].find(end_tag)
        if end_index == -1:
            return True
        word_index = self.line[start_index, end_index].find(word)
        if word_index == -1:
            return False
        return True

    '''Est-ce qu'on est dans les tags de la page ?'''
    def is_in_header_tags(self, word):
        return self.__is_in_tag(word, '{{tag>', '}}')

    '''Est-ce qu'on est dans les balises d'images internes ?'''
    def is_in_img(self, word):
        return self.__is_in_tag(word, '{{', '|')

    '''Est-ce qu'on est dans les liens wikipédia ?'''
    def is_in_wikipedia_link(self, word):
        return self.__is_in_tag(word, '[[wpfr>', '|')

    '''Est-ce qu'on est dans les liens internes ?'''
    def is_in_internal_link(self, word):
        return self.__is_in_tag(word, '[[:', '|') or self.__is_in_tag(word, '[[', '|')

    '''Est-ce qu'on est dans les lignes de code en ligne ?'''
    def is_in_inline_code_tag(self, word):
        if self.__is_in_tag(word, "''", "''"):
            return True

    '''Est-ce qu'on est dans les expressions soulignés ?'''
    def is_in_underline_expression(self, word):
        if self.__is_in_tag(word, "__", "__"):
            return True

    '''Est-ce qu'on est dans les suggestions de dépôts ppa ?'''
    def is_in_ppa_repo(self, word):
        return self.__is_in_tag(word, "**ppa:", "**")

    def is_in_inline_tag(self, word, start_tag, end_tag):
        while True:
            index_start = self.line.find(start_tag)
            index_end = self.line.find(end_tag)
            if index_start == -1 or index_end == -1:
                return False

            sub_str = self.line[index_start +  self.line[index_start:].find('>') + 1:index_end]
            if word in sub_str:
                return True
            self.line = self.line[index_end + 7:]

    '''Est-ce qu'on est dans les balises <file>...</file> ?'''
    def is_in_file_tag(self, word):
        return self.__is_in_tag(word, '<file', '</file>')

    '''Est-ce qu'on est dans les lignes de code en ligne ?'''
    def is_in_code_tag(self, word):
        return self.__is_in_tag(word, '<code', '</code>')

    '''Est-ce qu'on est dans un tag dokuwiki ?'''
    def is_in_all_tags(self, word):
        if self.is_in_header_tags(word):
            return True
        if self.is_in_img(word):
            return True
        if self.is_in_wikipedia_link(word):
            return True
        if self.is_in_internal_link(word):
            return True
        if self.is_in_ppa_repo(word):
            return True
        if self.is_in_inline_code_tag(word):
            return True
        if self.is_in_code_tag(word):
            return True
        if self.is_in_file_tag(word):
            return True
        return False

    def give_tags(self, start_tag, end_tag):
        tags = []
        line = self.line

        while True:
            start_tag_pos = line.find(start_tag)
            if start_tag_pos == -1:
                break
            end_tag_pos = line[start_tag_pos + len(start_tag):].find(end_tag)
            if end_tag_pos == -1:
                break
            tags.append(line[start_tag_pos:start_tag_pos + len(start_tag) + end_tag_pos + len(end_tag)])
            line = line[start_tag_pos + len(start_tag) + end_tag_pos + len(end_tag):]
        return tags

    def give_all_tags(self):
        tags = self.give_tags('[[', ']]')
        tags += self.give_tags('{{', '}}')
        tags += self.give_tags('((', '))')
        tags += self.give_tags("''", "''")
        tags += self.give_tags('**', '**')
        tags += self.give_tags('<code', '</code>')
        tags += self.give_tags('<file', '</file>')

        return tags


class Checker:
    def __init__(self, _dir, full=False):
        self.dir = _dir
        self.full = full
        self.state = State(_dir)
        self.index = self.state.get_index()
        self.state.create_index(full)
        self.code_open = False
        self.file_tag_open = False

    def set_path(self, root, _file, len_dir_cache):
        self.warnings = ''
        self.root = root
        self._file = _file
        self.path = self.dir + root[len_dir_cache:] + '/' + _file.replace('.dokuwiki', '.txt')
        self.root = root
        self.len_dir_cache = len_dir_cache

    def create_file(self):
        if isfile(self.path):
            content = Path(self.path).read_text(encoding="UTF-8")
            if content == self.warnings:
                return
            if not self.warnings.strip():
                print(self.path, '[deleted]')
                os.remove(self.path)
                return
            print(self.path, '[updated]')
        else:
            if not self.warnings.strip():
                return
            print(self.path, '[created]')
        with open(self.path, 'w') as f:
            f.write(self.warnings)

    def exist(self):
        if not isfile(self.path):
            return False
        file_date = datetime.fromtimestamp(os.path.getmtime(self.path))
        if not self.full and self.index and self.index['last_date'] > file_date:
            print(self.path, '[exist]')
            return True
        return False

    def write(self):
        os.makedirs(
            self.dir + '/' + self.root[self.len_dir_cache:],
            exist_ok=True
        )
        self.create_file()

    def write_error(self, e, content):
        error = f'path: {self.path}\nexception: {e}\ncontent : {content}'
        with open(join(self.dir, 'crash.log'), 'a') as f:
            f.write(error)
