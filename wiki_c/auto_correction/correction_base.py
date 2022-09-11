import os
import fnmatch
from pathlib import Path
from os.path import join, isfile
import asyncio

import aiohttp
from aiohttp.client_exceptions import InvalidURL
from scrapy.selector import Selector
import toml

from wiki_c.cli_message import success_message, warning_message, error_message


class FormatOperation:
    prefix_summary = ""

    def __init__(self, data, page):
        self.has_warning = False
        page_sel = Selector(text=page)

        self.data = data

        try:
            self.dokuwiki = page_sel.css('#wiki__text::text').get()
            self.sectok = page_sel.xpath('//input[@name="sectok"]').attrib['value']
            self.date = page_sel.xpath('//input[@name="date"]').attrib['value']
            self.changecheck = page_sel.xpath('//input[@name="changecheck"]').attrib['value']
        except:
            if page.find('<h1 class="sectionedit1 page-header" id="page_bloquee">Page bloquée</h1>') != -1:
                warning_message(f'La page : "{data["path"]}" est actuellement bloquée pour modification par un autre utilisateur.')
                self.has_warning = True
                return
            if page.find('<h1 class="sectionedit1 page-header" id="autorisation_refusee">Autorisation refusée</h1>'):
                warning_message(f'La page : "{data["path"]}" n\'est pas autorisé à être édité.')
                self.has_warning = True
                return
            error_message(data)
            error_message(page)
        self.article_changed = False

        self.dokuwiki_updated = self._replace(self.dokuwiki, self.data['detected_lines'])
        if self.dokuwiki_updated.lstrip().startswith('*'):
            return
        self.dokuwiki_updated = self.dokuwiki_updated.lstrip()

    def _replace(self, doc, detected_lines):
        return doc

    def has_changed(self):
        if self.dokuwiki != self.dokuwiki_updated:
            self.article_changed = True
        return self.article_changed

    def payload(self):
        return {
            'sectok': self.sectok,
            'date': self.date,
            'changecheck': self.changecheck,
            'summary': f"{self.prefix_summary} (détecté et corrigé via le bot wiki-corrector : https://forum.ubuntu-fr.org/viewtopic.php?id=2067892)",
            'do[save]': '',
            'minor': 1,
            'wikitext': self.dokuwiki_updated
        }


async def update(login, password, datas, formatType):
    async with aiohttp.ClientSession() as session:
        connection_payload = {
            'id': 'accueil',
            'do': 'login',
            'u': login,
            'p': password
        }
        async with session.post('https://doc.ubuntu-fr.org/accueil?do=login', data=connection_payload):
            pass

        nb_updated = 0

        for d in datas:
            try:
                async with session.get(d['url']) as r:
                    page = await r.text()
            except InvalidURL:
                error_message(f'invalid url : {d["url"]}')
                continue

            operation = formatType(d, page)
            if operation.has_warning:
                continue

            payload = operation.payload()
            if not operation.has_changed():
                continue

            print('Edition de "%s"' % d['path'].replace('.txt', ''))

            async with session.post(d['url'], data=payload):
                pass
            
            # update file
            with open(d['path'], 'w') as f:
                f.write(d['update_warnings'])

            nb_updated += 1

        print("Nombres de pages édités : %s" % nb_updated)


class BaseDetection:
    pattern = None

    def _extract(self, line):
        return {}

    def get(self, root, _file, dir_url_destination):
        try:
            content = Path(join(root, _file)).read_text(encoding='UTF-8')
        except:
            error_message(f"get content : {join(root, _file)}")
            return
        if not self.pattern in content:
            return
        lines = content.split('\n')
        detected_lines = [self._extract(line) for line in lines if self.pattern in line]

        return {
            'path': join(root, _file),
            'url': 'https://doc.ubuntu-fr.org/%s?do=edit' % join(
                root.replace(f'{dir_url_destination}', ''),
                _file.replace('.txt', '')
            ),
            'detected_lines': detected_lines,
            'update_warnings': '\n'.join([line for line in lines if not self.pattern in line])
        }


def replace_page(login, password, datas, formatType):
    asyncio.run(update(login, password, datas, formatType))


def walk(login, password, dir_url_destination, detectionType, formatType, exclude_dirs=[]):
    datas = []
    for root, _dir, files in os.walk(dir_url_destination):
        if _dir in exclude_dirs:
            continue
        for _file in fnmatch.filter(files, '*'):
            detection = detectionType()
            d = detection.get(root, _file, dir_url_destination)
            if not d:
                continue
            datas.append(d)
    replace_page(login, password, datas, formatType)


def authenticate():
    path = "credentials.toml"
    if isfile(path):
        content = Path(path).read_text(encoding='UTF-8')
        credentials = toml.loads(content)
        return ( credentials['login'], credentials['password'] )

    print('Enter login :')
    login = input()
    print('Enter password :')
    password = input()

    return ( login, password )
