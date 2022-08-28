from urllib.parse import urlparse
import asyncio

import tldextract
import aiohttp

from .checker import Checker

DIR_URL_DESTINATION = 'url_result'

async def get(url, session):
    pos = url['pos']
    url = url['url']
    try:
        async with session.head(url=url, allow_redirects=True) as response:
            if response.status != 200:
                return f'{pos} HTTP {response.status} : {url}\n'
    except Exception as e:
        return f'{pos} HTTP {e.__class__} : {url}\n'
    redirect_url =  str(response.url)

    if url == redirect_url and url.startswith("https:"):
        return ''

    if url == redirect_url and url.startswith("http:"):
        return f'{pos} Usage of http : {url}\n'

    if url.replace('http', 'https') == redirect_url:
        return f'{pos} HTTP redirect to HTTPS : {url} => {redirect_url}\n'

    if url.replace('http', 'https') + "/" == redirect_url:
        return f'{pos} HTTP redirect to HTTPS : {url} => {redirect_url}\n'

    hostname = urlparse(url).hostname.rstrip('/')
    if hostname == redirect_url.split('://')[1].rstrip('/'):
        return f'{pos} Url redirect to root path : {url} => {redirect_url}\n'
    redirect_hostname = urlparse(redirect_url).hostname.rstrip('/')

    if tldextract.extract(url).domain != tldextract.extract(redirect_url).domain:
        return f'{pos} Url redirect to an other hostname: {url} => {redirect_url}\n'

    if url.startswith("http:"):
        return f'{pos} Usage of http : {url}\n'

    return ''


class UrlChecker(Checker):
    def __init__(self, full=False):
        super(UrlChecker, self).__init__(DIR_URL_DESTINATION, full)

    def _extract_url(self, line):
        pos = len(line)
        sub_str_list = [' ', '|', ']', '}}', '<', '>', '))']
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
        urls = []

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
            urls.append({ 'pos': pos, 'url': url})

        asyncio.run(self._set_warn(urls))


    async def _set_warn(self, urls):
        async with aiohttp.ClientSession() as session:
            _warnings = await asyncio.gather(*[get(url, session) for url in urls])
        self.warnings += ''.join(_warnings)
