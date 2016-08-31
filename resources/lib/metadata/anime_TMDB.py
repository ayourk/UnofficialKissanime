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


import unicodedata
from metahandler.TMDB import TMDB
from resources.lib.common.helpers import helper


class AnimeTMDB(TMDB):
    def tmdb_lookup(self, name, imdb_id='', tmdb_id='', year=''):
        if isinstance(name, unicode):
            name = unicodedata.normalize('NFKD', unicode(name)).encode('ascii', 'ignore')

        if imdb_id or tmdb_id:
            return TMDB.tmdb_lookup(self, name, imdb_id, tmdb_id, year)

        meta = self._search_movie(name, year)              
        # Retry without the year if we didn't get any results
        if meta and meta['total_results'] == 0 and year:
            meta = self._search_movie(name,'')
        if meta and meta['total_results'] != 0 and meta['results']:
            # Try to find a Japanese result if possible, since this is anime-oriented
            japanese_result = None
            for result in meta['results']:
                orig_lang = result.get('original_language', '')
                if orig_lang == 'ja':
                    japanese_result = result
                    break

            # GUESS
            # Prefer the Japanese result if the name is a straight match, or if the 
            # first result doesn't match the name
            best_guess = meta['results'][0]
            if (japanese_result != None and 
                (japanese_result['title'] == name or best_guess['title'] != name)):
                best_guess = japanese_result
            tmdb_id = best_guess['id']
            imdb_id = best_guess.get('imdb_id', imdb_id)

        return TMDB.tmdb_lookup(self, name, imdb_id, tmdb_id, year)

    def search_imdb(self, name, imdb_id='', year=''):
        if isinstance(name, unicode):
            name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')
        name = self._TMDB__clean_name(name)
        return TMDB.search_imdb(self, name, imdb_id, year)

    def _TMDB__clean_name(self, mystring):
        newstring = ''
        for word in mystring.split(' '):
            if not word.isalnum():
                w = ''
                for i in range(len(word)):
                    if(word[i].isalnum()):              
                        w += word[i]
                    # Replace non-alpha-numeric chars with a space
                    else:
                        w += ' '
                word = w
            newstring += ' ' + word
        return newstring.strip()