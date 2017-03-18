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


import os, sys, unicodedata, xbmc, xbmcplugin, xbmcgui
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

    def debug_timestamp(self):
        return (helper.get_setting('debug-timestamp') == 'true')

    def debug_import(self):
        return (helper.get_setting('debug-import') == 'true')

    def debug_metadata_threads(self):
        return (helper.get_setting('debug-metadata-threads') == 'true')

    def debug_dump_html(self):
        return (helper.get_setting('debug-dump-html') == 'true')

    def debug_decrypt_key(self):
        return (helper.get_setting('debug-decryption-key'))

    def add_item(self, queries, infolabels, properties=None, contextmenu_items='', 
                 context_replace=False, img='', fanart='', resolved=False, total_items=0, 
                 playlist=False, item_type='video', is_folder=False):
        if fanart == '':
            fanart = self.addon.getAddonInfo('fanart')
        return Addon.add_item(self, queries, infolabels, properties, contextmenu_items, context_replace, img, fanart, resolved, total_items, playlist, item_type, is_folder)

    # AKA youve_got_to_be_kidding_me
    def get_datetime(self, date_str, format):
        if not date_str:
            None

        if len(date_str) == 4:
            format = '%Y'

        import time
        from datetime import datetime
        try:
            return datetime.strptime(date_str, format)
        except TypeError:
            return datetime(*(time.strptime(date_str, format)[0:6]))

    def log(self, msg, level=xbmc.LOGNOTICE):
        # Some strings will be unicode, and some of those will already be 
        # encoded.  This try/except tries to account for that.
        if isinstance(msg, str):
            unicode_msg = unicode(msg)
        elif isinstance(msg, unicode):
            try:
                unicode_msg = msg.decode('utf8')
            except:
                unicode_msg = msg.encode('utf8').decode('utf8')
        else:
            unicode_msg = msg
        msg = unicodedata.normalize('NFKD', unicode_msg).encode('ascii', 'ignore')
        Addon.log(self, msg, level)

    def set_content(self, content_type):
        xbmcplugin.setContent(self.handle, content_type)

    sort_method_dict = {
        'episode' : xbmcplugin.SORT_METHOD_EPISODE,
        'title' : xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE
    }

    def add_sort_methods(self, sort_methods):
        for m in sort_methods:
            if self.sort_method_dict.has_key(m):
                xbmcplugin.addSortMethod(self.handle, self.sort_method_dict[m])

    def get_user_input(self, title='', default_text='', hidden=False):
        keyboard = xbmc.Keyboard('', title, hidden)
        if default_text:
            keyboard.setDefault(default_text)
        keyboard.doModal()
        return keyboard.getText() if keyboard.isConfirmed() else None

    def show_busy_notification(self):
        xbmc.executebuiltin('ActivateWindow(busydialog)')

    def close_busy_notification(self):
        xbmc.executebuiltin('Dialog.Close(busydialog)')

    def refresh_page(self):
        xbmc.executebuiltin('Container.Refresh')

    def show_yes_no_dialog(self, msg, title=None):
        if not title:
            title = self.get_name()
        return xbmcgui.Dialog().yesno(title, msg)

    def present_selection_dialog(self, title, options):
        dialog = xbmcgui.Dialog()
        return dialog.select(title, options)

    def go_to_page_using_queries(self, queries):
        xbmc.executebuiltin('XBMC.Container.Update(%s)' % self.build_plugin_url(queries))

    def domain_url(self):
        return ('%s://%s/' % (self.get_setting('http-type'), constants.domain))

    def handle_html_errors(self, html, e):
        if html == '':
            if e.args[0] == 'The service is unavailable.':
                self.log_debug('The service is unavailable.')
                self.show_error_dialog(['Kissanime is reporting that their service is currently unavailable.','','Please try again later.'])
            elif e.args[0] == "You're browsing too fast! Please slow down.":
                self.log_debug('Got the browsing too fast error 1.')
                self.show_error_dialog(["Kissanime is reporting that you're browsing too quickly.",'','Please wait a bit and slow down :)'])
            else:
                import urllib2
                self.log_debug('Failed to grab HTML' + ('' if e == None else ' with exception %s' % str(e)))
                if isinstance(e, urllib2.HTTPError) and e.code == 503:
                    self.show_error_dialog(['The service is currently unavailable.', '', 'If it does not respond after 1 more try, the site may be temporarily down.'])
                else:
                    self.show_error_dialog([
                        'Failed to parse the KissAnime website.',
                        '',
                        ('Error details: %s' % str(e))
                        ])
        elif html == "You're browsing too fast! Please slow down.":
            self.log_debug('Got the browsing too fast error.')
            self.show_error_dialog(["Kissanime is reporting that you're browsing too quickly.",'','Please wait a bit and slow down :)'])
            html = ''
        elif html == 'Not found':
            self.log_debug('Navigated to a dead page')
            self.show_error_dialog(['This page does not exist.', '', 'If you clicked on a related link, KissAnime sometimes autogenerates related links which do not exist.'])
            html = ''

        return html

    def get_profile(self):
        profile_path = Addon.get_profile(self)
        if not os.path.exists(profile_path):
            import xbmcvfs
            try:
                xbmcvfs.mkdirs(profile_path)
            except:
                os.mkdir(profile_path)
        return profile_path    


helper = init()