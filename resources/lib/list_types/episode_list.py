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
from datetime import datetime
from resources.lib.common import args
from resources.lib.common.helpers import helper
from resources.lib.list_types.web_list import WebList
from resources.lib.list_types import media_container_list
from bs4 import BeautifulSoup


class EpisodeList(WebList):
    def __init__(self):
        WebList.__init__(self)
        self.genres = []
        self.aliases = []
        self.related_links = []
        self.first_air_date = ''
        self.season = None
        self.num_episodes = 0

    ''' PUBLIC FUNCTIONS '''
    def parse(self):
        helper.start('EpisodeList.parse')
        if self.soup == None:
            return

        self.links = self.soup.find('table', class_='listing').find_all('a')
        spans = self.soup.find_all('span', class_='info')
        helper.log_debug('# of links found: %d' % len(self.links))

        # We can determine if the media is a movie or not examining the genres
        span = [s for s in spans if s.string == 'Genres:']
        if span != []:
            genre_links = span[0].parent.find_all('a')
            self.genres = [link.string for link in genre_links]
            helper.log_debug('Found the genres: %s' % str(self.genres))

        # We'll try to determine the episode list from the first date
        span = [s for s in spans if s.string == 'Date aired:']
        if span != []:
            air_date = span[0].next_sibling.encode('ascii', 'ignore').strip().split(' to ')[0]
            air_datetime = helper.get_datetime(air_date, '%b %d, %Y')
            self.first_air_date = air_datetime.strftime('%Y-%m-%d')
            helper.log_debug('Found the first air date: %s' % str(self.first_air_date))

        # We'll try to determine the season from the alternate names, if necessary
        span = [s for s in spans if s.string == 'Other name:']
        if span != []:
            alias_links = span[0].parent.find_all('a')
            # Only keep aliases that do not contain CJK (eg, Japanese) characters
            f = lambda c: ord(c) > 0x3000
            self.aliases = [link.string for link in alias_links if filter(f, link.string) == u'']
            helper.log_debug('Found the aliases: %s' % str(self.aliases))

        rightboxes = self.soup.find('div', id='rightside').find_all('div', class_='rightBox')
        if len(rightboxes) > 1:
            related = rightboxes[1].find('div', class_='barContent').find_all('a')
            for link in related:
                self.related_links.append(link)
                has_class = dict(link.next_sibling.next_sibling.attrs).has_key('class')
                if has_class and link.next_sibling.next_sibling['class'][0] == u'line':
                    break

        # Grab bookmark ID
        if 'animeID=' in self.html:
            self.bookmark_id = self.html.split('animeID=')[1].split('"')[0]
        else:
            self.bookmark_id = None

        # Sort episodes in ascending order by default
        self.links.reverse()

        helper.end('EpisodeList.parse')
        return
    
    def get_actual_media_type(self):
        # 1.1) The metadata classification may have failed earlier before because
        # of lack of data.  We can fix any potential mismatches here.
        if 'Movie' in self.genres:
            helper.log_debug('|COUNT|MISMATCH| %s' % args.full_mc_name)
            return 'movie'

        # 1.2) We have a special, let's handle just use the season 0 data along with the show banner
        if ('(OVA)' in args.full_mc_name or ' Specials' in args.full_mc_name or
            re.search('( OVA)( \(((Sub)|(Dub))\))?$', args.full_mc_name) != None or
            re.search(' (Special)$', args.full_mc_name) != None):
            helper.log_debug('|COUNT|OVA| %s' % args.full_mc_name)
            return 'special'

        return 'tvshow'

    def add_items(self):
        helper.start('EpisodeList.add_items')
        if self.links == []:
            return

        # We now have a list of episodes in links, and we need to figure out
        # which season those episodes belong to, as well as filter out stray
        # specials/OVAs.  I have a numbered FSM for this.  The caller should
        # invoke get_actual_media_type before this function to get the first state.
        
        # 2) Otherwise, we have a tv show.  The most reliable way to figure out 
        # what data to use is to use the first air date with the number of 
        # episodes.
        self.season = None
        if self.first_air_date == '':
            # 3) If we don't have the air date, we will try out best to 
            # determine which season this is based on the data we scraped
            self.season = self.__determine_season()
            if self.season == None:
                # I'm not sure what the next best step is here, but I have to
                # assume it's the first season to catch a lot of actual first 
                # seasons...
                helper.log_debug('|COUNT|LEFTOVER| %s' % args.full_mc_name)
        else:
            helper.log_debug('|COUNT|AIR| %s' % args.full_mc_name)

        specials = []
        episodes = []
        double_eps = 0
        for link in self.links:
            name = link.string.strip()
            url = link['href']
            name_minus_show = name.replace(args.full_mc_name, '')
            if re.search('( .?Special ([0-9]?){0,2}[0-9])$', name) != None:
                specials.append((name, url))
            elif 'recap' in name_minus_show.lower() or '.5' in name_minus_show:
                specials.append((name, url))
            elif re.search('( Episode [0-9]{1,3}-[0-9]{0,3})$', name) != None:
                double_eps += 1
                episodes.append((name, url))
            else:
                episodes.append((name, url))

        self.num_episodes = len(episodes) + double_eps
        helper.log_debug('We have %d episodes' % self.num_episodes)
        action, is_folder = self._get_action_and_isfolder()
        helper.set_content('episodes')

        all_metadata = self._get_metadata(args.base_mc_name)
        helper.log_debug('We have %d metadata entries' % len(all_metadata))
        offset = 0
        for idx, (name, url) in enumerate(episodes):
            metadata = all_metadata[idx+offset] if len(all_metadata) > 0 else {'title':name}
            icon, fanart = self._get_art_from_metadata(metadata)
            query = self._construct_query(url, action, metadata)
            contextmenu_items = [('Show Information', 'XBMC.Action(Info)')]
            if re.search('( Episode [0-9]{1,3}-[0-9]{0,3})$', name) != None:
                metadata['title'] = '%d & %d - %s' % ((idx+offset+1), (idx+offset+2), metadata['title'])
                offset += 1
            else:
                metadata['title'] = '%d - %s' % ((idx+offset+1), metadata['title'])
            helper.add_directory(query, metadata, img=icon, fanart=fanart, is_folder=is_folder, contextmenu_items=contextmenu_items)

        if len(specials) > 0:
            icon, fanart = self._get_art_for_season0()
            for (name, url) in specials:
                metadata = {'title':name}
                query = self._construct_query(url, action, metadata)
                helper.add_directory(query, metadata, img=icon, fanart=fanart, is_folder=is_folder)

        # Add related links using the MCL (since they're all media containers)
        mclist = media_container_list.MediaContainerList(None)
        mclist.links = self.related_links
        mclist.add_items(title_prefix='Related: ')

        if self.bookmark_id != None:
            query = self._construct_query(self.bookmark_id, 'toggleBookmark')
            helper.add_directory(query, {'title':'Toggle bookmark'})

        helper.add_sort_methods(['title'])
        helper.end_of_directory()
        helper.end('EpisodeList.add_items')
        return

    ''' OVERRIDDEN PROTECTED FUNCTIONS '''
    def _get_metadata(self, name):
        if (helper.get_setting('enable-metadata') == 'false' or 
            (args.imdb_id == None and args.tvdb_id == None)):
            return []
        
        all_metadata = self.meta.get_episodes_meta(name, args.imdb_id, args.tvdb_id, self.num_episodes,
                                              self.first_air_date, self.season)

        return all_metadata

    ''' PROTECTED FUNCTIONS '''
    def _get_art_for_season0(self):
        helper.start('_get_art_for_season0 for name %s and imdb_id %s' % (args.base_mc_name, args.imdb_id))
        if helper.get_setting('enable-metadata') == 'false':
            return None, ''

        season_covers = self.meta.get_seasons(args.base_mc_name, args.imdb_id, ['0'])
        if len(season_covers) > 0:
            icon = season_covers[0]['cover_url']
            fanart = season_covers[0]['backdrop_url']
        else:
            icon = args.icon
            fanart = args.fanart
        return icon, fanart

    def _get_action_and_isfolder(self):
        select_quality = helper.get_setting('preset-quality') == 'Individually select'
        action = 'quality' if select_quality else 'autoplay'
        is_folder = select_quality # Display a folder if we have to select the quality
        return action, is_folder

    ''' PRIVATE FUNCTIONS '''
    def __determine_season(self):
        # 3.1) The next best thing is to examine the full name vs the base 
        # name and look for any season stuff
        clean_mc_name = self._clean_name(args.full_mc_name)
        leftovers = clean_mc_name.replace(args.base_mc_name, '')
        season = self.__extract_season(leftovers)
        if season != None:
            helper.log_debug('|COUNT|BASE| %s' % args.full_mc_name)
            # We have a season, let's extract it and work from there
            return season

        # 3.2) The next best thing after that is to examine the alternate 
        # names and look for any season stuff
        for alias in self.aliases:
            season = self.__extract_season(alias)
            if season != None:
                helper.log_debug('|COUNT|ALIAS| %s' % args.full_mc_name)
                return season

        return None

    def __extract_season(self, name):
        season = None
        name = name.replace(' (TV)', '')
        if ' Second Season' in name or ' 2nd Season' in name:
            season = str(2)
        elif re.search('( Season [0-9])$', name) != None:
            season = name[-1]
        elif re.search('( S[0-9])$', name) != None:
            season = name[-1]
        elif re.search('( II)$', name) != None:
            season = str(2)
        elif re.search('( [0-9])$', name):
            season = name[-1]
        return season
