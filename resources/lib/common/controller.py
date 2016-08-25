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


from resources.lib.common import args
from resources.lib.list_types import local_list, media_container_list, episode_list, movie_listing, specials_list, quality_list
from resources.lib.players import videoplayer, autoplayer
from resources.lib.common.helpers import helper


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
        player = autoplay.AutoPlayer()
        player.parse()
        player.add_items()
        player.play()        
        helper.end('auto_play')

    def play_video(self):
        helper.start('play_video')
        player = videoplayer.VideoPlayer(args.value)
        player.play()
        helper.end('play_video')
