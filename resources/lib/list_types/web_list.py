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
from resources.lib.common import args
from resources.lib.common.helpers import helper
from bs4 import BeautifulSoup


class WebList(object):
    def __init__(self, url_val=args.value, form_data=None):
        self.html = ''
        self.soup = None
        self.links = []
        self.has_next_page = False

        from resources.lib.metadata.loose_metahandlers import meta
        self.meta = meta
        from resources.lib.common.nethelpers import net, cookies
        self.net, self.cookies = net, cookies

        if not url_val:
            return

        assert(args.srctype == 'web')
        url = url_val if 'http' in url_val else (helper.domain_url() + url_val)
        self.html, e = self.net.get_html(url, self.cookies, helper.domain_url(), form_data)
        self.html = helper.handle_html_errors(self.html, e)
        helper.log_debug('HTML is %sempty' % ('' if self.html == '' else 'not '))
        
        self.html = self._filter_html(self.html)
        self.soup = BeautifulSoup(self.html) if self.html != '' else None

    def parse(self):
        pass

    def add_items(self):
        pass

    def _get_metadata(self):
        pass

    def _filter_html(self, html):
        new_lines = []
        for line in html.split('\n'):
            if 'Please disable AdBlock' not in line:
                new_lines.append(line)
        html = '\n'.join(new_lines)
        return html

    def _get_art_from_metadata(self, metadata):
        icon = metadata.get('cover_url', args.icon)
        fanart = metadata.get('backdrop_url', args.fanart)
        return (icon, fanart)

    def _construct_query(self, value, action, metadata={}, full_mc_name='', media_type=''):
        icon, fanart = self._get_art_from_metadata(metadata)
        base_mc_name = metadata.get('title', '')
        imdb_id = metadata.get('imdb_id', '')
        tvdb_id = metadata.get('tvdb_id', '')
        tmdb_id = metadata.get('tmdb_id', '')
        query = {'srctype':'web', 'value':value, 'action':action, 'imdb_id':imdb_id, 
                 'tvdb_id':tvdb_id, 'tmdb_id':tmdb_id, 'icon':icon, 'fanart':fanart,
                 'base_mc_name':base_mc_name, 'full_mc_name':full_mc_name, 'media_type':media_type}
        return query
    
    # This may belong somewhere else...
    def _strip_by_re(self, string, filter, end, start=0):
        return string[start:end] if re.search(filter, string) != None else string

    def _clean_name(self, name, specials=True):
        cleaned_name = name.replace(' (Sub)', '').replace(' (Dub)', '')
        if specials:
            cleaned_name = cleaned_name.replace (' (OVA)', '').replace (' Specials ', '')
            cleaned_name = self._strip_by_re(cleaned_name, '( OVA)$', end=-4)
            cleaned_name = self._strip_by_re(cleaned_name, '( Special)$', end=-8)
            cleaned_name = self._strip_by_re(cleaned_name, '( Specials)$', end=-9)
        cleaned_name = self._strip_by_re(cleaned_name, '( \(1080p\))$', end=-8)
        cleaned_name = self._strip_by_re(cleaned_name, '( \((720|480|360)p\))$', end=-8)
        return cleaned_name