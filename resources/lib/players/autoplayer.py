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


from resources.lib.common.helpers import helper
from resources.lib.list_types.quality_list import QualityList
from resources.lib.players.videoplayer import VideoPlayer


class AutoPlayer(QualityList, VideoPlayer):
    def __init__(self, url=''):
        QualityList.__init__(self)
        VideoPlayer.__init__(self, url)

    def add_items(self):
        preset_quality = int(helper.get_setting('preset-quality').strip('p'))

        for option in self.links:
            quality = option.string
            if preset_quality >= int(quality.strip('p')):
                helper.log_debug('Found media to play at matching quality: %s' % quality)
                url_to_play = option['value']
                break

        assert(len(encoded_links) > 0)
        if url_to_play == None:
            helper.log_debug('No matching quality found; using the lowest available')
            url_to_play = encoded_links[-1]['value']

        self.link = self.decode_link(url_to_play)