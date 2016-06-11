# -*- coding: utf-8 -*-

from configparser import ConfigParser

import motor
import tornado.gen
from tornado.options import options

from util import sqldb


class AstroSqldb(sqldb.Sqldb):
    def __init__(self, db_name, db_host, db_user, db_pwd):
        super(AstroSqldb, self).__init__(db_name, db_host, db_user, db_pwd)

    def add_location(self, location):
        self.replace('location', location)

    def get_location(self, query):
        return self.get('location', {'query': query})

    def get_last_query(self, openid):
        return self.get('users', {'openid': openid})

    def add_user_record(self, record):
        self.replace('users', record)


__db_parser = ConfigParser()
__db_parser.read(options.conf + '/db.conf')

astro_storage = AstroSqldb(**dict(__db_parser.items(options.env)))


class MongoConnector(object):
    def __init__(self, debug=False):
        self.client = motor.MotorClient("mongodb://localhost:27017/astro_data")
        self.datadb = self.client.astro_data
        self.debug = debug

    def __del__(self):
        self.client.close()

    @tornado.gen.coroutine
    def find_constellation(self, query):
        result = yield motor.Op(self.datadb.constellation.find_one, {
            '$or': [{'chinese': query}, {'alias': query}, {'abbr': query.upper()}, {'full': query.capitalize()},
                    {'gen': query.capitalize()}]})
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def find_solar(self, query):
        result = yield motor.Op(self.datadb.solar.find_one,
                                {'$or': [{'chinese': query}, {'name': query.capitalize()}, {'alias': query}]})
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def find_deepsky(self, query):
        if query.startswith('Abell'):
            res = yield motor.Op(self.datadb.deepsky.find_one, {
                '$or': [{'alias': query}, {'object': query}, {'cn_name': query}, {'cn_alias': query}]})
        else:
            res = yield motor.Op(self.datadb.deepsky.find_one, {
                '$or': [{'object': query}, {'alias': query}, {'cn_name': query}, {'cn_alias': query}]})
        raise tornado.gen.Return(res)


mongo_conn = MongoConnector(debug=False)
