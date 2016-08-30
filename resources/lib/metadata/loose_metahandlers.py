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


'''
    Ugh.  The following 3 lines are a result of me being extra lazy.  What I am
    doing here is called "monkey-patching" an entire class in another module
    (!!).

    http://stackoverflow.com/questions/3765222/monkey-patch-python-class

    At the end of the day, the TMDB class had comparisons that screwed over 
    anime titles (eg, preferring the first result over Japanese results, and 
    there is no way to filter based on original language).  These included 
    __clean_name and tmdb_lookup.

    My options, as I understood the problem, were the following:
    - I tried replacing the class in this file (ie, TMDB = AnimeTMDB), but that
      would only replace the local occurences of TMDB(), not the ones in 
      metahandler, just like the first option.
    - Define the functions in their entirety at the top level and patch them in
      at the class level, eg TMDB.tmdb_lookup = my_tmdb_lookup.  The downside
      to this approach is that I had to copy the entire freaking function.
      However, this would only replace the local occurences of TMDB.  To get
      everything, I would need to override all functions that create instances
      of TMDB and replace those instances with AnimeTMDB instances.
    - Modify the metahandler module code directly.  I didn't want to do this
      for obvious reasons.
    - Monkey-patch the class within the metahandler object itself. Although
      nasty, the replacement class AnimeTMDB could inherit from TMDB, so it
      could use any of the parent's methods, resulting in potentially a lot 
      less code.

    I ended up choosing the 4th option.
'''
import metahandler
from resources.lib.metadata.anime_TMDB import AnimeTMDB
metahandler.TMDB.TMDB = AnimeTMDB


import os, threading
from datetime import datetime, timedelta
from metahandler.metahandlers import *
from metahandler.thetvdbapi import TheTVDB
from metahandler import common
from resources.lib.common.helpers import helper


def init():
    meta = LooseMetaData()
    return meta


