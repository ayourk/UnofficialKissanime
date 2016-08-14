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


import xbmcgui, xbmcplugin, re
from resources.lib.common.helpers import helper
from resources.lib.common.loose_metahandlers import LooseMetaData
#from metahandlers.thetvdbapi import TheTVDB


meta = LooseMetaData()


class BaseList(object):
    def __init__(self):
        return

    def add_dir_item(self, name, query, thumb=None, icon=None, fanart='', info_labels=None, isFolder=True, isPlayable=False, total_items=0):
        url = helper.build_plugin_url(query)
        helper.log_debug("adding dir item - url: %s" % str(url)) # not printing names due to funky characters
        
        li = xbmcgui.ListItem(name, "test", iconImage=icon, thumbnailImage=thumb)
        li.setProperty('IsPlayable', 'true' if isPlayable else 'false')
        li.setProperty('fanart_image', fanart)
        if info_labels != None:
            li.setInfo('video', info_labels)
            li.addContextMenuItems([('Show Information', 'XBMC.Action(Info)')])

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


def clean_name(name):
    cleaned_name = name.replace(' (Sub)', '').replace(' (Dub)', '').replace (' (OVA)', '').replace (' Specials ', '')
    cleaned_name = cleaned_name.replace(' (TV)', '').replace(' Second Season', '').replace(' 2nd Season', '')
    cleaned_name = cleaned_name[:-8] if re.search('( \(1080p\))$', cleaned_name) != None else cleaned_name
    cleaned_name = cleaned_name[:-8] if re.search('( \((720|480|360)p\))$', cleaned_name) != None else cleaned_name
    return cleaned_name

def clean_tv_show_name(name):
    cleaned_name = name[:-9] if re.search('( Season [0-9])$', name) != None else name
    cleaned_name = cleaned_name[:-3] if re.search('( S[0-9])$', cleaned_name) != None else cleaned_name
    cleaned_name = cleaned_name[:-2] if re.search('( [0-9])$', cleaned_name) != None else cleaned_name
    cleaned_name = cleaned_name[:-2] if re.search('( II)$', cleaned_name) != None else cleaned_name
    return cleaned_name

def get_art_and_labels(name):
    icon, thumb, labels, fanart = None, None, None, ''
    if helper.get_setting('enable-metadata') == 'true' and name != 'Next' and name != 'Last':
        name_for_movie_search = clean_name(name)
        name_for_tv_search = clean_tv_show_name(name_for_movie_search)

        # Not sure if movie or tv show; try tv show first
        metadata = meta.get_meta('tvshow', name_for_tv_search)#, year=year)
        helper.log_debug('got metadata %s for show %s' % (metadata, name_for_tv_search))
        # It may be a movie, so let's try that with the general cleaned name
        if metadata['tvdb_id'] == '':
            metadata = meta.get_meta('movie', name_for_movie_search)#, year=year)
            # if movie failed, and if there was a year in the name, try tv without it
            if metadata['tmdb_id'] == '' and re.search('( \([12][0-9]{3}\))$', name_for_tv_search) != None:
                metadata = meta.get_meta('tvshow', name_for_tv_search[:-7], update=True)
                if metadata['imdb_id'] != '':
                    meta.update_meta('tvshow', name_for_tv_search, metadata['imdb_id'])

        if (metadata.has_key('tvdb_id') and metadata['tvdb_id'] != '') or (metadata.has_key('tmdb_id') and metadata['tmdb_id'] != ''):
            icon = metadata['cover_url']
            thumb = metadata['cover_url']
            fanart = metadata['backdrop_url']
            labels = metadata
    return (icon, thumb, fanart, labels)


class MediaContainerList(BaseList):
    def add_dir_item(self, name, query, isFolder=True, isPlayable=False, total_items=0):
        icon, thumb, fanart, labels = get_art_and_labels(name)
        BaseList.add_dir_item(self, name, query, thumb, icon, fanart, labels, isFolder, isPlayable, total_items)
        return


class MediaList(BaseList):
    def add_dir_item(self, name, query, isFolder=True, isPlayable=False, total_items=0):
        icon, thumb, fanart, labels = get_art_and_labels(name)
        BaseList.add_dir_item(self, name, query, thumb, icon, fanart, labels, isFolder, isPlayable, total_items)
        return