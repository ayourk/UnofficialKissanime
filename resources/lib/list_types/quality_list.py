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

        self.links = self.soup.find(id='slcQualix').find_all('option')

    def add_items(self):
        from resources.lib import pyaes
        key = '3353fbae49f94c2c62919cc10c526573ad65f0a79cfe3576b56ecdcd9571901d'.decode('hex')
        iv = 'a5e8d2e9c1721ae0e84ad660c472c1f3'.decode('hex')
        for option in self.links:
            quality = option.string
            decoded_link_val = option['value'].decode('base-64')

            decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv=iv))
            decrypted = decrypter.feed(decoded_link_val)
            decrypted += decrypter.feed()
            link_val = decrypted

            query = self._construct_query(link_val, 'play')
            helper.add_video_item(query, {'title':quality}, total_items=len(self.links))
        helper.end_of_directory()