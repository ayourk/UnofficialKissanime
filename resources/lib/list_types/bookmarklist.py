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
from resources.lib.list_types.media_container_list import MediaContainerList
from bs4 import BeautifulSoup


class BookmarkList(MediaContainerList):
    ''' PUBLIC FUNCTIONS '''
    def parse(self):
        helper.start('BookmarkList.parse')
        if self.soup == None:
            return

        MediaContainerList.parse(self)
        self.bookmark_dict = {}
        table = self.soup.find('table', class_='listing')
        remove_bookmark_links = table.find_all('a', class_='aRemove')
        for link in remove_bookmark_links:
            self.bookmark_dict[link['mname']] = link['mid']

        helper.end('BookmarkList.parse')

    def _get_contextmenu_items(self, url, name, metadata, media_type):
        items = MediaContainerList._get_contextmenu_items(self, url, name, metadata, media_type)
        remove_id = self.bookmark_dict[name]
        query = self._construct_query(remove_id, 'removeBookmark', metadata, name, media_type)
        cm_item = constants.runplugin % helper.build_plugin_url(query)
        items.insert(1, ('Remove bookmark', cm_item))
        return items