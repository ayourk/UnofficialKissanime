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


import sys, time, unicodedata, xbmc, xbmcplugin
from datetime import datetime
from addon.common.addon import Addon
from resources.lib.common import constants


# I like to define my module variables at the top, which explains the purpose 
# of this init function, invoked at the bottom
def init():
    helper = Helper(constants.plugin_name, argv=sys.argv)
    return helper


class Helper(Addon):
    def location(self, msg):
        self.log_debug("----LOC  : " + msg)

    def start(self, msg):
        self.log_debug("----START: " + msg)

    def end(self, msg):
        self.log_debug("----END  : " + msg)

    # AKA youve_got_to_be_kidding_me
    def get_datetime(self, date_str, format):
        try:
            return datetime.strptime(date_str, format)
        except TypeError:
            return datetime(*(time.strptime(date_str, format)[0:6]))

    def log(self, msg, level=xbmc.LOGNOTICE):
        msg = unicodedata.normalize('NFKD', unicode(msg)).encode('ascii', 'ignore')
        Addon.log(self, msg, level)

    def set_content(self, content_type):
        xbmcplugin.setContent(self.handle, content_type)

    sort_method_dict = {
        'episode' : xbmcplugin.SORT_METHOD_EPISODE,
        'title' : xbmcplugin.SORT_METHOD_TITLE
    }

    def add_sort_methods(self, sort_methods):
        for m in sort_methods:
            if self.sort_method_dict.has_key(m):
                xbmcplugin.addSortMethod(self.handle, self.sort_method_dict[m])


helper = init()