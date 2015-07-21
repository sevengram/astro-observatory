# -*- coding:utf8 -*-

import motor
import tornado.gen


class Connector(object):
    def __init__(self, debug=False):
        self.client = motor.MotorClient("mongodb://dsa:dsaeboue@localhost:27017/astro_data")
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
        # cursor = self.datadb.deepsky.find({'$or': [{'object': query}, {'alias': query}]}, limit=5)
        # result = yield motor.Op(cursor.to_list)
        if query.startswith('Abell'):
            res = yield motor.Op(self.datadb.deepsky.find_one, {
                '$or': [{'alias': query}, {'object': query}, {'cn_name': query}, {'cn_alias': query}]})
        else:
            res = yield motor.Op(self.datadb.deepsky.find_one, {
                '$or': [{'object': query}, {'alias': query}, {'cn_name': query}, {'cn_alias': query}]})
        raise tornado.gen.Return(res)
