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
from resources.lib.common import args, constants, threadpool
from resources.lib.common.helpers import helper
from resources.lib.metadata.loose_metahandlers import meta
from resources.lib.list_types.web_list import WebList
from bs4 import BeautifulSoup



# DEBUG
import time



class MediaContainerList(WebList):
    def __init__(self, url_val=args.value, form_data=None):
        t0 = time.time()
        WebList.__init__(self, url_val, form_data)
        self.has_next_page = False
        t1 = time.time()
        helper.log_notice('TIMER - MEDIACONTAINERLIST.INIT: %f' % (t1 - t0))

    ''' PUBLIC FUNCTIONS '''
    def parse(self):
        helper.start('MediaContainerList.parse')
        if self.soup == None:
            return

        t0 = time.time()
        table = self.soup.find('table', class_='listing')
        if table == None:
            self.links = self.__parse_upcoming()
            t1 = time.time()
            helper.log_notice('TIMER - MEDIACONTAINERLIST.PARSE: %f' % (t1 - t0))
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
        t1 = time.time()
        helper.log_notice('TIMER - MEDIACONTAINERLIST.PARSE: %f' % (t1 - t0))

    def worker(self, tuple):
        (name, url, idx) = tuple
        metadata, media_type = self._get_metadata(name)
        self.links_with_metadata[idx] = (name, url, metadata, media_type)

    # If title_prefix is not None, then assume we are being included inline 
    # and let the caller handle setting the content type and ending the directory
    def add_items(self, title_prefix=None):
        t0 = time.time()
        end_dir = title_prefix == None
        title_prefix = title_prefix if title_prefix else ''
        if not end_dir:
            helper.set_content('tvshows')
        iter_links = self.links[:-2] if self.has_next_page else self.links

        # Filter out the episode links for ongoing series
        t1 = time.time()
        mc_links = []
        idx = 0
        for link in iter_links:
            url = link['href']
            if re.search('(\?id=)', url) != None:
                continue
            mc_links.append((link.string.strip(), url, idx))
            idx += 1
        t2 = time.time()
        helper.log_notice('TIMER - MEDIACONTAINERLIST.ADD_ITEMS - initial loop: %f' % (t2 - t1))

        self.links_with_metadata = [None] * idx
        pool = threadpool.ThreadPool(4)
        pool.map(self.worker, mc_links)
        pool.wait_completion()

        for (name, url, metadata, media_type) in self.links_with_metadata:
            icon, fanart = self._get_art_from_metadata(metadata)
            if media_type == 'tvshow' and (' (OVA)' in name or ' Specials' in name or
                                           re.search('( OVA)( \(((Sub)|(Dub))\))?$', name) != None or 
                                           re.search(' (Special)$', name) != None):
                media_type = 'special'
            query = self._construct_query(url, 'mediaList', metadata, name, media_type)

            contextmenu_items = [('Show Information', 'XBMC.Action(Info)')]
            find_metadata_query = self._construct_query(url, 'findmetadata', metadata, name)
            find_metadata_context_item = constants.find_metadata_action % helper.build_plugin_url(find_metadata_query)
            if meta.is_metadata_empty(metadata, media_type):
                contextmenu_items.append(('Find metadata', find_metadata_context_item))
            else:
                contextmenu_items.append(('Fix metadata', find_metadata_context_item))
            
            metadata['title'] = title_prefix + name # needed for sub and dub
            helper.add_directory(query, metadata, img=icon, fanart=fanart, contextmenu_items=contextmenu_items, total_items=len(mc_links))

        if self.has_next_page:
            query = self._construct_query(self.links[-2]['href'], 'mediaContainerList')
            helper.add_directory(query, {'title':'Next'})
            query = self._construct_query(self.links[-1]['href'], 'mediaContainerList')
            helper.add_directory(query, {'title':'Last'})

        if end_dir:
            helper.end_of_directory()
        t_end = time.time()
        helper.log_notice('TIMER - MEDIACONTAINERLIST.ADD_ITEMS: %f' % (t_end - t0))


    ''' OVERRIDDEN PROTECTED FUNCTIONS '''
    def _get_metadata(self, name):
        helper.start('MediaContainerList._get_metadata - name: %s' % name)
        if helper.get_setting('enable-metadata') == 'false' or name == 'Next' or name == 'Last':
            return {}, ''

        t0 = time.time()

        name_for_movie_search = self._clean_name(name)
        name_for_tv_search = self.__clean_tv_show_name(name_for_movie_search)
        media_type = 'tvshow'

        # Not sure if movie or tv show; try tv show first
        metadata = meta.get_meta('tvshow', name_for_tv_search)#, year=year)
        helper.log_debug('Got metadata %s for show %s' % (metadata, name_for_tv_search))
        t1 = time.time()
        t2, t3, t4 = t1, t1, t1
        # It may be a movie, so let's try that with the general cleaned name
        if metadata['tvdb_id'] == '':
            metadata = meta.get_meta('movie', name_for_movie_search)#, year=year)
            t2 = time.time()
            # If movie failed, and if there was a year in the name, try tv without it
            if metadata['tmdb_id'] == '' and re.search('( \([12][0-9]{3}\))$', name_for_tv_search) != None:
                metadata = meta.get_meta('tvshow', name_for_tv_search[:-7], update=True)
                t3 = time.time()
                if metadata['imdb_id'] != '':
                    metadata = meta.update_meta('tvshow', name_for_tv_search, imdb_id='', new_imdb_id=metadata['imdb_id'])
                    t4 = time.time()
            elif metadata['tmdb_id'] != '': # otherwise we found a move
                media_type = 'movie'

        helper.end('MediaContainerList._get_metadata')

        t_end = time.time()
        helper.log_notice('TIMER - MEDIACONTAINERLIST._GET_METADTA - TOTAL:%f, TV:%f, MOVIE:%f, YEAR:%f, UPDATE:%f' %
                          (t_end-t0, t1-t0, t2-t1, t3-t2, t4-t3))

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

    def __clean_tv_show_name(self, name):
        cleaned_name = name.replace(' (TV)', '').replace(' Second Season', '').replace(' 2nd Season', '')
        cleaned_name = self._strip_by_re(cleaned_name, '( Season [0-9])$', end=-9)
        cleaned_name = self._strip_by_re(cleaned_name, '( S[0-9])$', end=-3)
        cleaned_name = self._strip_by_re(cleaned_name, '( II)$', end=-3)
        cleaned_name = self._strip_by_re(cleaned_name, '( [0-9])$', end=-2)
        return cleaned_name
