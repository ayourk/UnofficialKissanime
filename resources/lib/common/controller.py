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
from datetime import datetime
from resources.lib.common import constants, args, lists
from resources.lib.list_types import local_list, media_container_list
from resources.lib.common.helpers import helper
from resources.lib.common.nethelpers import net, cookies
from bs4 import BeautifulSoup


# DEBUG
import time, sys


def youve_got_to_be_kidding(date_str, format):
    try:
        return datetime.strptime(date_str, format)
    except TypeError:
        return datetime(*(time.strptime(date_str, format)[0:6]))


class Controller:
    def main_menu(self):
        helper.start("main_menu")
        local_list.LocalList().add_directories(constants.main_menu)
        helper.end("main_menu")
        return

    def show_list(self):
        helper.start("show_list")
        src = constants.ui_table[args.value]
        local_list.LocalList().add_directories(src)
        helper.end("show_list")
        return

    # A media container is a series or movie; it links to the media page, not any actual media
    def show_media_container_list(self):
        helper.start('show_media_container_list')
        list = media_container_list.MediaContainerList()
        list.parse()
        list.add_items()



        """html = self._get_html()
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
        self._create_media_list(links, 'mediaList', '(\?id=)', next_action)"""
        helper.end('show_media_container_list')
        return

    def show_media_list(self):
        helper.start('show_media_list')
        html = self._get_html()
        links = []
        if html != '':
            soup = BeautifulSoup(html)
            links = soup.find('table', class_='listing').find_all('a')
            helper.log_debug('# of links found: %d' % len(links))
            spans = soup.find_all('span', class_='info')
            # We can determine if the media is a movie or not examining the genres
            genres = []
            span = [span for span in spans if span.string == 'Genres:']
            if span != []:
                genre_links = span[0].parent.find_all('a')
                genres = [link.string for link in genre_links]
                helper.log_debug('Found the genres: %s' % str(genres))
            # We'll try to determine the episode list from the first date
            first_air_date = ''
            span = [span for span in spans if span.string == 'Date aired:']
            if span != []:
                air_date = span[0].next_sibling.encode('ascii', errors='ignore').strip().split(' to ')[0]
                air_datetime = youve_got_to_be_kidding(air_date, '%b %d, %Y')
                first_air_date = air_datetime.strftime('%Y-%m-%d')
                helper.log_debug('Found the first air date: %s' % str(first_air_date))
            # We'll try to determine the season from the alternate names, if necessary
            aliases = []
            span = [span for span in spans if span.string == 'Other name:']
            if span != []:
                alias_links = span[0].parent.find_all('a')
                # Only keep aliases that do not contain CJK (eg, Japanese) characters
                f = lambda c: ord(c) > 0x3000
                aliases = [link.string for link in alias_links if filter(f, link.string) == u'']
                helper.log_debug('Found the aliases: %s' % str(aliases))

        links.reverse() # sort episodes in ascending order by default

        if helper.get_setting('preset-quality') == 'Individually select':
            #self._create_media_list(links, 'media')
            is_folder = True; is_playable = False
        else:
            #self._create_media_list(links, 'media', is_folder=False, is_playable=True)
            is_folder=False; is_playable=True

        links = [(link.string.strip(), link['href']) for link in links]
        lists.MediaList().add_dir_items(links, args.full_mc_name, args.imdb_id, args.base_mc_name, args.media_type, first_air_date, genres, aliases, is_folder, is_playable)
        media_list = lists.MediaList()
        media_list.end_dir()
        helper.end("show_media_list")
        return

    # Can either display qualities or play videos directly depending on the settings
    def show_media(self):
        helper.start('show_media')
        html = self._get_html()
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

    def play_video(self):
        url = urlresolver.resolve(args.value)
        helper.resolve_url(url)

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

    def _get_html(self):
        assert(args.srctype == 'web')
        url_val = args.value
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
        total_items = 0 if filter != None else len(links)
        for link in iter_links:
            if filter != None and re.search(filter, link['href']) != None:
                continue
            name = link.string.strip()
            media_list.add_dir_item(name, {'srctype':'web', 'value':link['href'], 'action':action}, isFolder=is_folder, isPlayable=is_playable, total_items=total_items)
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