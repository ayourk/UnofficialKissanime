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


import os, sys, xbmcvfs


plugin_name = 'plugin.video.unofficialkissanime'
domain_url = 'https://kissanime.to/'


submenu_browse = [
    ('A-Z', {'srctype':'local', 'value':'submenu_alphabet', 'action':'genericList'}),
    ('Popular', {'srctype':'web', 'value':'AnimeList/MostPopular', 'action':'mediaContainerList'}),
    ('Last updated', {'srctype':'web', 'value':'AnimeList/LatestUpdate', 'action':'mediaContainerList'}),
    ('Newest', {'srctype':'web', 'value':'AnimeList/Newest', 'action':'mediaContainerList'}),
    ('Upcoming', {'srctype':'web', 'value':'UpcomingAnime', 'action':'mediaContainerList'}),
    ('Genre', {'srctype':'local', 'value':'submenu_genres', 'action':'genericList'}),
    ('Ongoing', {'srctype':'web', 'value':'Status/Ongoing/MostPopular', 'action':'mediaContainerList'}),
    ('Completed', {'srctype':'web', 'value':'Status/Ongoing/MostPopular', 'action':'mediaContainerList'})
]

submenu_alphabet = [
    ('All', {'srctype':'web', 'value':'AnimeList', 'action':'mediaContainerList'}),
    ('#', {'srctype':'web', 'value':'AnimeList?c=0', 'action':'mediaContainerList'}),
    ('A', {'srctype':'web', 'value':'AnimeList?c=a', 'action':'mediaContainerList'}),
    ('B', {'srctype':'web', 'value':'AnimeList?c=b', 'action':'mediaContainerList'}),
    ('C', {'srctype':'web', 'value':'AnimeList?c=c', 'action':'mediaContainerList'}),
    ('D', {'srctype':'web', 'value':'AnimeList?c=d', 'action':'mediaContainerList'}),
    ('E', {'srctype':'web', 'value':'AnimeList?c=e', 'action':'mediaContainerList'}),
    ('F', {'srctype':'web', 'value':'AnimeList?c=f', 'action':'mediaContainerList'}),
    ('G', {'srctype':'web', 'value':'AnimeList?c=g', 'action':'mediaContainerList'}),
    ('H', {'srctype':'web', 'value':'AnimeList?c=h', 'action':'mediaContainerList'}),
    ('I', {'srctype':'web', 'value':'AnimeList?c=i', 'action':'mediaContainerList'}),
    ('J', {'srctype':'web', 'value':'AnimeList?c=j', 'action':'mediaContainerList'}),
    ('K', {'srctype':'web', 'value':'AnimeList?c=k', 'action':'mediaContainerList'}),
    ('L', {'srctype':'web', 'value':'AnimeList?c=l', 'action':'mediaContainerList'}),
    ('M', {'srctype':'web', 'value':'AnimeList?c=m', 'action':'mediaContainerList'}),
    ('N', {'srctype':'web', 'value':'AnimeList?c=n', 'action':'mediaContainerList'}),
    ('O', {'srctype':'web', 'value':'AnimeList?c=o', 'action':'mediaContainerList'}),
    ('P', {'srctype':'web', 'value':'AnimeList?c=p', 'action':'mediaContainerList'}),
    ('Q', {'srctype':'web', 'value':'AnimeList?c=q', 'action':'mediaContainerList'}),
    ('R', {'srctype':'web', 'value':'AnimeList?c=r', 'action':'mediaContainerList'}),
    ('S', {'srctype':'web', 'value':'AnimeList?c=s', 'action':'mediaContainerList'}),
    ('T', {'srctype':'web', 'value':'AnimeList?c=t', 'action':'mediaContainerList'}),
    ('U', {'srctype':'web', 'value':'AnimeList?c=u', 'action':'mediaContainerList'}),
    ('V', {'srctype':'web', 'value':'AnimeList?c=v', 'action':'mediaContainerList'}),
    ('W', {'srctype':'web', 'value':'AnimeList?c=w', 'action':'mediaContainerList'}),
    ('X', {'srctype':'web', 'value':'AnimeList?c=x', 'action':'mediaContainerList'}),
    ('Y', {'srctype':'web', 'value':'AnimeList?c=y', 'action':'mediaContainerList'}),
    ('Z', {'srctype':'web', 'value':'AnimeList?c=z', 'action':'mediaContainerList'})
]

