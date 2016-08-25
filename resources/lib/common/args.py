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


params = dict(helper.queries)
action = params.get('action', None)
srctype = params.get('srctype', None)
value = params.get('value', None)
icon = params.get('icon', None)
fanart = params.get('fanart', None)
full_mc_name = params.get('full_mc_name', None)
base_mc_name = params.get('base_mc_name', None)
imdb_id = params.get('imdb_id', None)
tvdb_id = params.get('tvdb_id', None)
tmdb_id = params.get('tmdb_id', None)
media_type = params.get('media_type', None)

helper.location('Here are the params: %s' % str(params))