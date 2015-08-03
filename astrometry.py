# -*- coding:utf8 -*-

import sys
import json
import time
import urllib

import tornado.gen
import tornado.httpclient
import tornado.httputil
import tornado.web
import tornado.ioloop

import consts
from util.web import BaseHandler

reply_format = u'''赤经 %s
赤纬 %s
范围 %s
主要天体 %s
点击查看详情 %s
图像分析来自 astrometry. net
'''


def format_ra(ra):
    h = ra * 24.0 / 360.0
    m = (h - int(h)) * 60.0
    s = (m - int(m)) * 60.0
    return '%02dh %02dm %06.3fs' % (int(h), int(m), s)


def format_dec(dec):
    d = dec
    m = abs(d - int(d)) * 60.0
    s = abs(m - int(m)) * 60.0
    return u'%+03d° %02d\' %06.3f"' % (int(d), int(m), s)


def format_radius(radius):
    return '%.3f deg' % radius


def build_reply(message):
    cal = message.get('calibration')
    if cal:
        ra, dec, radius = format_ra(cal.get('ra')), format_dec(
            cal.get('dec')), format_radius(cal.get('radius'))
    else:
        ra = dec = radius = None
    objects = ', '.join(message.get('objects_in_field'))[:420]
    url = 'http://nova.astrometry.net/annotated_display/%s' % message.get('jobid')
    return reply_format % (ra, dec, radius, objects, url)


class AstrometryHandler(BaseHandler):
    def initialize(self, sign_check=False):
        super(AstrometryHandler, self).initialize(sign_check=sign_check)
        self.session = None

    @tornado.gen.coroutine
    def notify(self, url, status, message, userinfo):
        body = urllib.urlencode(
            {'status': status, 'message': message.encode('utf-8'), 'userinfo': userinfo})
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            url=url, method='POST', headers={}, body=body, connect_timeout=30, request_timeout=120)
        response = yield client.fetch(request)
        print 'notify result:' + response.body
        sys.stdout.flush()
        raise tornado.gen.Return(response)

    @tornado.gen.coroutine
    def post(self):
        pic_url = self.get_argument('pic_url')
        notify_url = self.get_argument('notify_url')
        userinfo = self.get_argument('userinfo')
        self.send_response(err_code=0, err_msg='ok')

        subid = yield self.url_upload(pic_url)
        if not subid:
            yield self.notify(notify_url, 1, 'submission error', userinfo)
            return

        yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + 10)
        count, i = 0, 5
        jobid = None
        while True:
            stat = yield self.sub_status(subid)
            if stat:
                j = None
                jobs = stat.get('jobs', [])
                for j in jobs:
                    if j:
                        break
                if j:
                    jobid = j
                    break
            count += 1
            if count == 10:
                i = 10
            elif count > 20:
                yield self.notify(notify_url, 3, 'pic reduce error', userinfo)
                return
            yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + i)

        yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + 5)
        count, i = 0, 5
        while True:
            stat = yield self.job_status(jobid)
            if stat and stat.get('status') == 'success':
                yield self.notify(notify_url, 0, build_reply(stat), userinfo)
                return
            elif stat and stat.get('status') == 'failure':
                yield self.notify(notify_url, 2, 'fail to solve', userinfo)
                return
            else:
                count += 1
                if count == 10:
                    i = 15
                elif count > 20:
                    yield self.notify(notify_url, 2, 'fail to solve', userinfo)
                    return
                yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + i)

    @tornado.gen.coroutine
    def send_request(self, service, args=None, retry=0, retry_limit=1):
        if retry > retry_limit:
            raise tornado.gen.Return(None)

        if self.session and args:
            args.update({'session': self.session})
        json_data = json.dumps(args or {})
        url = consts.astrometry_net_api_url + service
        print 'Sending to URL:', url
        print 'Sending json:', json_data

        headers = tornado.httputil.HTTPHeaders(
            {"content-type": "application/x-www-form-urlencoded"})
        body = urllib.urlencode({'request-json': json_data})

        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            url=url, method='POST', headers=headers, body=body, connect_timeout=30, request_timeout=120)
        sys.stdout.flush()
        try:
            response = yield client.fetch(request)
        except tornado.web.HTTPError:
            response = yield self.send_request(service, args, retry + 1, retry_limit)
            raise tornado.gen.Return(response)
        if response.code == 200:
            raise tornado.gen.Return(json.loads(response.body))
        else:
            response = yield self.send_request(service, args, retry + 1, retry_limit)
            raise tornado.gen.Return(response)

    @tornado.gen.coroutine
    def login(self):
        args = {'apikey': consts.astrometry_net_api_key}
        result = yield self.send_request('login', args)
        if not result:
            raise tornado.gen.Return(None)
        if result.get('status') == 'success':
            raise tornado.gen.Return(result.get('session'))
        else:
            print 'Bad apikey'
            raise tornado.gen.Return(None)

    @tornado.gen.coroutine
    def url_upload(self, url):
        if not self.session:
            self.session = yield self.login()
        if not self.session:
            raise tornado.gen.Return(None)

        args = dict(url=url,
                    allow_commercial_use='d',
                    allow_modifications='d',
                    publicly_visible='n')
        result = yield self.send_request('url_upload', args)
        if not result:
            raise tornado.gen.Return(None)
        if result.get('status') == 'success':
            raise tornado.gen.Return(result.get('subid'))
        elif result.get('errormessage') and result.get('errormessage').startswith('no'):
            self.session = yield self.login()
            if not self.session:
                raise tornado.gen.Return(None)
            else:
                result = yield self.send_request('url_upload', args)
                if not result:
                    raise tornado.gen.Return(None)
                else:
                    raise tornado.gen.Return(result.get('subid'))
        else:
            raise tornado.gen.Return(None)

    @tornado.gen.coroutine
    def job_status(self, job_id):
        result = yield self.send_request('jobs/%s' % job_id)
        if result and result.get('status') == 'success':
            info = yield self.send_request('jobs/%s/info' % job_id)
            if info:
                info['jobid'] = job_id
                raise tornado.gen.Return(info)
            else:
                tornado.gen.Return(None)
        else:
            raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def sub_status(self, sub_id):
        result = yield self.send_request('submissions/%s' % sub_id)
        raise tornado.gen.Return(result)
