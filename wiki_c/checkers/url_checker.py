import requests
from requests.exceptions import (
    ConnectionError, MissingSchema, InvalidURL,
    TooManyRedirects, ReadTimeout
)

from .checker import Checker

DIR_URL_DESTINATION = 'url_result'


class UrlChecker(Checker):
    def __init__(self, full=False):
        super(UrlChecker, self).__init__(DIR_URL_DESTINATION, full)

    def _extract_url(self, line):
        pos = len(line)
        sub_str_list = [' ', '|', ']', '}}']
        for sub_str in sub_str_list:
            tmp_pos = line.find(sub_str)
            if tmp_pos != -1 and tmp_pos < pos:
                pos = tmp_pos
        tmp_pos = line.find('))')
        if tmp_pos != -1 and tmp_pos < pos:
            pos = tmp_pos + 1
        return line[:pos]

    def parse(self, content):
        content_list = content.splitlines()

        for pos, line in enumerate(content_list):
            http_start_pos = line.find('https://')
            if http_start_pos == -1:
                http_start_pos = line.find('http://')
            if http_start_pos == -1:
                continue
            url = self._extract_url(line[http_start_pos:])
            if url.find('...') != -1:
                # this URL is an example
                continue
            self.warnings += self._set_warn(pos, url)

    def _set_warn(self, pos, url):
        #print(f'{pos} => {url}')
        try:
            r = requests.head(url, timeout=10, allow_redirects=True)
        except (ConnectionError, MissingSchema, InvalidURL, TooManyRedirects, ReadTimeout) as e:
            return f'{pos} HTTP 500 {type(e).__name__} : {url}\n'

        status_code = r.status_code
        if status_code == 200:
            return ''
        return f'{pos} HTTP {status_code} : {url}\n'
