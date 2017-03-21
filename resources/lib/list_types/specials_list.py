# -*- coding: utf-8 -*-
'''
    The Unofficial KissAnime Plugin, aka UKAP - a plugin for Kodi
    Copyright (C) 2016 dat1guy

    This file is part of UKAP.

    UKAP is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    UKAP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with UKAP.  If not, see <http://www.gnu.org/licenses/>.
'''


from resources.lib.common.helpers import helper
from resources.lib.list_types.episode_list import EpisodeList


class SpecialsList(EpisodeList):
    def __init__(self, episode_list=None):
        if not episode_list:
            EpisodeList.__init__(self)
        else:
            self.html = episode_list.html
            self.soup = episode_list.soup
            self.links = episode_list.links
            self.genres = episode_list.genres
            self.aliases = episode_list.aliases
            self.first_air_date = episode_list.first_air_date
            self.season = episode_list.season
            self.num_episodes = episode_list.num_episodes
            self.bookmark_id = episode_list.bookmark_id
            self.related_links = episode_list.related_links
            from resources.lib.metadata.loose_metahandlers import meta
            self.meta = meta
            from resources.lib.common.nethelpers import net, cookies
            self.net, self.cookies = net, cookies

    ''' PUBLIC FUNCTIONS '''
    def add_items(self):
        helper.start('SpecialsList.add_items')

        action, is_folder = self._get_action_and_isfolder()
        icon, fanart = self._get_art_for_season0()
        
        for link in self.links:
            name = link.string.strip()
            url = link['href']
            metadata = self.get_metadata(name)
            query = self._construct_query(url, action, metadata)
            helper.add_directory(query, metadata, img=icon, fanart=fanart, is_folder=is_folder)

        self._add_related_links()
        self._add_bookmark_link()

        helper.end_of_directory()
        helper.end('SpecialsList.add_items')
        return

    def get_metadata(self, name):
        return {'title' : name}