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
from resources.lib.common import controller


print "type: %s" % str(type(helper))
helper.location("default entry point")

params = dict(helper.queries)
action = params.get('action')

if action == None:
    controller.Controller().main_menu()
elif action == 'genericList':
    controller.Controller().show_list(params)
elif action == 'mediaContainerList':
    controller.Controller().show_media_container_list(params)
elif action == 'mediaList':
    controller.Controller().show_media_list(params)
elif action == 'media':
    controller.Controller().show_media(params)
elif action == 'play':
    controller.Controller().play_video(params)
else:
    helper.log_error("WHAT HAVE YOU DONE?")
    helper.show_error_dialog(['Something went wrong.  Please restart the addon.'])

helper.location("default exit point")