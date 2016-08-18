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


from resources.lib.common.helpers import helper
from resources.lib.list_types.episode_list import EpisodeList


class SpecialsList(EpisodeList):
    ''' PUBLIC FUNCTIONS '''
    def add_items(self):
        helper.start('SpecialsList.add_items')

        action, is_folder = self._get_action_and_isfolder()
        icon, fanart = self._get_art_for_season0()
        
        for link in self.links:
            name = link.string.strip()
            url = link['href']
            metadata = self._get_metadata(name)
            query = self._construct_query(url, action, metadata)
            helper.add_directory(query, metadata, img=icon, fanart=fanart, is_folder=is_folder)

        helper.end_of_directory()
        helper.end('SpecialsList.add_items')
        return

    ''' OVERRIDDEN PROTECTED FUNCTIONS '''
    def _get_metadata(self, name):
        return {'title' : name}