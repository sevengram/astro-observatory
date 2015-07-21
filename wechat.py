# -*- coding: utf-8 -*-

import re
from collections import defaultdict

import tornado.gen

from util.web import BaseHandler
import consts
import motordb
import astro

mongo_conn = motordb.Connector(debug=False)

type_dict = defaultdict(lambda: ['default'], {
    'image': ['astrometry'],
    'location': ['weather1'],
    'text': ['command', 'constellation', 'deepsky', 'solar', 'weather1', 'weather2', 'default'],
    'event': ['welcome']
})


@tornado.gen.coroutine
def process_welcome(req):
    res = {
        'msg_type': 'text',
        'content': consts.welcome_direction,
        'tag': 'welcome'
    }
    raise tornado.gen.Return(res)


@tornado.gen.coroutine
def process_command(req):
    if req.get('content') in consts.text_commands:
        cmd = consts.text_commands[req['content']]
    else:
        cmd = req.get('content')
    if cmd and len(cmd) == 1 and '0' <= cmd <= '9':
        res = None
        # history = mysql_conn.get_lastquery(request['FromUserName'])
        # if history and not history['last_status'] and history['last_query']:
        #     if cmd == '1':
        #         res = yield process_weather({
        #             'Content': history['last_query'],
        #             'MsgType': 'text',
        #             'FromUserName': request['FromUserName']
        #         })
        #     if not res:
        #         mysql_conn.add_feedback(
        #             {'uid': request['FromUserName'], 'query': history['last_query'], 'type': cmd})
        if res:
            raise tornado.gen.Return(res)
        else:
            res = {
                'msg_type': 'text',
                'content': consts.command_dicts[cmd],
                'tag': 'command'
            }
            raise tornado.gen.Return(res)
    else:
        raise tornado.gen.Return(None)


@tornado.gen.coroutine
def process_default(req):
    if req.get('content'):
        msg = consts.default_format % req['content']
    else:
        msg = consts.default_response
    res = {
        'msg_type': 'text',
        'content': msg,
        'tag': 'default'
    }
    raise tornado.gen.Return(res)


def process_constellation(req):
    query = req.get('content')
    result = yield mongo_conn.find_constellation(query)
    if result:
        article = result.get('article', '')[:100] + u'...(来自维基百科)'
        res = {
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
        raise tornado.gen.Return(res)
    else:
        raise tornado.gen.Return(None)


@tornado.gen.coroutine
def process_solar(req):
    query = req.get('content')
    result = yield mongo_conn.find_solar(query)
    if result:
        target_url = result.get('cn_wiki', '') if u'\u4e00' <= query[0] <= u'\u9fa5' else result.get('en_wiki', '')
        article = result.get('article', '')[:100] + u'...(来自维基百科)'
        res = {
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
        raise tornado.gen.Return(res)
    else:
        raise tornado.gen.Return(None)


@tornado.gen.coroutine
def process_deepsky(req):
    query = req.get('content')
    match = re.search('\d', query)
    usetitle = match and query[:match.start()].strip().lower() in [
        'messier', 'caldwell', 'abell', 'stock', 'berk', 'arp', 'cr', 'tr', 'sh']
    query = query.title() if usetitle else query.upper()
    querys = [query, query.replace(' ', '')] if ' ' in query else [query]
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
            res = {
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
            raise tornado.gen.Return(res)
    raise tornado.gen.Return(None)


process_dict = {
    'constellation': process_constellation,
    'command': process_command,
    # 'weather1': process_weather1,
    # 'weather2': process_weather2,
    'deepsky': process_deepsky,
    'solar': process_solar,
    'default': process_default,
    'welcome': process_welcome,
    # 'astrometry': process_astrometry
}


class MsgHandler(BaseHandler):
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
        # for p in type_dict[msg_data['msg_type']]:
        #     if p in process_dict:
        #         res = yield process_dict.get(p)(msg_data)
        #         if res:
        #             processed = (p != 'default')
        #             break
        post_resp_data = {
            'msg_type': 'text',
            'content': u'系统维护中'
        }
        self.send_response(post_resp_data)

    def get_check_key(self, refer_dict):
        return 'cee02b3226ac33fc254071832d099102'
