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
    cleaned_name = cleaned_name[:-8] if re.search('( \(1080p\))$', cleaned_name) != None else cleaned_name
    cleaned_name = cleaned_name[:-8] if re.search('( \((720|480|360)p\))$', cleaned_name) != None else cleaned_name
    return cleaned_name

def clean_tv_show_name(name):
    cleaned_name = name[:-9] if re.search('( Season [0-9])$', name) != None else name
    cleaned_name = cleaned_name.replace(' (TV)', '').replace(' Second Season', '').replace(' 2nd Season', '')
    cleaned_name = cleaned_name[:-3] if re.search('( S[0-9])$', cleaned_name) != None else cleaned_name
    cleaned_name = cleaned_name[:-2] if re.search('( [0-9])$', cleaned_name) != None else cleaned_name
    cleaned_name = cleaned_name[:-2] if re.search('( II)$', cleaned_name) != None else cleaned_name
    return cleaned_name

def get_art_and_labels(name):
    helper.start('get_art_and_labels name: %s' % name)
    icon, thumb, labels, fanart, base_name, media_type = None, None, None, '', '', ''
    if helper.get_setting('enable-metadata') == 'true' and name != 'Next' and name != 'Last':
        name_for_movie_search = clean_name(name)
        name_for_tv_search = clean_tv_show_name(name_for_movie_search)
        base_name = name_for_tv_search
        media_type = 'tvshow'

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
                    metadata = meta.update_meta('tvshow', name_for_tv_search, imdb_id='', new_imdb_id=metadata['imdb_id'])
                    base_name = name_for_tv_search[:-7]
            else:
                base_name = name_for_movie_search
                media_type = 'movie'

        if (metadata.has_key('tvdb_id') and metadata['tvdb_id'] != '') or (metadata.has_key('tmdb_id') and metadata['tmdb_id'] != ''):
            icon = metadata['cover_url']
            thumb = metadata['cover_url']
            fanart = metadata['backdrop_url']
            labels = metadata
    helper.end('get_art_and_labels')
    return (icon, thumb, fanart, labels, base_name, media_type)


class MediaContainerList(BaseList):
    def add_dir_item(self, name, query, isFolder=True, isPlayable=False, total_items=0):
        (icon, thumb, fanart, labels, base_name, media_type) = get_art_and_labels(name)
        if labels != None and labels.has_key('imdb_id'):
            query['imdb_id'] = labels['imdb_id']
        else:
            query['imdb_id'] = ''
        query['mc_name'] = name # Media Container name
        query['base_name'] = base_name
        query['media_type'] = media_type
        BaseList.add_dir_item(self, name, query, thumb, icon, fanart, labels, isFolder, isPlayable, total_items)
        return


class MediaList(BaseList):
    def __init__(self):
        BaseList.__init__(self)
        helper.log_debug('here is the AoT metadata list %s' % str(meta.get_episodes_meta('Shingeki no Kyojin', 'tt2560140', '2013-04-06', 25)))

    def add_dir_item(self, name, query, isFolder=True, isPlayable=False, total_items=0):
        icon, thumb, fanart, labels, base_name = None, None, None, '', ''#get_art_and_labels(name)
        BaseList.add_dir_item(self, name, query, thumb, icon, fanart, labels, isFolder, isPlayable, total_items)
        return

    def add_dir_items(self, link_tuples, media_container_name, imdb_id, base_name, media_type, first_air_date, genres, aliases, isFolder=True, isPlayable=False):
        # Determine if this is a movie by examining the genres
        if 'Movie' in genres:
            if media_type == 'tvshow':
                helper.log_debug('|COUNT|MISMATCH| %s' % media_container_name)
                return
            # We have a movie, let's handle this differently
            helper.log_debug('|COUNT|MOVIE| %s' % media_container_name)
            return


        if '(OVA)' in media_container_name or ' Specials' in media_container_name:
            # We have a special, let's handle just use the season 0 data along with the show banner
            helper.log_debug('|COUNT|OVA| %s' % media_container_name)
            return

        # Otherwise, we have a tv show.  The most reliable way to figure out 
        # what data to use is to use the first air date with the number of 
        # episodes
        if first_air_date != '':
            helper.log_debug('|COUNT|AIR| %s' % media_container_name)
            return

        # The next best thing is to examine the full name vs the base name and 
        # look for any season stuff
        clean_mc_name = clean_name(media_container_name)
        leftovers = clean_mc_name.replace(base_name, '')
        if season_in_name(leftovers):
            helper.log_debug('|COUNT|BASE| %s' % media_container_name)
            # We have a season, let's extract it and work from there
            return

        # The next best thing after that is to examine the alternate names and
        # look for any season stuff
        for alias in aliases:
            if season_in_name(alias):
                helper.log_debug('|COUNT|ALIAS| %s' % media_container_name)
                # We probably have a season, let's extract it and work from there
                return

        # I'm really not sure what the next best step is.  It's probably to stop
        # looking for metadata, but I would really rather just assume that we're
        # looking at the first season.  Should probably do some testing to determine
        # this (eg, log this and browse a lot to determine what's missing this filter
        # most of the time
        helper.log_debug('|COUNT|LEFTOVER| %s' % media_container_name)

        # Determine number of valid episodes to parse
        #num_valid_episodes = 0


        #meta_list = meta.get_episodes_meta(media_container_name, imdb_id, first_air_date, num_valid_episodes)

        # Replace the episode names with their real episode names


        # Move the specials to the end, if there are any

        return