submenu_genres = [
    ('Action', {'srctype':'web', 'value':'Genre/Action', 'action':'mediaContainerList'}),
    ('Adventure', {'srctype':'web', 'value':'Genre/Adventure', 'action':'mediaContainerList'}),
    ('Cars', {'srctype':'web', 'value':'Genre/Cars', 'action':'mediaContainerList'}),
    ('Cartoon', {'srctype':'web', 'value':'Genre/Cartoon', 'action':'mediaContainerList'}),
    ('Comedy', {'srctype':'web', 'value':'Genre/Comedy', 'action':'mediaContainerList'}),
    ('Dementia', {'srctype':'web', 'value':'Genre/Dementia', 'action':'mediaContainerList'}),
    ('Demons', {'srctype':'web', 'value':'Genre/Demons', 'action':'mediaContainerList'}),
    ('Drama', {'srctype':'web', 'value':'Genre/Drama', 'action':'mediaContainerList'}),
    ('Dub', {'srctype':'web', 'value':'Genre/Dub', 'action':'mediaContainerList'}),
    ('Ecchi', {'srctype':'web', 'value':'Genre/Ecchi', 'action':'mediaContainerList'}),
    ('Fantasy', {'srctype':'web', 'value':'Genre/Fantasy', 'action':'mediaContainerList'}),
    ('Game', {'srctype':'web', 'value':'Genre/Game', 'action':'mediaContainerList'}),
    ('Harem', {'srctype':'web', 'value':'Genre/Harem', 'action':'mediaContainerList'}),
    ('Historical', {'srctype':'web', 'value':'Genre/Historical', 'action':'mediaContainerList'}),
    ('Horror', {'srctype':'web', 'value':'Genre/Horror', 'action':'mediaContainerList'}),
    ('Josei', {'srctype':'web', 'value':'Genre/Josei', 'action':'mediaContainerList'}),
    ('Kids', {'srctype':'web', 'value':'Genre/Kids', 'action':'mediaContainerList'}),
    ('Magic', {'srctype':'web', 'value':'Genre/Magic', 'action':'mediaContainerList'}),
    ('Martial Arts', {'srctype':'web', 'value':'Genre/Martial ', 'action':'mediaContainerList'}),
    ('Mecha', {'srctype':'web', 'value':'Genre/Mecha', 'action':'mediaContainerList'}),
    ('Military', {'srctype':'web', 'value':'Genre/Military', 'action':'mediaContainerList'}),
    ('Movie', {'srctype':'web', 'value':'Genre/Movie', 'action':'mediaContainerList'}),
    ('Music', {'srctype':'web', 'value':'Genre/Music', 'action':'mediaContainerList'}),
    ('Mystery', {'srctype':'web', 'value':'Genre/Mystery', 'action':'mediaContainerList'}),
    ('ONA', {'srctype':'web', 'value':'Genre/ONA', 'action':'mediaContainerList'}),
    ('OVA', {'srctype':'web', 'value':'Genre/OVA', 'action':'mediaContainerList'}),
    ('Parody', {'srctype':'web', 'value':'Genre/Parody', 'action':'mediaContainerList'}),
    ('Police', {'srctype':'web', 'value':'Genre/Police', 'action':'mediaContainerList'}),
    ('Psychological', {'srctype':'web', 'value':'Genre/Psychological', 'action':'mediaContainerList'}),
    ('Romance', {'srctype':'web', 'value':'Genre/Romance', 'action':'mediaContainerList'}),
    ('Samurai', {'srctype':'web', 'value':'Genre/Samurai', 'action':'mediaContainerList'}),
    ('School', {'srctype':'web', 'value':'Genre/School', 'action':'mediaContainerList'}),
    ('Sci-Fi', {'srctype':'web', 'value':'Genre/Sci', 'action':'mediaContainerList'}),
    ('Seinen', {'srctype':'web', 'value':'Genre/Seinen', 'action':'mediaContainerList'}),
    ('Shoujo', {'srctype':'web', 'value':'Genre/Shoujo', 'action':'mediaContainerList'}),
    ('Shoujo Ai', {'srctype':'web', 'value':'Genre/Shoujo ', 'action':'mediaContainerList'}),
    ('Shounen', {'srctype':'web', 'value':'Genre/Shounen', 'action':'mediaContainerList'}),
    ('Shounen Ai', {'srctype':'web', 'value':'Genre/Shounen ', 'action':'mediaContainerList'}),
    ('Slice of Life', {'srctype':'web', 'value':'Genre/Slice ', 'action':'mediaContainerList'}),
    ('Space', {'srctype':'web', 'value':'Genre/Space', 'action':'mediaContainerList'}),
    ('Special', {'srctype':'web', 'value':'Genre/Special', 'action':'mediaContainerList'}),
    ('Sports', {'srctype':'web', 'value':'Genre/Sports', 'action':'mediaContainerList'}),
    ('Super Power', {'srctype':'web', 'value':'Genre/Super ', 'action':'mediaContainerList'}),
    ('Supernatural', {'srctype':'web', 'value':'Genre/Supernatural', 'action':'mediaContainerList'}),
    ('Thriller', {'srctype':'web', 'value':'Genre/Thriller', 'action':'mediaContainerList'}),
    ('Vampire', {'srctype':'web', 'value':'Genre/Vampire', 'action':'mediaContainerList'}),
    ('Yuri', {'srctype':'web', 'value':'Genre/Yuri', 'action':'mediaContainerList'})
]

main_menu = [
#    ('Last Anime Visited', {'srctype':'web', 'value':'sql', 'action':'mediaList'),
    ('Browse', {'srctype':'local', 'value':'submenu_browse', 'action':'genericList'})
#    ('Account', {'value':'nothing'),
#    ('Search', {'value':'dialog_search'),
#    ('Settings', {'value':'dialog_settings'}
]

ui_table = {
    'main_menu' : main_menu,
    'submenu_browse' : submenu_browse,
    'submenu_alphabet' : submenu_alphabet,
    'submenu_genres' : submenu_genres
}