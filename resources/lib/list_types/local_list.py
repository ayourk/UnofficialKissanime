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
from resources.lib.common import constants


class LocalList(object):
    ''' PUBLIC FUNCTIONS '''
    def add_directories(self, src):
        helper.start('LocalList.add_directories')
        helper.set_content('addons')
        for (name, query) in src:
            icon = query.get('icon', '')
            fanart = query.get('fanart', '')
            helper.add_directory(query, infolabels={'title':name}, img=icon, fanart=fanart, total_items=len(src))
        helper.end_of_directory()
        helper.end('LocalList.add_directories')
        return