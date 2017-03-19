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


from resources.lib.list_types.web_list import WebList
from resources.lib.common.helpers import helper


class QualityList(WebList):
    ''' OVERRIDDEN PROTECTED FUNCTIONS '''
    def parse(self):
        if self.soup == None:
            return

        hasQuality = self.soup.find(id='slcQualix')
        if hasQuality:
            self.links = hasQuality.find_all('option')
        else:
            helper.log_debug('Could not find KissAnime server links; attempting to find Openload link')
            try:
                split_str = self.html.split('#divContentVideo')[1].split('iframe')[1].split('src=')[1].split('"')[1]
                helper.log_debug('Split string attempt: %s' % split_str)
                from bs4 import BeautifulSoup
                fake_soup = BeautifulSoup('<option value="%s">Openload</option>' % split_str)
                self.links = fake_soup.find_all('option')
                helper.log_debug('Successfully found and parsed Openload link %s' % self.links)
            except Exception as e:
                self.links = []
                helper.log_debug('Failed to parse Openload link with exception: %s' % str(e))
                helper.show_error_dialog("Could not find supported video link for this episode/movie")
            
    def add_items(self):
        for option in self.links:
            quality = option.string
            link_val = self.decode_link(option['value'])
            query = self._construct_query(link_val, 'play')
            helper.add_video_item(query, {'title':quality}, total_items=len(self.links))
        helper.end_of_directory()

    def decode_link(self, url):
        if not url:
            return ''

        if 'https://' in url:
            decrypted_link_val = url # Openload probably, since it's already a valid link
        else:
            from resources.lib import pyaes
            key = '77523155af8cbed35649d6b9ad2f6a9596609be26cde24ee0334b80ae673b803'.decode('hex')
            if (helper.debug_decrypt_key() != ''):
                key = helper.debug_decrypt_key().decode('hex')
            iv = 'a5e8d2e9c1721ae0e84ad660c472c1f3'.decode('hex')
            decoded_link_val = url.decode('base-64')
            decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv=iv))
            decrypted_link_val = decrypter.feed(decoded_link_val)
            decrypted_link_val += decrypter.feed()

        return decrypted_link_val