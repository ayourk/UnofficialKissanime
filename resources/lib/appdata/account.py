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


from resources.lib.common.helpers import helper
from resources.lib.common.nethelpers import net, cookies
from resources.lib.common import args


class Account(object):
    def __init__(self):
        pass

    def login(self):
        username = helper.get_setting('username')
        password = helper.get_setting('password')
        if len(username) == 0 or len(password) == 0:
            return False

        username_and_password = 0
        for cookie in net._cj:
            if cookie.name.lower() == 'username' or cookie.name.lower() == 'password':
                username_and_password += 1
        if username_and_password == 2:
            return True

        # Log in through the page
        url = helper.domain_url() + 'Login'
        form_data = {'username': username, 'password': password, 'chkRemember': 1}
        html, e = net.get_html(url, cookies, helper.domain_url(), form_data)
        html = helper.print_html_errors(html, e)

        return (len(html) > 0)

    def logout(self):
        net.refresh_cookies()

    def is_in_bookmark_list(self, id=args.value):
        url = helper.domain_url() + 'CheckBookmarkStatus'
        html, e = net.get_html(url, cookies, helper.domain_url(), {'animeId':id})
        helper.print_html_errors(html, e)
        if html == '':
            return None
        elif html == 'null':
            return False
        else:
            return True

    def toggle_bookmark(self):
        self.remove_bookmark() if self.is_in_bookmark_list() else self.add_bookmark()

    def add_bookmark(self):
        self._perform_bookmark_operation(True)

    def remove_bookmark(self):
        proceed = helper.show_yes_no_dialog('Are you sure you want to remove the show from your bookmarks?')
        if proceed:
            self._perform_bookmark_operation(False)

    # if add == False, remove, otherwise add
    def _perform_bookmark_operation(self, add):
        helper.start('Account._perform_bookmark_operation: %s' % ('add' if add else 'remove'))
        helper.show_busy_notification()
        bookmark_id = args.value
        url = '%sBookmark/%s/%s' % (helper.domain_url(), bookmark_id, 'add' if add else 'remove')
        html, e = net.get_html(url, cookies, helper.domain_url(), {'no-op':0})
        html = helper.print_html_errors(html, e)
        helper.close_busy_notification()
        if html != '':
            helper.refresh_page()
            msg = 'Successfully %s the bookmark list' % ('added to' if add else 'removed from')
            helper.show_ok_dialog([msg])
        helper.end('Account._perform_bookmark_operation')
