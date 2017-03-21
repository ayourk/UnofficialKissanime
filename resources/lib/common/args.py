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


def init():
    return Args()


class Args(object):
    def __init__(self):
        params = dict(helper.queries)
        helper.location('Here are the params: %s' % str(params))
        self.action = params.get('action', None)
        self.srctype = params.get('srctype', None)
        self.value = params.get('value', None)
        self.icon = params.get('icon', None)
        self.fanart = params.get('fanart', None)
        self.full_mc_name = params.get('full_mc_name', None)
        self.base_mc_name = params.get('base_mc_name', None)
        self.imdb_id = params.get('imdb_id', None)
        self.tvdb_id = params.get('tvdb_id', None)
        self.tmdb_id = params.get('tmdb_id', None)
        self.media_type = params.get('media_type', None)

    def override(self, queries):
        self.action = queries.get('action', self.action)
        self.srctype = queries.get('srctype', self.srctype)
        self.value = queries.get('value', self.value)
        self.icon = queries.get('icon', self.icon)
        self.fanart = queries.get('fanart', self.fanart)
        self.full_mc_name = queries.get('full_mc_name', self.full_mc_name)
        self.base_mc_name = queries.get('base_mc_name', self.base_mc_name)
        self.imdb_id = queries.get('imdb_id', self.imdb_id)
        self.tvdb_id = queries.get('tvdb_id', self.tvdb_id)
        self.tmdb_id = queries.get('tmdb_id', self.tmdb_id)
        self.media_type = queries.get('media_type', self.media_type)


args = init()