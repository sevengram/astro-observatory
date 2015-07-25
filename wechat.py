# -*- coding: utf-8 -*-

import re
import urllib
import time
import json
import logging
from collections import defaultdict

import tornado.gen
import tornado.httpclient
import tornado.curl_httpclient

from util.web import BaseHandler
from storage import mongo_conn, astro_storage
import consts
import astro

type_dict = defaultdict(lambda: ['default'], {
    'image': ['astrometry'],
    'location': ['weather1'],
    'text': ['command', 'constellation', 'deepsky', 'solar', 'weather2', 'default'],
    'event': ['welcome']
})


@tornado.gen.coroutine
def process_welcome(req):
    resp = {
        'msg_type': 'text',
        'content': consts.welcome_direction,
        'tag': 'welcome'
    }
    raise tornado.gen.Return(resp)


@tornado.gen.coroutine
def process_command(req):
    resp = None
    if req.get('content') in consts.text_commands:
        cmd = consts.text_commands[req['content']]
    else:
        cmd = req.get('content')
    if cmd and len(cmd) == 1 and '0' <= cmd <= '9':
        history = astro_storage.get_last_query(req['openid'])
        if history and not history['last_status'] and history['last_query'] and cmd == '1':
            req['content'] = history['last_query']
            req['msg_type'] = 'text'
            req['is_location'] = 1
            resp = yield process_weather2(req)
        if not resp:
            resp = {
                'msg_type': 'text',
                'content': consts.command_dicts[cmd],
                'tag': 'command'
            }
    raise tornado.gen.Return(resp)


@tornado.gen.coroutine
def process_default(req):
    if req.get('content'):
        msg = consts.default_format % req['content']
    else:
        msg = consts.default_response
    resp = {
        'msg_type': 'text',
        'content': msg,
        'tag': 'default'
    }
    raise tornado.gen.Return(resp)


@tornado.gen.coroutine
def process_constellation(req):
    query = req.get('content')
    result = yield mongo_conn.find_constellation(query)
    resp = None
    if result:
        article = result.get('article', '')[:100] + u'...(来自维基百科)'
        resp = {
            'msg_type': 'news',
            'tag': 'constellation',
            'articles': [
                {
                    'title': result.get('chinese', ''),
                    'description': article,
                    'picurl': result.get('image', ''),
                    'url': result.get('wiki', '')
                }
            ]
        }
    raise tornado.gen.Return(resp)


@tornado.gen.coroutine
def process_solar(req):
    query = req.get('content')
    result = yield mongo_conn.find_solar(query)
    resp = None
    if result:
        target_url = result.get('cn_wiki', '') if u'\u4e00' <= query[0] <= u'\u9fa5' else result.get('en_wiki', '')
        article = result.get('article', '')[:100] + u'...(来自维基百科)'
        resp = {
            'msg_type': 'news',
            'tag': 'constellation',
            'articles': [
                {
                    'title': result.get('chinese', ''),
                    'description': article,
                    'picurl': result.get('image', ''),
                    'url': target_url
                }
            ]
        }
    raise tornado.gen.Return(resp)


@tornado.gen.coroutine
def process_deepsky(req):
    query = req.get('content', '')
    match = re.search('\d', query)
    usetitle = match and query[:match.start()].strip().lower() in [
        'messier', 'caldwell', 'abell', 'stock', 'berk', 'arp', 'cr', 'tr', 'sh']
    query = query.title() if usetitle else query.upper()
    querys = [query, query.replace(' ', '')] if ' ' in query else [query]
    resp = None
    for q in querys:
        result = yield mongo_conn.find_deepsky(q)
        if result:
            objname = result.get('object', '')
            title = objname + ' - %s' % result['cn_name'] if 'cn_name' in result else objname
            match = re.search('\d', objname)
            if match:
                i = match.start()
                if u'\u4e00' <= query[0] <= u'\u9fa5':
                    target_url = 'http://zh.m.wikipedia.org/zh-cn/%s' % '_'.join([objname[:i], objname[i:]])
                else:
                    target_url = 'http://en.m.wikipedia.org/wiki/%s' % '_'.join([objname[:i], objname[i:]])
            else:
                target_url = ''
            resp = {
                'msg_type': 'news',
                'tag': 'constellation',
                'articles': [
                    {
                        'title': title,
                        'description': astro.get_description(result),
                        'picurl': result.get('image', ''),
                        'url': target_url
                    }
                ]
            }
            break
    raise tornado.gen.Return(resp)


