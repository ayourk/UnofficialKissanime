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


import re
from resources.lib.common.helpers import helper
from resources.lib.common.loose_metahandlers import meta
from resources.lib.list_types.web_list import WebList
from bs4 import BeautifulSoup

class MediaContainerList(WebList):
    ''' PUBLIC FUNCTIONS '''
    def parse(self):
        helper.start('MediaContainerList.parse')
        if self.soup == None:
            return

        table = self.soup.find('table', class_='listing')
        if table == None:
            self.links = self.__parse_upcoming(self.soup)
            return
        
        self.links = table.find_all('a', {'href':re.compile('\/Anime\/')})
        helper.log_debug('# of links found with href=/Anime/: %d' % len(self.links))
        
        # Pagination support
        pager_section = self.soup.find('ul', class_='pager')
        if pager_section != None:
            page_links = pager_section.find_all('a')
            if "Next" in page_links[-2].string and "Last" in page_links[-1].string:
                self.links.append(page_links[-2])
                self.links.append(page_links[-1])
                self.has_next_page = True
        helper.end('MediaContainerList.parse')    

    def add_items(self):
        iter_links = self.links[:-2] if self.has_next_page else self.links
        for link in iter_links:
            url = link['href']
            if re.search('(\?id=)', url) != None:
                continue
            name = link.string.strip()
            metadata, media_type = self._get_metadata(name)
            icon, fanart = self._get_art_from_metadata(metadata)
            query = self._construct_query(url, 'mediaList', metadata, name, media_type)
            contextmenu_items = [('Show Information', 'XBMC.Action(Info)')]
            helper.add_directory(query, metadata, img=icon, fanart=fanart, contextmenu_items=contextmenu_items)

        if self.has_next_page:
            query = self._construct_query(self.links[-2]['href'], 'mediaContainerList')
            helper.add_directory(query, {'title':'Next'})
            query = self._construct_query(self.links[-1]['href'], 'mediaContainerList')
            helper.add_directory(query, {'title':'Last'})

        helper.end_of_directory()

    ''' OVERRIDDEN PROTECTED FUNCTIONS '''
    def _get_metadata(self, name):
        helper.start('MediaContainerList._get_metadata - name: %s' % name)
        if helper.get_setting('enable-metadata') == 'false' or name == 'Next' or name == 'Last':
            return {}, ''

        name_for_movie_search = self.__clean_name(name)
        name_for_tv_search = self.__clean_tv_show_name(name_for_movie_search)
        media_type = 'tvshow'

        # Not sure if movie or tv show; try tv show first
        metadata = meta.get_meta('tvshow', name_for_tv_search)#, year=year)
        helper.log_debug('got metadata %s for show %s' % (metadata, name_for_tv_search))
        # It may be a movie, so let's try that with the general cleaned name
        if metadata['tvdb_id'] == '':
            metadata = meta.get_meta('movie', name_for_movie_search)#, year=year)
            # If movie failed, and if there was a year in the name, try tv without it
            if metadata['tmdb_id'] == '' and re.search('( \([12][0-9]{3}\))$', name_for_tv_search) != None:
                metadata = meta.get_meta('tvshow', name_for_tv_search[:-7], update=True)
                if metadata['imdb_id'] != '':
                    metadata = meta.update_meta('tvshow', name_for_tv_search, imdb_id='', new_imdb_id=metadata['imdb_id'])
            elif metadata['tmdb_id'] != '': # otherwise we found a move
                media_type = 'movie'

        helper.end('MediaContainerList._get_metadata')
        return (metadata, media_type)

    ''' PRIVATE FUNCTIONS '''
    def __parse_upcoming(self):
        '''
            The content for the upcoming page is not a table, and has spans in
            between the name and the link, so filter those out.
        '''
        assert(self.soup.find(class_='barTitle').string.strip() == 'Upcoming anime')
        titles = self.soup.find(class_='barContent').find_all(class_='title')
        links = []
        for title in titles:
            name = title.string
            link = title.parent
            link.string = name
            links.append(link)
        return links

    def __strip_by_re(self, string, filter, end, start=0):
        return string[start:end] if re.search(filter, string) != None else string

    def __clean_name(self, name):
        cleaned_name = name.replace(' (Sub)', '').replace(' (Dub)', '').replace (' (OVA)', '').replace (' Specials ', '')
        cleaned_name = self.__strip_by_re(cleaned_name, '( \(1080p\))$', end=-8)
        cleaned_name = self.__strip_by_re(cleaned_name, '( \((720|480|360)p\))$', end=-8)
        #cleaned_name = cleaned_name[:-8] if re.search('( \(1080p\))$', cleaned_name) != None else cleaned_name
        #cleaned_name = cleaned_name[:-8] if re.search('( \((720|480|360)p\))$', cleaned_name) != None else cleaned_name
        return cleaned_name

    def __clean_tv_show_name(self, name):
        cleaned_name = name.replace(' (TV)', '').replace(' Second Season', '').replace(' 2nd Season', '')
        cleaned_name = self.__strip_by_re(cleaned_name, '( Season [0-9])$', end=-9)
        cleaned_name = self.__strip_by_re(cleaned_name, '( S[0-9])$', end=-3)
        cleaned_name = self.__strip_by_re(cleaned_name, '( II)$', end=-3)
        cleaned_name = self.__strip_by_re(cleaned_name, '( [0-9])$', end=-2)
        #cleaned_name = cleaned_name[:-9] if re.search('( Season [0-9])$', cleaned_name) != None else cleaned_name
        #cleaned_name = cleaned_name[:-3] if re.search('( S[0-9])$', cleaned_name) != None else cleaned_name
        #cleaned_name = cleaned_name[:-2] if re.search('( [0-9])$', cleaned_name) != None else cleaned_name
        #cleaned_name = cleaned_name[:-2] if re.search('( II)$', cleaned_name) != None else cleaned_name
        return cleaned_name