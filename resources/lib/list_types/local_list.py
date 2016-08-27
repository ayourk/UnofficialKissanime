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
from resources.lib.common import constants


class LocalList(object):
    def add_directories(self, src):
        helper.start('LocalList.add_directories')
        for (name, query) in src:
            icon = query.get('icon', '')
            fanart = query.get('fanart', '')
            helper.add_directory(query, infolabels={'title':name}, img=icon, fanart=fanart, total_items=len(src))
        helper.end_of_directory()
        helper.end('LocalList.add_directories')
        return