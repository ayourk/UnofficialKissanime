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


from resources.lib.list_types.episode_list import EpisodeList


class MovieListing(EpisodeList):
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
        
    def add_items(self):
        return