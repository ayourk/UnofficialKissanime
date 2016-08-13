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


import re, xbmc, xbmcgui, xbmcplugin, urlresolver
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

    # A media container is a series or movie; it links to the media page, not any actual media
    def show_media_container_list(self, params):
        helper.start('show_media_container_list')
        html = self._get_html_from_params(params)
        links = []
        next_action = None
        if html != '':
            soup = BeautifulSoup(html)
            table = soup.find('table', class_='listing')
            if table == None:
                links = self._parse_upcoming(soup)
            else:
                links = table.find_all('a', {'href':re.compile('\/Anime\/')})
                helper.log_debug('# of links found with href=/Anime/: %d' % len(links))
                # Pagination support
                pager_section = soup.find('ul', class_='pager')
                if pager_section != None:
                    page_links = pager_section.find_all('a')
                    if "Next" in page_links[-2].string:
                        page_links[-2].string = 'Next'
                        page_links[-1].string = 'Last'
                        links.append(page_links[-2])
                        links.append(page_links[-1])
                        next_action = 'mediaContainerList'

        # Ignore latest episode links for ongoing series
        print links
        self._create_media_list(links, 'mediaList', '(Episode).*(\?id=)', next_action)
        helper.end('show_media_container_list')
        return

    def show_media_list(self, params):
        helper.start('show_media_list')
        html = self._get_html_from_params(params)
        links = []
        if html != '':
            soup = BeautifulSoup(html)
            links = soup.find('table', class_='listing').find_all('a')
            helper.log_debug('# of links found: %d' % len(links))
        links.reverse() # sort episodes in ascending order by default
        self._create_media_list(links, 'media')
        helper.end("show_media_list")
        return

    def show_media(self, params):
        helper.start('show_media')
        html = self._get_html_from_params(params)
        links = []
        media_list = lists.GenericList()
        if html != '':
            soup = BeautifulSoup(html)
            encoded_links = soup.find(id='selectQuality').find_all('option')
            for option in encoded_links:
                name = option.string
                link_val = option['value'].decode('base-64')
                media_list.add_dir_item(name, {'srctype':'web', 'value':link_val, 'action':'play'}, isFolder=False, isPlayable=True)
        media_list.end_dir()
        helper.end('show_media')
        return

    def play_video(self, params):
        url_val = params['value']
        print url_val
        url = urlresolver.resolve(url_val)
        print 'url: %s' % url
        play_item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(helper.handle, True, play_item)

    def _get_html_from_params(self, params):
        assert(params['srctype'] == 'web')
        url_val = params['value']
        url = url_val if constants.domain_url in url_val else (constants.domain_url + url_val)
        html,e = net.get_html(url, cookies, constants.domain_url)
        if html == '':
            helper.log_debug('Failed to grab HTML' + ('' if e == None else ' with exception %s' % str(e)))
            helper.show_error_dialog([
                'Failed to parse the KissAnime website.',
                'Please see the error below.  If it has to do with HTTP exception 503, KissAnime may be down; in that case, try again later.',
                ('Error details: %s' % str(e))
                ])
        elif html == 'The service is unavailable.':
            helper.log_debug('The service is unavailable.')
            helper.show_error_dialog(['Kissanime is reporting that their service is currently unavailable.','','Please try again later.'])
            html = ''
        elif html == "You're browsing too fast! Please slow down.":
            helper.log_debug('Got the browsing too fast error.')
            helper.show_error_dialog(["Kissanime is reporting that you're browsing too quickly.",'','Please wait a bit and slow down :)'])
            html = ''
        helper.log_debug('HTML is %sempty' % ('' if html == '' else 'not '))
        return html

    def _create_media_list(self, links, action, filter=None, next_action=None):
        '''
            Helper for creating a media or media container list.  The filter 
            parameter allows us to filter out any links while iterating, and 
            the next_action allows for pagination for both types, if necessary.
        '''
        if action == 'mediaList':
            media_list = lists.MediaContainerList()
        elif action == 'media':
            media_list = lists.MediaList()
        else:
            media_list = lists.GenericList()
        iter_links = links if next_action == None else links[0:-2]
        for link in iter_links:
            if filter != None and re.search(filter, link['href']) != None:
                continue
            name = link.string.strip()
            media_list.add_dir_item(name, {'srctype':'web', 'value':link['href'], 'action':action})
        if next_action != None:
            media_list.add_dir_item(links[-2].string, {'srctype':'web', 'value':links[-2]['href'], 'action':next_action})
            media_list.add_dir_item(links[-1].string, {'srctype':'web', 'value':links[-1]['href'], 'action':next_action})
        media_list.end_dir()

    def _parse_upcoming(self, soup):
        '''
            The content for the upcoming page is not a table, and has spans in
            between the name and the link, so filter those out.
        '''
        assert(soup.find(class_='barTitle').string.strip() == 'Upcoming anime')
        titles = soup.find(class_='barContent').find_all(class_='title')
        links = []
        for title in titles:
            name = title.string
            link = title.parent
            link.string = name
            links.append(link)
        return links