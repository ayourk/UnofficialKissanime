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


import urllib
from resources.lib.common import args, constants, keyboard
from resources.lib.list_types import local_list, media_container_list, episode_list, movie_listing, specials_list, quality_list
from resources.lib.players import videoplayer, autoplayer
from resources.lib.common.helpers import helper


# TEMP
import xbmcgui, xbmc
from resources.lib.metadata.loose_metahandlers import meta


class Controller:
    def main_menu(self):
        helper.start('main_menu')
        local_list.LocalList().add_directories('main_menu')
        helper.end("main_menu")
        return

    def show_list(self):
        helper.start("show_list")
        local_list.LocalList().add_directories(args.value)
        helper.end("show_list")
        return

    def _show_list(self, list):
        list.parse()
        if isinstance(list, episode_list.EpisodeList):
            actual_media_type = list.get_actual_media_type() if args.media_type == 'tvshow' else args.media_type
            if actual_media_type != 'tvshow':
                if actual_media_type == 'special':
                    list = specials_list.SpecialsList(list)
                elif actual_media_type == 'movie':
                    list = movie_listing.MovieListing(list, mismatch=True)
        list.add_items()

    # A media container is a series or movie; it links to the media listings 
    # page, not any actual media.  Thus, a media container list is list of 
    # series and/or movies
    def show_media_container_list(self):
        helper.start('show_media_container_list')
        self._show_list(media_container_list.MediaContainerList())
        helper.end('show_media_container_list')
        return

    def show_media_list(self):
        helper.start('show_media_list')
        self._show_list(episode_list.EpisodeList())
        helper.end('show_media_list')
        return

    def show_quality(self):
        helper.start('show_quality')
        self._show_list(quality_list.QualityList())
        helper.end('show_quality')
        return

    def auto_play(self):
        helper.start('auto_play')
        player = autoplayer.AutoPlayer()
        player.parse()
        player.add_items()
        player.play()        
        helper.end('auto_play')

    def play_video(self):
        helper.start('play_video')
        player = videoplayer.VideoPlayer(args.value)
        player.play()
        helper.end('play_video')

    def search(self):
        helper.start('search')
        search_string = helper.get_user_input('Search for show title')
        if search_string:
            search_string = constants.domain_url + 'Search/Anime?' + urllib.urlencode({'keyword':search_string})
            self._show_list(media_container_list.MediaContainerList(search_string))
        helper.end('search')

    def find_metadata(self):
        helper.start('find_metadata')
        path = xbmc.getInfoLabel('ListItem.FileNameAndPath')
        helper.log_debug('here is the path %s' % path)
        #win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        #curctl = win.getFocus()
        #cursel = curctl.get

        xbmc.executebuiltin('ActivateWindow(busydialog)')
        list = episode_list.EpisodeList()
        list.parse()
        options = list.aliases
        options.insert(0, 'Manual search')
        options.insert(1, args.base_mc_name)
        dialog = xbmcgui.Dialog()
        xbmc.executebuiltin('Dialog.Close(busydialog)')
        search_string = None
        # THIS SHIT WILL NEVER END, PLEASE FIX
        while not search_string:
            idx = dialog.select('Choose a title to search for', options)
            helper.log_debug('User selected index %d' % idx)
            if idx == 0:
                search_string = helper.get_user_input('Manually type the show to find metadata for')
            else:
                search_string = helper.get_user_input('Alter the title if necessary', options[idx])
            if not search_string:
                helper.show_ok_dialog(['Invalid search query.  Please try again'])

        # I have the string to search for; now I need to feed it to my metadata query thing
        metadata, media_type = media_container_list.MediaContainerList(None)._get_metadata(search_string)
        helper.log_debug('metadata from search string: %s' % str(metadata))
        if metadata.get('tvdb_id', ''):
            meta.update_meta(media_type, args.base_mc_name, imdb_id='', new_tmdb_id=metadata.get('tvdb_id'), new_imdb_id=metadata.get('imdb_id'), )
            #xbmc.executebuiltin('Container.Update')

        helper.end('find_metadata')