class LooseMetaData(MetaData):
    def __init__(self, prepack_images=False, preparezip=False, tmdb_api_key='af95ef8a4fe1e697f86b8c194f2e5e11'):
        '''
        A copy of __init__ from the metahandler plugin, modified to use a 
        different db path, which unfortunately required pasting this function 
        and modifying it :/
        '''
        # TMDB constants
        self.tmdb_image_url = ''
        try:
            from resources.lib.common import api
            self.tmdb_api_key = api.tmdb_key
        except:
            self.tmdb_api_key = tmdb_api_key
            pass

        self.path = helper.get_profile()
        self.cache_path = make_dir(self.path, 'meta_cache')

        if prepack_images:
            #create container working directory
            #!!!!!Must be matched to workdir in metacontainers.py create_container()
            self.work_path = make_dir(self.path, 'work')
            
        #set movie/tvshow constants
        self.type_movie = 'movie'
        self.type_tvshow = 'tvshow'
        self.type_season = 'season'        
        self.type_episode = 'episode'
            
        #this init auto-constructs necessary folder hierarchies.

        # control whether class is being used to prepare pre-packaged .zip
        self.prepack_images = bool2string(prepack_images)
        self.videocache = os.path.join(self.cache_path, 'video_cache.db')
        self.tvpath = make_dir(self.cache_path, self.type_tvshow)
        self.tvcovers = make_dir(self.tvpath, 'covers')
        self.tvbackdrops = make_dir(self.tvpath, 'backdrops')
        self.tvbanners = make_dir(self.tvpath, 'banners')
        self.mvpath = make_dir(self.cache_path, self.type_movie)
        self.mvcovers = make_dir(self.mvpath, 'covers')
        self.mvbackdrops = make_dir(self.mvpath, 'backdrops')

        # connect to db at class init and use it globally
        if DB == 'mysql':
            class MySQLCursorDict(database.cursor.MySQLCursor):
                def _row_to_python(self, rowdata, desc=None):
                    row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
                    if row:
                        return dict(zip(self.column_names, row))
                    return None
            db_address = common.addon.get_setting('db_address')
            db_port = common.addon.get_setting('db_port')
            if db_port: db_address = '%s:%s' %(db_address,db_port)
            db_user = common.addon.get_setting('db_user')
            db_pass = common.addon.get_setting('db_pass')
            db_name = common.addon.get_setting('db_name')
            self.dbcon = database.connect(database=db_name, user=db_user, password=db_pass, host=db_address, buffered=True)
            self.dbcur = self.dbcon.cursor(cursor_class=MySQLCursorDict, buffered=True)
        else:
            self.dbcon = database.connect(self.videocache, isolation_level=None, check_same_thread=False)
            self.dbcon.row_factory = database.Row # return results indexed by field names and not numbers so we can convert to dict
            self.dbcur = self.dbcon.cursor()

        # initialize cache db
        self._cache_create_movie_db()
        
        # Check TMDB configuration, update if necessary
        self._set_tmdb_config()

        # Add the absolute_number column here, which is helpful for animes
        if not self._does_column_exist('absolute_episode', 'episode_meta'):
            sql_alter = "ALTER TABLE episode_meta ADD absolute_episode INTEGER"
            try:
                self.dbcur.execute(sql_alter)
                helper.log_debug('Successfully added the absolute_episode column')
            except:
                helper.log_debug('Failed to alter the table')
        else:
            helper.log_debug('The absolute_episode column already exists')

        common.addon.log = helper.log
        self.lock = threading.Lock()
    
    def is_metadata_empty(self, metadata, media_type):
        if not metadata:
            return True
        if media_type == 'tvshow' or media_type == 'special':
            return (not metadata.get('tvdb_id', '') and not metadata.get('imdb_id', ''))
        if media_type == 'movie':
            return (not metadata.get('tmdb_id', '') and not metadata.get('imdb_id', ''))
        return True

    def get_episodes_meta(self, tvshowtitle, imdb_id, tvdb_id, num_episodes, first_air_date='', season=None):
        '''
        Returns all metadata about the given number of episodes (inclusive) for
        the given show, starting at the given first air date.

        At least one of tvdb_id and imdb_id must be given.
        '''
        helper.start('get_episodes_meta')
        if not imdb_id and not tvdb_id:
            helper.log_debug('Invalid imdb_id and tvdb_id')
            return []

        imdb_id = self._valid_imdb_id(imdb_id) if imdb_id else ''

        if not tvdb_id:
            tvdb_id = self._get_tvdb_id(tvshowtitle, imdb_id)

        # Look up in cache first
        meta_list = self._cache_lookup_episodes(imdb_id, tvdb_id, first_air_date, season, num_episodes)

        if not meta_list:
            if tvdb_id:
                # if not cached, grab all of the raw data using get_show_and_episodes()
                helper.log_debug('Grabbing show and episodes for metadata')
                tvdb = TheTVDB(language=self._MetaData__get_tvdb_language())
                (show, episode_list) = tvdb.get_show_and_episodes(tvdb_id)
                meta_list, curr_abs_num = [], 0
                for ep in episode_list:
                    m = self._episode_to_meta(ep, tvshowtitle, show)
                    # Fix the absolute episode number if it doesn't exist at any point
                    # I assume the list is sorted by season/episode
                    if m['season'] != 0:
                        if m['absolute_episode'] != -1:
                            curr_abs_num = m['absolute_episode']
                        else:
                            curr_abs_num += 1
                            m['absolute_episode'] = curr_abs_num
                    meta_list.append(m)
                         
                #meta_list = [self._episode_to_meta(ep, tvshowtitle, show) for ep in episode_list]
            else:
                helper.log_debug('No TVDB ID available, could not find TV show with imdb: %s' % imdb_id)
                tvdb_id = ''

            if not meta_list:
                meta_list = [self._MetaData__init_episode_meta(imdb_id, tvdb_id, '', 0, 0, first_air_date)]
                meta_list[0]['playcount'] = 0
                meta_list[0]['TVShowTitle'] = tvshowtitle

            self._cache_save_episodes_meta(meta_list)

            # Filter out those that start before first_air_date/season (and 
            # have no absolute number) and those that come after plus 
            # num_episdoes
            if first_air_date != '':
                meta_list = self.__filter_meta_list_by_airdate(meta_list, first_air_date, num_episodes)
            elif season != None:
                meta_list = self.__filter_meta_list_by_season(meta_list, season, num_episodes)
            else:
                meta_list = [m for m in meta_list if m['absolute_episode'] != -1]

        helper.end('get_episodes_meta')
        return meta_list

    def update_meta_to_nothing(self, media_type, title):
        meta = self._cache_lookup_by_name(media_type, title)
        if meta:
            self._cache_delete_video_meta(media_type, '', '', title, '')

        init_fn = self._init_tvshow_meta if media_type == 'tvshow' else self._init_movie_meta
        meta = init_fn('', '', title)

        self._cache_save_video_meta(meta, title, media_type)

    def _does_column_exist(self, column_name, table):
        sql_pragma = 'PRAGMA table_info(episode_meta)'
        try:
            self.dbcur.execute(sql_pragma)
            matched_rows = self.dbcur.fetchall()
        except:
            common.addon.log_debug('Unable to execute sql for column existance query')
            return True
        return ([r for r in matched_rows if r['name'] == 'absolute_episode'] != [])

    def _MetaData__init_episode_meta(self, imdb_id, tvdb_id, episode_title, season, episode, air_date):
        meta = MetaData._MetaData__init_episode_meta(self, imdb_id, tvdb_id, episode_title, season, episode, air_date)
        meta['absolute_episode'] = 0
        return meta
    
    def _cache_lookup_episodes(self, imdb_id, tvdb_id, first_air_date, season, num_episodes):
        '''
        Lookup metadata for multiple episodes starting from the first air date
        for the given number of episodes.
        '''
        helper.start('LooseMetadata._cache_lookup_episodes')
        row = self.__cache_find_absolute_episode(tvdb_id, first_air_date, season)

        # Account for TVDB's off-by-1 error for first_air_date
        if row == None:
            if first_air_date == '':
                return []
            first_date = helper.get_datetime(first_air_date, '%Y-%m-%d')
            try1 = (first_date - timedelta(days=1)).strftime('%Y-%m-%d')
            try2 = (first_date + timedelta(days=1)).strftime('%Y-%m-%d')
            row = self.__cache_find_absolute_episode(tvdb_id, try1, season)
            row2 = self.__cache_find_absolute_episode(tvdb_id, try2, season)
            if row == None and row2 == None:
                return []
            elif row2 != None:
                row = row2

        first_ep = row['absolute_episode']
        last_ep = first_ep + (num_episodes - 1) # inclusive

        sql_select = ('SELECT '
                      'episode_meta.title as title, '
                      'episode_meta.plot as plot, '
                      'episode_meta.director as director, '
                      'episode_meta.writer as writer, '
                      'tvshow_meta.genre as genre, '
                      'tvshow_meta.duration as duration, '
                      'episode_meta.premiered as premiered, '
                      'tvshow_meta.studio as studio, '
                      'tvshow_meta.mpaa as mpaa, '
                      'tvshow_meta.title as TVShowTitle, '
                      'episode_meta.imdb_id as imdb_id, '
                      'episode_meta.rating as rating, '
                      '"" as trailer_url, '
                      'episode_meta.season as season, '
                      'episode_meta.episode as episode, '
                      'episode_meta.overlay as overlay, '
                      'tvshow_meta.backdrop_url as backdrop_url, '                               
                      'episode_meta.poster as cover_url ' 
                      'FROM episode_meta, tvshow_meta '
                      'WHERE episode_meta.tvdb_id = tvshow_meta.tvdb_id AND '
                      'episode_meta.tvdb_id = ? AND episode_meta.absolute_episode BETWEEN ? and ? '
                      'ORDER BY episode_meta.absolute_episode ASC '
                      'GROUP BY TVShowTitle')
        helper.log_debug('SQL select: %s with params %s' % (sql_select, (tvdb_id, first_ep, last_ep)))
        try:
            self.dbcur.execute(sql_select, (tvdb_id, first_ep, last_ep))
            matchedrows = self.dbcur.fetchall()
        except Exception, e:
            helper.log_debug('************* Error attempting to select from Episode table: %s ' % e)
            return []

        if matchedrows == None:
            return []

        # Because 2 shows in the tvshow meta can have the same tvdb ID (eg, 
        # Fairy Tail and Fairy Tail (2014)), we need to filter out duplicates.
        if len(matchedrows) / num_episodes > 1:
            matchedrows = matchedrows[:num_episodes]

        meta_list = []
        for row in matchedrows:
            meta_list.append(dict(row))
        
        helper.end('LooseMetadata._cache_lookup_episodes success')
        return meta_list

    def _cache_save_episodes_meta(self, meta_list):
        '''
        Save metadata of multiple episodes to local cache db.
        '''
        if meta_list[0]['imdb_id']:
            sql_select = 'SELECT * from episode_meta WHERE imdb_id = "%s"' % meta_list[0]['imdb_id']
            sql_delete = 'DELETE * from episode_meta WHERE imdb_id = "%s"' % meta_list[0]['imdb_id']
        elif meta_list[0]['tvdb_id']:
            sql_select = 'SELECT * from episode_meta WHERE tvdb_id = "%s"' % meta_list[0]['tvdb_id']
            sql_delete = 'DELETE * from episode_meta WHERE tvdb_id = "%s"' % meta_list[0]['tvdb_id']
        else:
            sql_select = 'SELECT * from episode_meta WHERE title = "%s"' % self._clean_string(meta_list[0]['title'].tolower())
            sql_delete = 'DELETE * from episode_meta WHERE title = "%s"' % self._clean_string(meta_list[0]['title'].tolower())
        helper.log_debug('SQL Select: %s' % sql_select)

        try:
            self.dbcur.execute(sql_select)
            matchedrow = self.dbcur.fetchone()
            if matchedrow:
                helper.log_debug('SQL Delete: %s' % sql_delete)
                self.dbcur.execute(sql_delete)
        except Exception as e:
            helper.log_debug('************* Error attempting to delete episodes from cache table: %s ' % e)
            pass

        helper.log_debug('Saving metadata information for the episodes')
        try:
            sql_insert = MetaData._MetaData__insert_from_dict(self, 'episode_meta', 14)
            m_list = []
            for m in meta_list:
                m_list.append((m['imdb_id'], m['tvdb_id'], m['episode_id'], m['season'],
                               m['episode'], m['title'], m['director'], m['writer'], m['plot'],
                               m['rating'], m['premiered'], m['poster'], m['overlay'], m['absolute_episode']))
            helper.log_debug('SQL INSERT: %s' % sql_insert)
            self.dbcur.executemany(sql_insert, m_list)
            self.dbcon.commit()
        except Exception, e:
            helper.log_debug('************* Error attempting to insert into episodes cache table: %s ' % e)
            pass 

        return

    def _get_tvdb_meta(self, imdb_id, name, year=''):
        '''
        Requests meta data from TVDB and creates proper dict to send back.
        This version is a bit looser in determining if we can use the given 
        results, and also checks against aliases.
        
        Args:
            imdb_id (str): IMDB ID
            name (str): full name of movie you are searching
        Kwargs:
            year (str): 4 digit year of movie, when imdb_id is not available it is recommended
                        to include the year whenever possible to maximize correct search results.
                        
        Returns:
            DICT. It must also return an empty dict when
            no movie meta info was found from tvdb because we should cache
            these "None found" entries otherwise we hit tvdb alot.
        '''      
        common.addon.log('Starting TVDB Lookup', 0)
        helper.start('_get_tvdb_meta')
        tvdb = TheTVDB(language=self._MetaData__get_tvdb_language())
        tvdb_id = ''
                
        try:
            if imdb_id:
                tvdb_id = tvdb.get_show_by_imdb(imdb_id)
                helper.log_debug('Attempt to get show from imdb_id %s gave us tvdb_id %s.' % (imdb_id, tvdb_id))
        except Exception, e:
            common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
            tvdb_id = ''
            pass
            
        # Intialize tvshow meta dictionary
        meta = self._init_tvshow_meta(imdb_id, tvdb_id, name, year)

        # If not found by imdb, try by name
        if tvdb_id == '':
            try:
                # If year is passed in, add it to the name for better TVDB search results
                if year:
                    name = name + ' ' + year
                show_list = tvdb.get_matching_shows(name, want_raw=True)
            except Exception, e:
                common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
                show_list = []
                pass
            tvdb_id = ''
            prob_id = ''

            helper.log_debug('Raw results of tv show candidates: %s' % str(show_list))
            strcmp = self._string_compare
            clean = self._clean_string
            for show in show_list:
                # This is probably our result (or if the list length is 1!)
                tmp_imdb_id = show.get('IMDB_ID', None)
                if tmp_imdb_id == imdb_id or strcmp(clean(show['SeriesName']), clean(name)) or len(show_list) == 1:
                    tvdb_id = clean(show['seriesid'])
                    if not imdb_id:
                        imdb_id = clean(tmp_imdb_id)
                    break
                # Check aliases
                if show.has_key('AliasNames'):
                    helper.log_debug('Looking at the aliases: %s' % str(show['AliasNames'].encode('ascii', 'xmlcharrefreplace').split('|')))
                    for alias in show['AliasNames'].split('|'):
                        if strcmp(clean(alias), clean(name)):
                            prob_id = clean(show['seriesid'])
                            if not imdb_id:
                                imdb_id = clean(tmp_imdb_id)
            if tvdb_id == '' and prob_id != '':
                tvdb_id = self._clean_string(prob_id)


        # If we still haven't found anything, let's try IMDB to see if we can find a show
        if tvdb_id == '' and imdb_id == '':
            tmdb = TMDB(api_key=self.tmdb_api_key, lang=self._MetaData__get_tmdb_language())
            imdb_meta = tmdb.search_imdb(name)
            helper.log_debug('Found IMDB result with metadata %s' % str(imdb_meta))
            helper.log_debug('imdbID: %s | %s|' % (imdb_meta.get('imdbID', ''), str('tt' in imdb_meta.get('imdbID', ''))))
            if imdb_meta and 'tt' in imdb_meta.get('imdbID', ''):
                media_type = imdb_meta.get('Type', '')
                if media_type == 'series':
                    imdb_id = imdb_meta.get('imdbID')
                elif media_type == 'episode' and imdb_meta.get('seriesID', '') != '':
                    imdb_id = imdb_meta.get('seriesID')
            if imdb_id != '':
                helper.log_debug('Found metadata from IMDB with id %s! Restarting _get_tvdb_meta' % imdb_id)
                return self._get_tvdb_meta(imdb_id, name, year)

        if tvdb_id:
            common.addon.log('Show *** ' + name + ' *** found in TVdb. Getting details...', 0)

            try:
                show = tvdb.get_show(tvdb_id)
            except Exception, e:
                common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
                show = None
                pass
            
            if show is not None:
                helper.log_debug('Got a show from tvdb_id %s' % str(show))
                meta = self._show_to_meta(show, imdb_id, tvdb_id, name, year)
                if meta['plot'] == 'None' or meta['plot'] == '' or meta['plot'] == 'TBD' or meta['plot'] == 'No overview found.' or meta['rating'] == 0 or meta['duration'] == 0 or meta['cover_url'] == '':
                    common.addon.log(' Some info missing in TVdb for TVshow *** '+ name + ' ***. Will search imdb for more', 0)
                    tmdb = TMDB(api_key=self.tmdb_api_key, lang=self._MetaData__get_tmdb_language())
                    imdb_meta = tmdb.search_imdb(name, imdb_id)
                    if imdb_meta:
                        imdb_meta = tmdb.update_imdb_meta(meta, imdb_meta)
                        if imdb_meta.has_key('overview'):
                            meta['plot'] = imdb_meta['overview']
                        if imdb_meta.has_key('rating'):
                            meta['rating'] = float(imdb_meta['rating'])
                        if imdb_meta.has_key('runtime'):
                            meta['duration'] = int(imdb_meta['runtime']) * 60
                        if imdb_meta.has_key('cast'):
                            meta['cast'] = imdb_meta['cast']
                        if imdb_meta.has_key('cover_url'):
                            meta['cover_url'] = imdb_meta['cover_url']

                return meta
            else:
                tmdb = TMDB(api_key=self.tmdb_api_key, lang=self._MetaData__get_tmdb_language())
                imdb_meta = tmdb.search_imdb(name, imdb_id)
                if imdb_meta:
                    meta = tmdb.update_imdb_meta(meta, imdb_meta)
                return meta    
        else:
            return meta

    def _get_tvshow_backdrops(self, imdb_id, tvdb_id):
        # Some of us aren't so lucky as to have both an imdb_id and a tvdb_id
        if not imdb_id and not tvdb_id:
            helper.log_debug('Cannot get tv show backdrop with neither type of id supplied')
            return ''

        sql_select = "SELECT backdrop_url FROM tvshow_meta WHERE %s=?" % ('imdb_id' if imdb_id else 'tvdb_id')
        id = imdb_id if imdb_id else str(tvdb_id)

        common.addon.log('SQL Select: %s params: %s' % (sql_select, id), 0)
        try:
            self.dbcur.execute(sql_select, (id,))
            matchedrow = self.dbcur.fetchone()
        except Exception as e:
            common.addon.log('************* Error attempting to select from tvshow_meta table: %s ' % e, 4)
            pass
            return ''
                    
        if matchedrow:
            return dict(matchedrow)['backdrop_url']
        else:
            return ''

    def _show_to_meta(self, show, imdb_id, tvdb_id, show_name, year):
        meta = self._init_tvshow_meta(imdb_id, tvdb_id, show_name, year)
        meta['imdb_id'] = imdb_id if imdb_id != None else ''
        meta['tvdb_id'] = tvdb_id
        meta['title'] = show_name
        if str(show.rating) != '' and show.rating != None:
            meta['rating'] = float(show.rating)
        meta['duration'] = int(show.runtime) * 60 if show.runtime else 0
        meta['plot'] = show.overview
        meta['mpaa'] = show.content_rating
        meta['premiered'] = str(show.first_aired)

        #Do whatever we can to set a year, if we don't have one lets try to strip it from show.first_aired/premiered
        if not year and show.first_aired:
            meta['year'] = int(meta['premiered'][:4])

        if show.genre != '':
            temp = show.genre.replace("|",",")
            temp = temp[1:(len(temp)-1)]
            meta['genre'] = temp
        meta['studio'] = show.network
        meta['status'] = show.status
        meta['cast'] = []
        if show.actors:
            for actor in show.actors:
                meta['cast'].append(actor)
        meta['banner_url'] = show.banner_url
        meta['imgs_prepacked'] = self.prepack_images
        meta['cover_url'] = show.poster_url
        meta['backdrop_url'] = show.fanart_url
        meta['overlay'] = 6
        meta['trailer_url'] = ''
        return meta

    def _episode_to_meta(self, episode, tvshowtitle, show, overlay=6, playcount=0):
        meta = {}
        meta['imdb_id'] = self._check(episode.imdb_id)
        meta['tvdb_id'] = self._check(episode.show_id)
        meta['episode_id'] = self._check(episode.id)
        meta['season'] =  int(self._check(episode.season_number, 0))
        meta['episode'] = int(self._check(episode.episode_number, 0))
        meta['title'] = self._check(episode.name)
        meta['director'] = self._check(episode.director)
        meta['writer'] = self._check(episode.writer)
        meta['plot'] = self._check(episode.overview)
        if episode.guest_stars:
            guest_stars = episode.guest_stars
            if guest_stars.startswith('|'):
                guest_stars = guest_stars[1:-1]
            guest_stars = guest_stars.replace('|', ', ')
            meta['plot'] = meta['plot'] + '\n\nGuest Starring: ' + guest_stars
        meta['rating'] = float(self._check(episode.rating, 0))
        meta['premiered'] = self._check(episode.first_aired)
        meta['poster'] = self._check(episode.image)
        meta['cover_url'] =  self._check(episode.image)
        meta['trailer_url'] = ''
        meta['overlay'] = overlay
        meta['playcount'] = playcount
        meta['absolute_episode'] = int(self._check(episode.absolute_number)) if episode.absolute_number else -1

        if show.genre != '':
            temp = show.genre.replace("|",",")
            meta['genre'] = temp[1:(len(temp)-1)]
        meta['duration'] = int(show.runtime) * 60
        meta['studio'] = self._check(show.network)
        meta['mpaa'] = show.content_rating
        meta['backdrop_url'] = show.fanart_url
        meta['banner_url'] = show.banner_url

        return meta

    def __filter_meta_list_by_airdate(self, meta_list, first_air_date, num_episodes):
        helper.log_debug('Filtering metadata list by airdate %s' % first_air_date)
        # For some stupid reason, the tvdb may have the premiere date one-off, 
        # maybe because it aired in Japan first or something, I don't know
        first_date = helper.get_datetime(first_air_date, '%Y-%m-%d')
        tmp_meta_list = []
        for meta in meta_list:
            if num_episodes == 0: # end of the sequence
                break
            if meta['absolute_episode'] == -1:
                helper.log_debug('Filtering out meta')
                continue
            if len(tmp_meta_list) > 0: # middle of the sequence
                helper.log_debug('Found next meta')
                tmp_meta_list.append(meta)
                num_episodes -= 1
                continue
            if meta['premiered'] == '':
                helper.log_debug('Episode has no premiered data, so skipping')
                continue
            date = helper.get_datetime(meta['premiered'], '%Y-%m-%d')
            days = abs((first_date - date).days)
            if days <= 1: # start of the sequence
                helper.log_debug('Found first meta')
                tmp_meta_list.append(meta)
                num_episodes -= 1
            else:
                helper.log_debug('Skipping meta for absolute episode %d' % meta['absolute_episode'])

        final_meta_list = sorted(tmp_meta_list, key=lambda d: d['absolute_episode'])
        return final_meta_list

    def __filter_meta_list_by_season(self, meta_list, season, num_episodes):
        helper.log_debug('Filtering metadata list by season %d' % season)
        tmp_meta_list = []
        for meta in meta_list:
            if num_episodes == 0:
                break
            if len(tmp_meta_list) > 0: # in sequence
                helper.log_debug('Found next meta')
                tmp_meta_list.append(meta)
                num_episodes -= 1
            elif meta['season'] == season:
                helper.log_debug('Found first meta')
                tmp_meta_list.append(meta)
                num_episodes -= 1
            else:
                helper.log_debug('Skipping meta')
                pass
        final_meta_list = sorted(tmp_meta_list, key=lambda d: d['absolute_episode'])
        return tmp_meta_list

    def __cache_find_absolute_episode(self, tvdb_id, first_air_date, season):
        sql_select = 'SELECT absolute_episode FROM episode_meta WHERE tvdb_id=? AND '
        if first_air_date != '':
            sql_select += 'premiered=?'
            params = (tvdb_id, first_air_date)
        elif season != None:
            sql_select += 'season=? AND episode=1'
            params = (tvdb_id, season)
        else:
            sql_select += 'season=1 AND episode=1'
            params = (tvdb_id, )

        helper.log_debug('SQL select: %s with params %s' % (sql_select, params))
        try:
            self.dbcur.execute(sql_select, params)
            matchedrow = self.dbcur.fetchone()
        except Exception, e:
            helper.log_debug('************* Error attempting to select from Episode table: %s ' % e)
            return None
        return matchedrow

    def _cache_lookup_by_id(self, media_type, imdb_id = '', tmdb_id = ''):
        self.lock.acquire()
        result = MetaData._cache_lookup_by_id(self, media_type, imdb_id, tmdb_id)
        self.lock.release()
        return result

    def _cache_lookup_by_name(self, media_type, name, year = ''):
        self.lock.acquire()
        result = MetaData._cache_lookup_by_name(self, media_type, name, year)
        self.lock.release()
        return result

    def _cache_save_video_meta(self, meta_group, name, media_type, overlay = 6):
        self.lock.acquire()
        MetaData._cache_save_video_meta(self, meta_group, name, media_type, overlay)
        self.lock.release()

    def _cache_delete_video_meta(self, media_type, imdb_id, tmdb_id, name, year):
        self.lock.acquire()
        MetaData._cache_delete_video_meta(self, media_type, imdb_id, tmdb_id, name, year)
        self.lock.release()

    def _format_tmdb_meta(self, md, imdb_id, name, year):
        if md.get('runtime', 0) == None:
            md['runtime'] = 0
        return MetaData._format_tmdb_meta(self, md, imdb_id, name, year)


meta = init()