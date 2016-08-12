# -*- coding: utf-8 -*-
'''
    The Unofficial KissAnime Plugin - a plugin for Kodi
    Copyright (C) 2016  dat1guy

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re
from resources.lib.common import lists, constants
from resources.lib.common.helpers import helper
from resources.lib.common.nethelpers import net, cookies
from bs4 import BeautifulSoup


# DEBUG
import time


class Controller:
    def main_menu(self):
        helper.start("main_menu")
        lists.GenericList().add_dir_items(constants.main_menu)
        helper.end("main_menu")
        return

    def show_list(self, params):
        helper.start("show_list")
        assert(params['srctype'] == 'local')
        src = constants.ui_table[params['value']]
        lists.GenericList().add_dir_items(src)
        helper.end("show_list")
        return

    def show_media_container_list(self, params):
        helper.start('show_media_container_list')
        t0 = time.time()
        html = self._get_html_from_params(params)
        t1 = time.time()
        links = []
        if html != '':
            soup = BeautifulSoup(html)
            links = soup.find('table', class_='listing').find_all('a', {'href':re.compile('\/Anime\/')})
            helper.log_debug('# of links found with href=/Anime/: %d' % len(links))
        t2 = time.time()
        # Ignore latest episode links for ongoing series
        self._create_media_list(links, 'mediaList', '(Episode).*(\?id=)')
        t3 = time.time()
        helper.log_notice("get_html: %f, parse: %f, UI: %f, total: %f" % (t1-t0, t2-t1, t3-t2, t3-t0))
        helper.end('show_media_container_list')
        return

    def show_media_list(self, params):
        helper.start('show_media_list')
        t0 = time.time()
        html = self._get_html_from_params(params)
        t1 = time.time()
        links = []
        if html != '':
            soup = BeautifulSoup(html)
            links = soup.find('table', class_='listing').find_all('a')
            helper.log_debug('# of links found: %d' % len(links))
        t2 = time.time()
        links.reverse() # sort episodes in ascending order by default
        self._create_media_list(links, 'media')
        t3 = time.time()
        helper.log_notice("get_html: %f, parse: %f, UI: %f, total: %f" % (t1-t0, t2-t1, t3-t2, t3-t0))
        helper.end("show_media_list")
        return

    def _get_html_from_params(self, params):
        assert(params['srctype'] == 'web')
        url_val = params['value']
        url = constants.domain_url + url_val
        html,e = net.get_html(url, cookies, constants.domain_url)
        if len(html) == 0:
            helper.log_debug('Failed to grab HTML' + ('' if e == None else ' with exception %s' % str(e)))
            # HOW TO FAIL GRACEFULLY HERE
        helper.log_debug('html len %d' % len(html))
        return html

    def _create_media_list(self, links, action, filter=None):
        media_list = lists.MediaContainerList()
        for link in links:
            if filter != None and re.search(filter, link['href']) != None:
                continue
            name = link.string.strip()
            media_list.add_dir_item(name, {'srctype':'web', 'value':link['href'], 'action':action})
        media_list.end_dir()