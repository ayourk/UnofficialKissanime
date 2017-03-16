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


from resources.lib.common import constants
from resources.lib.common.args import args
from resources.lib.common.helpers import helper
from resources.lib.appdata import account, lastvisited


class Controller:
    def main_menu(self):
        helper.start('main_menu')
        from resources.lib.list_types.local_list import LocalList
        LocalList().add_directories(self._get_main_menu_src())
        helper.end('main_menu')
        return

    def _get_main_menu_src(self):
        main_menu = constants.main_menu
        last_show_queries = lastvisited.LastVisited().get_last_anime_visited()
        if last_show_queries:
            (last_anime_visited_title, queries) = main_menu[0]
            title = '%s - %s' % (last_show_queries.get('full_mc_name'), last_anime_visited_title)
            queries['icon'] = last_show_queries.get('icon', '')
            queries['fanart'] = last_show_queries.get('fanart', '')
            main_menu[0] = (title, queries)
        return main_menu

    def show_list(self):
        helper.start("show_list")
        from resources.lib.list_types.local_list import LocalList
        LocalList().add_directories(constants.ui_table[args.value])
        helper.end("show_list")
        return

    def _show_list(self, list):
        list.parse()
        from resources.lib.list_types import episode_list, specials_list, movie_listing
        if isinstance(list, episode_list.EpisodeList):
            actual_media_type = list.get_actual_media_type() if args.media_type == 'tvshow' else args.media_type
            if actual_media_type != 'tvshow':
                if actual_media_type == 'special':
                    list = specials_list.SpecialsList(list)
                elif actual_media_type == 'movie':
                    mismatch = (actual_media_type != args.media_type)
                    list = movie_listing.MovieListing(list, mismatch=mismatch)
        list.add_items()

    # A media container is a series or movie; it links to the media listings 
    # page, not any actual media.  Thus, a media container list is list of 
    # series and/or movies
    def show_media_container_list(self):
        helper.start('show_media_container_list')
        from resources.lib.list_types.media_container_list import MediaContainerList
        self._show_list(MediaContainerList())
        helper.end('show_media_container_list')
        return

    def show_media_list(self):
        helper.start('show_media_list')
        from resources.lib.list_types.episode_list import EpisodeList
        self._show_list(EpisodeList())
        lastvisited.LastVisited().update_last_anime_visited()
        helper.end('show_media_list')
        return

    def show_quality(self):
        helper.start('show_quality')
        from resources.lib.list_types.quality_list import QualityList
        self._show_list(QualityList())
        helper.end('show_quality')
        return

    def auto_play(self):
        helper.start('auto_play')
        from resources.lib.players.autoplayer import AutoPlayer
        player = AutoPlayer()
        player.parse()
        player.add_items()
        player.play()        
        helper.end('auto_play')

    def play_video(self):
        helper.start('play_video')
        from resources.lib.players.videoplayer import VideoPlayer
        player = VideoPlayer(args.value)
        player.play()
        helper.end('play_video')

    def search(self):
        helper.start('search')
        search_string = helper.get_user_input('Search for show title')
        if search_string:
            url = helper.domain_url() + 'AdvanceSearch'
            form_data = {'animeName':search_string, 'genres':'0', 'status':''}
            helper.log_debug('Searching for show using url %s and form data %s' % (url, str(form_data)))
            from resources.lib.list_types.media_container_list import MediaContainerList
            self._show_list(MediaContainerList(url, form_data))
        helper.end('search')

    def find_metadata(self):
        helper.start('find_metadata')
        from resources.lib.metadata.metadatafinder import MetadataFinder
        finder = MetadataFinder()
        finder.search_and_update()
        helper.end('find_metadata')

    # The last anime visited entry is really a redirector to the url.  I did 
    # this (instead of having the entry point directly to the anime) so that 
    # widgets for the Last Anime Visited are not hard coded to that specific show.
    def show_last_visited(self):
        helper.start('show_last_visited')
        last_show_queries = lastvisited.LastVisited().get_last_anime_visited()
        if last_show_queries:
            # The relative URL is stored in args, which is a parameter to WebList, the parent of
            # EpisodeList.  We override args with the real relative URL.  When debug_import is on,
            # we need to reload web_list because it's optional url_val parameter is already set to 
            # the value of args.value at the add-on entry point, not at object creation.
            args.override(last_show_queries)
            if helper.debug_import():
                from resources.lib.list_types import episode_list, web_list
                reload(web_list)
                reload(episode_list)
            from resources.lib.list_types.episode_list import EpisodeList
            self._show_list(EpisodeList())
        else:
            helper.show_ok_dialog(['Visit an anime to populate this directory'], 'Last Anime Visited not set')
        helper.end('show_last_visited')

    def _account_operation(self, fn):
        if account.Account().is_logged_in():
            fn()
        else:
            helper.show_error_dialog(['Failed to access account bookmarks.  Please login if you have not already.'])

    def show_bookmark_list(self):
        if account.Account().is_logged_in():
            from resources.lib.list_types.bookmarklist import BookmarkList
            self._show_list(BookmarkList())
        else:
            helper.show_error_dialog(['Failed to access account bookmarks.  Please login if you have not already.'])

    def add_bookmark(self):
        self._account_operation(account.Account().add_bookmark)

    def remove_bookmark(self):
        self._account_operation(account.Account().remove_bookmark)

    def toggle_bookmark(self):
        self._account_operation(account.Account().toggle_bookmark)

    def account_login_logout(self):
        account.Account().log_in_or_out()
