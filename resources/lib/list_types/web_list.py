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
from resources.lib.common import args, constants
from resources.lib.common.helpers import helper
from resources.lib.common.nethelpers import net, cookies
from bs4 import BeautifulSoup


class WebList(object):
    def __init__(self):
        self.html = ''
        self.soup = None
        self.links = []
        self.has_next_page = False

        assert(args.srctype == 'web')
        url_val = args.value
        url = url_val if constants.domain_url in url_val else (constants.domain_url + url_val)
        self.html, e = net.get_html(url, cookies, constants.domain_url)
        if self.html == '':
            if e.read() == 'The service is unavailable.':
                helper.log_debug('The service is unavailable.')
                helper.show_error_dialog(['Kissanime is reporting that their service is currently unavailable.','','Please try again later.'])
            elif e.read() == "You're browsing too fast! Please slow down.":
                helper.log_debug('Got the browsing too fast error 1.')
                helper.show_error_dialog(["Kissanime is reporting that you're browsing too quickly.",'','Please wait a bit and slow down :)'])
            else:
                helper.log_debug('Failed to grab HTML' + ('' if e == None else ' with exception %s' % str(e)))
                helper.show_error_dialog([
                    'Failed to parse the KissAnime website.',
                    'Please see the error below.  If it has to do with HTTP exception 503, KissAnime may be down; in that case, try again later.',
                    ('Error details: %s' % str(e))
                    ])
        elif self.html == "You're browsing too fast! Please slow down.":
            helper.log_debug('Got the browsing too fast error.')
            helper.show_error_dialog(["Kissanime is reporting that you're browsing too quickly.",'','Please wait a bit and slow down :)'])
            self.html = ''
        helper.log_debug('HTML is %sempty' % ('' if self.html == '' else 'not '))
        
        self.soup = BeautifulSoup(self.html) if self.html != '' else None

    def parse(self):
        pass

    def add_items(self):
        pass

    def _get_metadata(self):
        pass

    def _get_art_from_metadata(self, metadata):
        icon = metadata.get('cover_url', args.icon)
        fanart = metadata.get('backdrop_url', args.fanart)
        return (icon, fanart)

    def _construct_query(self, value, action, metadata={}, full_mc_name='', media_type=''):
        icon, fanart = self._get_art_from_metadata(metadata)
        base_mc_name = metadata.get('title', '')
        imdb_id = metadata.get('imdb_id', '')
        query = {'srctype':'web', 'value':value, 'action':action, 'imdb_id':imdb_id, 'icon':icon, 'fanart':fanart,
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
        cleaned_name = self._strip_by_re(cleaned_name, '( \(1080p\))$', end=-8)
        cleaned_name = self._strip_by_re(cleaned_name, '( \((720|480|360)p\))$', end=-8)
        return cleaned_name