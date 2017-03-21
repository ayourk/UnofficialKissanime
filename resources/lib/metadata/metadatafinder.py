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


from resources.lib.common.args import args
from resources.lib.common.helpers import helper
from resources.lib.list_types import episode_list, media_container_list


class MetadataFinder(object):
    def __init__(self):
        helper.show_busy_notification()
        from resources.lib.metadata.loose_metahandlers import meta
        self.meta = meta
        self.ep_list = episode_list.EpisodeList()
        self.ep_list.parse()
        self.options = ['Manual search', args.base_mc_name] + self.ep_list.aliases
        helper.close_busy_notification()

    def search_and_update(self):
        while True:
            idx = helper.present_selection_dialog('Choose a title to search for', self.options)
            helper.log_debug('User selected index %d' % idx)
            default_text = self.options[idx] if idx != 0 else ''
            search_string = helper.get_user_input('Type the show to find metadata for', default_text)
            if search_string == None:
                helper.log_debug('User cancelled manual metadata search')
                return
            elif not search_string:
                helper.show_ok_dialog(['Invalid search query.  Please try again'])
            else:
                break

        helper.show_busy_notification()
        mc_list = media_container_list.MediaContainerList(None)
        metadata, media_type = mc_list._get_metadata(search_string)

        # Grab the ID and the actual title, which might have gotten stripped of
        # the year because of a mismatch...
        if media_type == 'tvshow':
            tmdb_id = metadata.get('tvdb_id', '')
            actual_title = mc_list._clean_tv_show_name(mc_list._clean_name(args.full_mc_name))
        else:
            tmdb_id = metadata.get('tmdb_id', '')
            actual_title = mc_list._clean_name(args.full_mc_name)

        helper.log_debug('Metadatafinder results: %s, %s, %s' % (tmdb_id, media_type, metadata))
        if tmdb_id:
            helper.log_debug('Found metadata from search for %s; refreshing the page' % args.base_mc_name)
            self.meta.update_meta(media_type, actual_title, imdb_id='', new_tmdb_id=tmdb_id, new_imdb_id=metadata.get('imdb_id'))
            helper.refresh_page()
        else:
            helper.show_ok_dialog(['Did not find any metadata from the search query.  Please try again.'])
        helper.close_busy_notification()