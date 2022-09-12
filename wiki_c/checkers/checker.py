import os
from os.path import join, isfile
from pathlib import Path
from datetime import datetime

from ..state import State


class Checker:
    def __init__(self, _dir, full=False):
        self.dir = _dir
        self.full = full
        self.state = State(_dir)
        self.index = self.state.get_index()
        self.state.create_index(full)

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
