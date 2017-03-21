# -*- coding: utf-8 -*-
'''
    The Unofficial KissAnime Plugin, aka UKAP - a plugin for Kodi
    Copyright (C) 2016 dat1guy

    This file is part of UKAP.

    UKAP is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    UKAP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with UKAP.  If not, see <http://www.gnu.org/licenses/>.
'''


from resources.lib.list_types.web_list import WebList
from resources.lib.common.helpers import helper


class QualityList(WebList):
    ''' OVERRIDDEN PROTECTED FUNCTIONS '''
    def parse(self):
        if self.soup == None:
            return

        self.quality_options = self.soup.find(id='slcQualix')
        if self.quality_options:
            helper.log_debug('Using KissAnime or Beta servers')
            self.links = self.quality_options.find_all('option')
        else:
            helper.log_debug('Could not find KissAnime server links; attempting to find Openload link')
            try:
                video_str = self._get_default_video_link()
                from bs4 import BeautifulSoup
                fake_soup = BeautifulSoup('<option value="%s">Openload</option>' % video_str, "html.parser")
                self.links = fake_soup.find_all('option')
                helper.log_debug('Successfully found and parsed Openload link %s' % self.links)
            except Exception as e:
                self.links = []
                helper.log_debug('Failed to parse Openload link with exception: %s' % str(e))
                helper.show_error_dialog("Could not find supported video link for this episode/movie")
            
    def add_items(self):
        num_links = len(self.links)
        for option in self.links:
            quality = option.string
            link_val = self.decode_link(option['value'])

            # If we failed to decode the link, then we'll just use the already selected option and ignore the rest
            if link_val == '':
                selected_quality_opt = self.quality_options.find('option', selected=True)
                quality = 'Default quality - %s' % selected_quality_opt.string
                link_val = self._get_default_video_link()
                num_links = 1

            query = self._construct_query(link_val, 'play')
            helper.add_video_item(query, {'title':quality}, total_items=num_links)
            if 'Default quality' in quality:
                break

        helper.end_of_directory()

    def decode_link(self, url):
        if not url:
            return ''

        helper.log_debug('URL to decode: %s' % url)
        if 'https://' in url:
            decoded_link_val = url # Openload probably, since it's already a valid link
        else:
            decoded_link_val = self._decrypt_link(url.decode('base64'))

        return decoded_link_val

    def _get_default_video_link(self):
        video_str = self.html.split('#divContentVideo')[1].split('iframe')[1].split('src=')[1].split('"')[1]
        helper.log_debug('Got default video string: %s' % video_str)
        return video_str

    def _decrypt_text(self, key, iv, txt):
        from resources.lib import pyaes
        decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv=iv))
        decrypted_txt = decrypter.feed(txt)
        decrypted_txt += decrypter.feed()
        return decrypted_txt

    def _decrypt_link(self, url):
        iv = 'a5e8d2e9c1721ae0e84ad660c472c1f3'.decode('hex')
        if (helper.debug_decrypt_key() != ''):
            helper.log_debug('Using the key input in the debug settings')
            key = helper.debug_decrypt_key().decode('hex')
        else:
            key = self._get_key_from_html()

        try:
            decrypted_link_val = self._decrypt_text(key, iv, url)
            helper.log_debug('Successfully decrypted link %s' % decrypted_link_val)
        except Exception as e:
            helper.log_debug('Failed to decrypt the link with exception %s' % str(e))
            decrypted_link_val = ''

        return decrypted_link_val

    def _get_base_skH(self, filename):
        if filename == 'vr.js':
            return 'nhasasdbasdtene7230asb'
        elif filename == 'skH =':
            # We need to find the last skH before ovelwrap
            split1 = self.html.split("ovelWrap($('#slcQualix').val())")[0]
            split2 = split1.split('skH =')[-2]
            da_list_str = '[' + split2.split('[')[-1].strip('; ')
            import ast
            da_list = ast.literal_eval(da_list_str)
            helper.log_debug('da_list %s' % da_list)
            return da_list[0]
        else:
            helper.log_debug('Do not recognize base skH file')
            return ''

    def _get_modified_skH(self, skH, filename):
        if filename == 'shal.js':
            return skH + '6n23ncasdln213'
        elif filename == 'moon.js':
            return skH + 'znsdbasd012933473'
        elif filename == 'file3.js':
            return skH.replace('a', 'c')
        else:
            helper.log_debug('Do not recognize skH modifier file')
            return skH

    def _get_key_from_html(self):
        helper.log_debug('Attempting to get key from html')

        set_skH_code = ['vr.js', 'skH =']
        set_skH_dict = {}
        for f in set_skH_code:
            set_skH_dict[f] = self.html.rfind(f)
        
        # Find latest key setter
        sorted_skH = sorted(set_skH_dict, key=set_skH_dict.get, reverse=True)
        last_set_skH_file = sorted_skH[0]
        last_set_skH_line = set_skH_dict[last_set_skH_file]

        skH = self._get_base_skH(last_set_skH_file)

        # Find modifications
        js_files = ['shal.js', 'moon.js', 'file3.js']
        js_dict = {}
        for f in js_files:
            js_dict[f] = self.html.find(f)

        # Filter modifications if they come before the line that sets skH
        js_dict = {k: v for k, v in js_dict.iteritems() if v > last_set_skH_line}

        # Sort the modifications by appearance
        sorted_js = sorted(js_dict, key=js_dict.get, reverse=False)

        # Apply the modification
        for k in sorted_js:
            skH = self._get_modified_skH(skH, k)

        import hashlib
        key = hashlib.sha256(skH).hexdigest()
        helper.log_debug('Found the key: %s' % key)
        
        return key.decode('hex')