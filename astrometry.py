# -*- coding:utf8 -*-

import json
import time
import logging

import tornado.gen
import tornado.httpclient
import tornado.httputil
import tornado.web
import tornado.ioloop

import consts
from util import security, http
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
    def notify(self, status, message, openid):
        # TODO: notify wechat api
        req_data = {'appid': consts.appid,
                    'openid': openid,
                    'msg_type': 'text'}
        if status == 0:
            req_data['content'] = message
        elif status == 1:
            req_data['content'] = consts.image_data_err_msg
        elif status == 2:
            req_data['content'] = consts.image_resolution_err_msg
        else:
            req_data['content'] = consts.image_fail_err_msg
        security.add_sign(req_data, consts.sitekey)
        response = yield http.post_dict(url=consts.wechat_msgs_url, data=req_data)
        logging.info('notify result: %s', response.body)
        raise tornado.gen.Return(response)

    @tornado.gen.coroutine
    def post(self):
        pic_url = self.get_argument('pic_url')
        openid = self.get_argument('openid')
        self.send_response(err_code=0, err_msg='ok')

        subid = yield self.url_upload(pic_url)
        if not subid:
            yield self.notify(1, 'submission error', openid)
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
                yield self.notify(2, 'pic reduce error', openid)
                return
            yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + i)

        yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + 5)
        count, i = 0, 5
        while True:
            stat = yield self.job_status(jobid)
            if stat and stat.get('status') == 'success':
                yield self.notify(0, build_reply(stat), openid)
                return
            elif stat and stat.get('status') == 'failure':
                yield self.notify(3, 'fail to solve', openid)
                return
            else:
                count += 1
                if count == 10:
                    i = 15
                elif count > 20:
                    yield self.notify(3, 'fail to solve', openid)
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
        logging.info('Sending to URL: %s', url)
        logging.info('Sending json: %s', json_data)
        try:
            response = yield http.post_dict(url=url, data={'request-json': json_data})
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
            logging.error('Bad apikey')
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
