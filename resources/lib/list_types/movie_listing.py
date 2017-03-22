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
from resources.lib.common.args import args
from resources.lib.list_types.episode_list import EpisodeList


class MovieListing(EpisodeList):
    def __init__(self, episode_list=None, mismatch=False):
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
            self.mismatch = mismatch
            from resources.lib.metadata.loose_metahandlers import meta
            self.meta = meta
            from resources.lib.common.nethelpers import net, cookies
            self.net, self.cookies = net, cookies
        
    ''' PUBLIC FUNCTIONS '''
    def add_items(self):
        helper.start('MovieListing.add_items')
        helper.set_content('movies')

        action, is_folder = self._get_action_and_isfolder()

        for link in self.links:
            name = link.string.strip()
            url = link['href']
            if self.mismatch:
                metadata = self.get_metadata(self.clean_name(args.full_mc_name))
                if self.meta.is_metadata_empty(metadata, 'movie'):
                    metadata = self.get_metadata(args.base_mc_name)
            else:
                metadata = self.get_metadata(args.base_mc_name)
            query = self._construct_query(url, action, metadata)
            metadata['title'] = name
            contextmenu_items = self._get_contextmenu_items(url, name)
            helper.add_directory(query, metadata, img=args.icon, fanart=args.fanart, is_folder=is_folder, contextmenu_items=contextmenu_items)

        self._add_related_links()
        self._add_bookmark_link()

        helper.end_of_directory()
        helper.end('MovieListing.add_items')
        return

    def get_metadata(self, name):
        if helper.get_setting('enable-metadata') == 'false':
            return {}

        # If we have no previous metadata, and this isn't a mismatch, then
        # we've already had a legitimate try with no luck.
        if not self.mismatch and (args.imdb_id == None and args.tmdb_id == None):
            helper.log_debug('Not a mismatch and no previous results for movie')
            return {}
        
        imdb_id = args.imdb_id if args.imdb_id and not self.mismatch else ''
        tmdb_id = args.tmdb_id if args.tmdb_id and not self.mismatch else ''
        should_update = self.mismatch
        metadata = self.meta.get_meta('movie', name, imdb_id, tmdb_id, update=should_update)

        # Update the tvshow cache to nothing for this name 
        if self.mismatch:
            self.meta.update_meta_to_nothing('tvshow', name)
            helper.log_debug('Movie mismatch - new meta: %s' % str(self.meta))

        return metadata
