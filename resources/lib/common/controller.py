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
from resources.lib.list_types import local_list, media_container_list, episode_list, movie_listing, specials_list
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

    # A media container is a series or movie; it links to the media listings 
    # page, not any actual media.  Thus, a media container list is list of 
    # series and/or movies
    def show_media_container_list(self):
        helper.start('show_media_container_list')
        list = media_container_list.MediaContainerList()
        list.parse()
        list.add_items()
        helper.end('show_media_container_list')
        return

    def show_media_list(self):
        helper.start('show_media_list')
        if args.media_type == 'tvshow':
            list = episode_list.EpisodeList()
            list.parse()
            actual_media_type = list.get_actual_media_type()
            if actual_media_type == 'special':
                list = specials_list.SpecialsList(list)
            elif actual_media_type == 'movie':
                list = movie_listing.MovieListing(list)
            list.add_items()
        elif args.media_type == 'movie':
            list = movie_listing.MovieListing()
            list.parse()
            list.add_items()
        elif args.media_type == 'special':
            list = specials_list.SpecialsList()
            list.parse()
            list.add_items()
        helper.end('show_media_list')
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
            if e.read() == 'The service is unavailable.':
                helper.log_debug('The service is unavailable.')
                helper.show_error_dialog(['Kissanime is reporting that their service is currently unavailable.','','Please try again later.'])
            elif e.read() == "You're browsing too fast! Please slow down.":
                helper.log_debug('Got the browsing too fast error 1.')
                helper.show_error_dialog(["Kissanime is reporting that you're browsing too quickly.",'','Please wait a bit and slow down :)'])
            else:
                helper.log_debug('Failed to grab HTML' + ('' if e == None else ' with exception %s' % str(e)))
                helper.show_error_dialog([
                    'Failed to parse the KissAnime website.',
                    'Please see the error below.  If it has to do with HTTP exception 503, KissAnime may be down; in that case, try again later.',
                    ('Error details: %s' % str(e))
                    ])
        elif html == "You're browsing too fast! Please slow down.":
            helper.log_debug('Got the browsing too fast error 2.')
            helper.show_error_dialog(["Kissanime is reporting that you're browsing too quickly.",'','Please wait a bit and slow down :)'])
            html = ''
        helper.log_debug('HTML is %sempty' % ('' if html == '' else 'not '))
        return html
