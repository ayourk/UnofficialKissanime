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


from metahandler.metahandlers import MetaData
from metahandler.TMDB import TMDB
from metahandler.thetvdbapi import TheTVDB
from metahandler import common
from resources.lib.common.helpers import helper


class LooseMetaData(MetaData):
    def __init__(self, prepack_images=False, preparezip=False, tmdb_api_key='af95ef8a4fe1e697f86b8c194f2e5e11'):
        return MetaData.__init__(self, prepack_images, preparezip, tmdb_api_key)

    def _get_tvdb_meta(self, imdb_id, name, year=''):
        '''
        Requests meta data from TVDB and creates proper dict to send back
        
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
        except Exception, e:
            common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
            tvdb_id = ''
            pass
            
        #Intialize tvshow meta dictionary
        meta = self._init_tvshow_meta(imdb_id, tvdb_id, name, year)

        # if not found by imdb, try by name
        if tvdb_id == '':
            try:
                #If year is passed in, add it to the name for better TVDB search results
                if year:
                    name = name + ' ' + year
                show_list=tvdb.get_matching_shows(name) # DAT1GUY: CONSIDER USING WANT_RAW HERE
                show_list2 = tvdb.get_matching_shows(name, want_raw=True)
            except Exception, e:
                common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
                show_list = []
                pass
            common.addon.log('Found TV Show List: %s' % show_list, 0)
            tvdb_id=''
            prob_id=''

            helper.log_debug('Here are the raw results: %s' % str(show_list2))

            helper.log_debug('Have a show list to match against %s' % name)
            '''for show in show_list:
                helper.log_debug('Potential candidate %s' % str(show))
                (junk1, junk2, junk3) = show
                #if we match imdb_id or full name (with year) then we know for sure it is the right show
                if junk3==imdb_id or self._string_compare(self._clean_string(junk2),self._clean_string(name)):
                    tvdb_id=self._clean_string(junk1)
                    if not imdb_id:
                        imdb_id=self._clean_string(junk3)
                    break
                #if we match just the cleaned name (without year) keep the tvdb_id
                elif self._string_compare(self._clean_string(junk2),self._clean_string(name)):
                    prob_id = junk1
                    if not imdb_id:
                        imdb_id = self_clean_string(junk3)'''
            strcmp = self._string_compare
            clean = self._clean_string
            en_result = None
            for show in show_list2:
                # this is probably our result
                tmp_imdb_id = show['IMDB_ID'] if show.has_key('IMDB_ID') else None
                if tmp_imdb_id == imdb_id or strcmp(clean(show['SeriesName']), clean(name)) or len(show_list2) == 1: # if the list length is one, then this is probably the right result
                    tvdb_id = clean(show['seriesid'])
                    if not imdb_id:
                        imdb_id = clean(tmp_imdb_id)
                    break
                # Check aliases
                if show.has_key('AliasNames'):
                    helper.log_debug('looking at AliasNames: ' + show['AliasNames'].encode('ascii', errors='xmlcharrefreplace'))
                    helper.log_debug('here it is split: %s' % str(show['AliasNames'].encode('ascii', errors='xmlcharrefreplace').split('|')))
                    for alias in show['AliasNames'].split('|'):
                        if strcmp(clean(alias), clean(name)):
                            prob_id = clean(show['seriesid'])
                            if not imdb_id:
                                imdb_id = clean(tmp_imdb_id)
            if tvdb_id == '' and prob_id != '':
                tvdb_id = self._clean_string(prob_id)

        if tvdb_id:
            common.addon.log('Show *** ' + name + ' *** found in TVdb. Getting details...', 0)

            try:
                show = tvdb.get_show(tvdb_id)
            except Exception, e:
                common.addon.log('************* Error retreiving from thetvdb.com: %s ' % e, 4)
                show = None
                pass
            
            if show is not None:
                meta['imdb_id'] = imdb_id
                meta['tvdb_id'] = tvdb_id
                meta['title'] = name
                if str(show.rating) != '' and show.rating != None:
                    meta['rating'] = float(show.rating)
                meta['duration'] = int(show.runtime) * 60
                meta['plot'] = show.overview
                meta['mpaa'] = show.content_rating
                meta['premiered'] = str(show.first_aired)

                #Do whatever we can to set a year, if we don't have one lets try to strip it from show.first_aired/premiered
                if not year and show.first_aired:
                        #meta['year'] = int(self._convert_date(meta['premiered'], '%Y-%m-%d', '%Y'))
                        meta['year'] = int(meta['premiered'][:4])

                if show.genre != '':
                    temp = show.genre.replace("|",",")
                    temp = temp[1:(len(temp)-1)]
                    meta['genre'] = temp
                meta['studio'] = show.network
                meta['status'] = show.status
                if show.actors:
                    for actor in show.actors:
                        meta['cast'].append(actor)
                meta['banner_url'] = show.banner_url
                meta['imgs_prepacked'] = self.prepack_images
                meta['cover_url'] = show.poster_url
                meta['backdrop_url'] = show.fanart_url
                meta['overlay'] = 6

                if meta['plot'] == 'None' or meta['plot'] == '' or meta['plot'] == 'TBD' or meta['plot'] == 'No overview found.' or meta['rating'] == 0 or meta['duration'] == 0 or meta['cover_url'] == '':
                    common.addon.log(' Some info missing in TVdb for TVshow *** '+ name + ' ***. Will search imdb for more', 0)
                    helper.log_debug('help me please %s' % str(dir(self)))
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

