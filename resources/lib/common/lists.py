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


import xbmcgui, xbmcplugin
from resources.lib.common.helpers import helper


class BaseList(object):
    def __init__(self):
        return

    def add_dir_item(self, name, query, thumb=None, icon=None, isFolder=True):
        url = helper.build_plugin_url(query)
        helper.log_debug("adding dir item - name: %s, url: %s" % (name, str(url)))
        li = xbmcgui.ListItem(name, "test", iconImage=icon, thumbnailImage=thumb)
        xbmcplugin.addDirectoryItem(handle=helper.handle, url=url, listitem=li, isFolder=isFolder)
        return

    def end_dir(self):
        xbmcplugin.endOfDirectory(helper.handle)
        return

    def add_dir_items(self, src):
        helper.start("add_dir_items")
        for (name, query) in src:
            self.add_dir_item(name, query)
        xbmcplugin.endOfDirectory(helper.handle)
        helper.end("add_dir_items")
        return        


class GenericList(BaseList):
    def __init__(self):
        return


class MediaContainerList(BaseList):
    def __init__(self):
        return


class MediaList(BaseList):
    def __init__(self):
        return