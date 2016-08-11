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


import urlparse,sys
from resources.lib.common import controller


params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
action = params.get('action')

if action == None:
    controller.Controller().main_menu()
elif action == 'genericList':
    print "showing list"
    controller.Controller().show_list(params)
elif action == 'mediaContainerList':
    controller.Controller().show_media_container_list(params)
elif action == 'mediaList':
    controller.Controller().show_media_list(params)
else:
    print "WHAT HAVE YOU DONE?"