@tornado.gen.coroutine
def get_location(query):
    query = query.encode('utf-8')
    client = tornado.curl_httpclient.CurlAsyncHTTPClient()
    map_url = "http://maps.googleapis.com/maps/api/geocode/json?" + urllib.urlencode(
        {'address': query, 'sensor': 'false', 'language': 'zh-CN'})
    locreq = tornado.httpclient.HTTPRequest(
        url=map_url, connect_timeout=20, proxy_host='192.110.165.49', proxy_port=8180, request_timeout=20)
    locres = yield client.fetch(locreq)
    resp = None
    if locres.code == 200:
        try:
            report = json.loads(locres.body)
            if report['status'] == 'OK':
                result = report['results'][0]
                label = result['formatted_address']
                lng = result['geometry']['location']['lng']
                lat = result['geometry']['location']['lat']
                resp = {'query': query, 'address': label, 'longitude': lng, 'latitude': lat}
        except KeyError:
            logging.warning('invalid resp from google geo api')
    raise tornado.gen.Return(resp)


@tornado.gen.coroutine
def process_weather1(request):
    img_url = consts.seventimer_url + '?' + urllib.urlencode(
        {'lon': request['longitude'], 'lat': request['latitude'], 'lang': 'zh-CN', 'time': int(time.time())})
    resp = {
        'msg_type': 'news',
        'tag': 'weather',
        'articles': [
            {
                'title': request.get('label', ''),
                'description': u'数据来自晴天钟(7timer.com)',
                'picurl': img_url,
                'url': img_url
            }
        ]
    }
    raise tornado.gen.Return(resp)


@tornado.gen.coroutine
def process_weather2(request):
    query = request.get('content', '')
    if len(query) < 2:
        raise tornado.gen.Return(None)
    resp = None
    is_location = request.get('is_location') == 1
    location = astro_storage.get_location(query)
    if not location and not is_location:
        for word in consts.loc_keys:
            if word in query:
                is_location = True
                break
    if not location and is_location:
        location = yield get_location(query)
        if location:
            astro_storage.add_location(location)
    if location:
        img_url = consts.seventimer_url + '?' + urllib.urlencode(
            {'lon': location['longitude'], 'lat': location['latitude'], 'lang': 'zh-CN',
             'time': int(time.time())})
        resp = {
            'msg_type': 'news',
            'tag': 'weather',
            'articles': [
                {
                    'title': location.get('address', ''),
                    'description': u'数据来自晴天钟(7timer.com)',
                    'picurl': img_url,
                    'url': img_url
                }
            ]
        }
    raise tornado.gen.Return(resp)


process_dict = {
    'constellation': process_constellation,
    'command': process_command,
    'weather1': process_weather1,
    'weather2': process_weather2,
    'deepsky': process_deepsky,
    'solar': process_solar,
    'default': process_default,
    'welcome': process_welcome,
    # 'astrometry': process_astrometry
}


class MsgHandler(BaseHandler):
    @tornado.gen.coroutine
    def prepare(self):
        if self.sign_check:
            self.check_signature({k: v[0] for k, v in self.request.arguments.iteritems() if v},
                                 sign_key='cee02b3226ac33fc254071832d099102',
                                 method='md5')

    @tornado.gen.coroutine
    def post(self):
        msg_data = self.assign_arguments(
            essential=['appid', 'openid', 'msg_type', 'msg_time', 'msg_id'],
            extra=[('content', ''),
                   ('pic_url', ''),
                   ('media_id', ''),
                   ('longitude', None),
                   ('latitude', None),
                   ('label', ''),
                   ('event_type', '')]
        )
        resp = None
        processed = False
        for p in type_dict[msg_data['msg_type']]:
            if p in process_dict:
                resp = yield process_dict.get(p)(msg_data)
                if resp:
                    processed = (p != 'default')
                    break
        if resp:
            post_resp_data = resp
            self.send_response(post_resp_data)
        else:
            self.send_response(err_code=1)
        astro_storage.add_user_record(
            {'openid': msg_data['openid'], 'last_query': msg_data.get('content'), 'last_status': 1 if processed else 0})
