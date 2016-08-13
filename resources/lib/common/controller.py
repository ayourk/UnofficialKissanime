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


import re, xbmc, xbmcgui, xbmcplugin, urlresolver, xbmcaddon
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
        if helper.get_setting('preset-quality') == 'Individually select':
            self._create_media_list(links, 'media')
        else:
            self._create_media_list(links, 'media', is_folder=False, is_playable=True)
        helper.end("show_media_list")
        return

    # Can either display qualities or play videos directly depending on the settings
    def show_media(self, params):
        helper.start('show_media')
        html = self._get_html_from_params(params)
        if helper.get_setting('preset-quality') != 'Individually select':
            self._find_and_play_media_with_preset_quality(html)
            return
        
        media_list = lists.GenericList()
        if html != '':
            soup = BeautifulSoup(html)
            encoded_links = soup.find(id='selectQuality').find_all('option')
            for option in encoded_links:
                quality = option.string
                link_val = option['value'].decode('base-64')
                media_list.add_dir_item(quality, {'srctype':'web', 'value':link_val, 'action':'play'}, isFolder=False, isPlayable=True)
        media_list.end_dir()
            
        helper.end('show_media')
        return

    def play_video(self, params):
        url = params['value']
        play_item = xbmcgui.ListItem(path=urlresolver.resolve(url))
        xbmcplugin.setResolvedUrl(helper.handle, True, play_item)

    def _find_and_play_media_with_preset_quality(self, html):
        helper.start('_find_and_play_media_with_preset_quality')
        if html == '':
            return # an error dialog should've already appeared at this point

        preset_quality = int(helper.get_setting('preset-quality').strip('p'))
        helper.log_debug("Searching for media with the preset quality: %dp" % preset_quality)
        url_to_play = None
        soup = BeautifulSoup(html)
        encoded_links = soup.find(id='selectQuality').find_all('option')
        for option in encoded_links:
            quality = option.string
            if preset_quality >= int(quality.strip('p')):
                helper.log_debug('Found media to play at matching quality: %s' % quality)
                url_to_play = option['value'].decode('base-64')
                break

        assert(len(encoded_links) > 0)
        if url_to_play == None:
            helper.log_debug('No matching quality found; using the lowest available')
            url_to_play = encoded_links[-1]['value'].decode('base-64')
        self.play_video({'value':url_to_play})
        helper.end('_find_and_play_media_with_preset_quality')
        return

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

    def _create_media_list(self, links, action, filter=None, next_action=None, is_folder=True, is_playable=False):
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
            media_list.add_dir_item(name, {'srctype':'web', 'value':link['href'], 'action':action}, isFolder=is_folder, isPlayable=is_playable)
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