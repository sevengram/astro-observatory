#! /usr/bin/env python2
# -*- coding:utf8 -*-

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options

define('port', default=20100, help="run on the given port", type=int)
define('env', default='dev', help="run on the given environment", type=str)
define('conf', default='config', help="config file dir", type=str)

tornado.options.parse_command_line()

from wechat import MsgHandler
from astrometry import AstrometryHandler

application = tornado.web.Application(
    handlers=[
        (r'/notify/messages', MsgHandler),
        (r'/astrometry', AstrometryHandler)
    ], debug=True
)

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
