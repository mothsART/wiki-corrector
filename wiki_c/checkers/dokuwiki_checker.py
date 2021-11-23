from .checker import Checker

DIR_DOKUWIKI_DESTINATION = 'dokuwiki_result'


class DokuwikiChecker(Checker):
    def __init__(self, full=False):
        super(DokuwikiChecker, self).__init__(DIR_DOKUWIKI_DESTINATION, full)

    def parse(self, content):
        pass
