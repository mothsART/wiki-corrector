import os
from os.path import isfile, join
from datetime import datetime

import toml

class State:
    def __init__(self, _dir):
        self.path = join(_dir, 'index.toml')
        os.makedirs(_dir, exist_ok=True)

    def get_index(self):
        if not isfile(self.path):
            return None
        with open(self.path, 'r') as f:
            index = toml.loads(f.read())
        return index

    def update_index(self, index):
        index['last_date'] = datetime.now()
        index['finished'] = 'true'
        with open(self.path, 'w') as f:
            toml.dump(index, f)

    def create_index(self, force_update=False):
        index = self.get_index()
        if not force_update and index:
            return index

        toml_str = """
        first_date = {0},
        last_date = {0}
        finished = false
        """.format(datetime.now())
        index = toml.loads(toml_str)
        with open(self.path, 'w') as f:
            toml.dump(index, f)
        return index

    def is_finished(self):
        index = self.get_index()
        if not index:
            return False
        if index['finished'] == 'true':
            return True
        return False
