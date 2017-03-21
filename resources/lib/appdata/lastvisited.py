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
from resources.lib.common import constants
from resources.lib.common.args import args


class LastVisited(object):
    def __init__(self, *args, **kwargs):
        import os
        from sqlite3 import dbapi2 as database
        db_path = os.path.join(helper.get_profile(), constants.appdata_cache_path)
        self.dbcon = database.connect(db_path)
        self.dbcon.row_factory = database.Row
        self.dbcur = self.dbcon.cursor()
        self.__createTable()

    def __createTable(self):
        sql_create = 'CREATE TABLE IF NOT EXISTS last_visited ('\
            'id TEXT, '\
            'action TEXT, '\
            'srctype TEXT, '\
            'value TEXT, '\
            'icon TEXT, '\
            'fanart TEXT, '\
            'full_mc_name TEXT, '\
            'base_mc_name TEXT, '\
            'imdb_id TEXT, '\
            'tvdb_id TEXT, '\
            'tmdb_id TEXT, '\
            'media_type TEXT, '\
            'UNIQUE(id))'
        self.dbcur.execute(sql_create)

    def __get_row(self, id):
        sql_select = 'SELECT * FROM last_visited WHERE id=?'
        helper.log_debug('SQL SELECT: %s with params: %s' % (sql_select, id))
        self.dbcur.execute(sql_select, (id, ))
        matchedrow = self.dbcur.fetchone()
        return dict(matchedrow) if matchedrow else None

    def __update_row(self, id):
        sql_update = 'INSERT OR REPLACE INTO last_visited '\
            '(id, action, srctype, value, icon, fanart, full_mc_name, base_mc_name, '\
            'imdb_id, tvdb_id, tmdb_id, media_type) '\
            'VALUES (' + (', '.join('?' * 12)) + ')'
        # Be sure to decode the names which may contain funky characters!
        full_mc_name = args.full_mc_name.decode('utf8')
        base_mc_name = args.base_mc_name.decode('utf8')
        data = (id, args.action, args.srctype, args.value, args.icon, args.fanart,
                full_mc_name, base_mc_name, args.imdb_id, args.tvdb_id, args.tmdb_id, 
                args.media_type)
        helper.log_debug('SQL INSERT OR REPLACE: %s with params %s' % (sql_update, str(data)))
        self.dbcur.execute(sql_update, data)
        self.dbcon.commit()

    def get_prev_page(self):
        return self.__get_row('previouspage')

    def update_prev_page(self):
        self.__update_row('previouspage')

    def get_last_anime_visited(self):
        return self.__get_row('lastanimevisited')

    def update_last_anime_visited(self):
        self.__update_row('lastanimevisited')