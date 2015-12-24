#! /usr/bin/env python2
# -*- coding:utf8 -*-

import json
import logging
import datetime
import re
import time

import tornado.web
import tornado.httpclient
from bs4 import BeautifulSoup

import consts
from util import http, security

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def replace_blanks(text):
    t = text.strip().replace('\n', '').replace('\r', '').replace('\t', '').replace(u'\uff1b', '; ').replace(
        u'\uff1f', '? ').replace(u'\uff0c', ', ').replace(u'\uff0e', '').replace(u'\uff1a', ': ').replace(
        u'\uff01', '! ').replace(u'\u3002', '. ').replace(u'\u2500', '--').replace('(', ' (').replace(
        ')', ') ').replace(':', ': ')
    return re.sub('\s+', ' ', t)


def fetch_apod():
    date = datetime.datetime.now().strftime('%y%m%d')
    cn_url = consts.apod_cn_base_url % date
    en_url = consts.apod_en_base_url % date
    try:
        resp = http.get_dict_sync(url=cn_url)
        data = BeautifulSoup(resp.body)
        title = replace_blanks(data.find_all('center')[1].find('b').text)
        author = replace_blanks(data.find_all('center')[1].text).replace(title, '').strip()
        article = replace_blanks(
            '\n'.join([p.text for p in data.find('body').findChildren(
                name='p', recursive=False)]).replace(u'\u8aaa\u660e:', ''))
        t = data.find_all('center')[-1].text
        translate = replace_blanks(t[t.find(u'\u7ffb\u8b6f'):])
        picurl = consts.apod_pic_base_url + data.find('center').find('img').get('src')
        res = {'title': title, 'article': article, 'author': author, 'translate': translate, 'picurl': picurl,
               'cn_url': cn_url, 'en_url': en_url}
        logging.info('finish to fetch apod: %s', res)
        return res
    except AttributeError:
        logging.error('fail to fetch apod: parse error')
        return None
    except tornado.web.HTTPError:
        logging.error('fail to fetch apod: http error')
        return None


def upload_news(data):
    data = {
        'appid': consts.appid,
        'title': (u'[每日天文一圖] ' + data['title']).encode('utf-8'),
        'content': (
            u'<p><strong>%s</strong></p>'
            u'<p><strong>%s</strong></p>'
            u'<p><br/></p>'
            u'<p>%s</p>'
            u'<p><br/></p>'
            u'<p><strong>资料来自:</strong></p>'
            u'<p>%s</p><p>%s</p><p><br/></p>'
            u'<p style="color: rgb(37, 79, 130);"><strong>---------------</strong></p>'
            u'<p style="color: rgb(54, 96, 146);"><strong>欢迎关注邻家天文馆, 这里有什么好玩的呢?</strong></p>'
            u'<p style="color: rgb(71, 113, 162);"><strong>1.从晴天钟获取天气预报</strong></p>'
            u'<p style="color: rgb(89, 129, 178);"><strong>2.查询全天88星座</strong></p>'
            u'<p style="color: rgb(106, 145, 194);"><strong>3.查询超过3万个深空天体</strong></p>'
            u'<p style="color: rgb(124, 162, 210);"><strong>4.解析星空照片</strong></p>'
            u'<p style="color: rgb(141, 179, 226);"><strong>如需详细帮助, 请回复对应数字.</strong></p>' % (
                data['author'], data['translate'], data['article'], data['en_url'], data['cn_url'])).encode('utf-8'),
        'picurl': data['picurl'], 'source_url': data['cn_url'],
        'digest': (data['article'][:100] + '...').encode('utf-8')}
    security.add_sign(data, consts.sitekey)
    resp = http.post_dict_sync(url=consts.wechat_news_url, data=data)
    if resp.code != 200:
        logging.error('fail to upload material')
        return False
    else:
        resp_data = json.loads(resp.body)
        if resp_data['err_code'] != 0:
            logging.error('fail to upload material: %s: %s', resp_data['err_code'], resp_data['err_msg'])
            return False
        else:
            logging.info('finish to upload material')
            return True


def get_lastest_news():
    data = {'appid': consts.appid}
    security.add_sign(data, consts.sitekey)
    resp = http.get_dict_sync(url=consts.wechat_news_url, data=data)
    if resp.code != 200:
        logging.error('fail to get lastest news')
        return None
    else:
        resp_data = json.loads(resp.body)
        if resp_data['err_code'] != 0:
            logging.error('fail to get lastest news: %s: %s', resp_data['err_code'], resp_data['err_msg'])
            return None
        else:
            logging.info('finish to get lastest news: %s', resp_data['data'])
            return resp_data['data']


def send_message(appmsgid):
    data = {
        'appid': consts.appid,
        'appmsgid': appmsgid
    }
    security.add_sign(data, consts.sitekey)
    resp = http.post_dict_sync(url=consts.wechat_multimsgs_url, data=data)
    if resp.code != 200:
        logging.error('fail to send msg')
        return False
    else:
        resp_data = json.loads(resp.body)
        if resp_data['err_code'] != 0:
            logging.error('fail to send msg: %s: %s', resp_data['err_code'], resp_data['err_msg'])
            return False
        else:
            logging.info('finish to send msg')
            return True


if __name__ == "__main__":
    limit = 5

    result = None
    for i in range(limit):
        logging.info('fetch apod...%d', i)
        result = fetch_apod()
        if result:
            break
        else:
            time.sleep(60)
    if not result:
        exit(1)

    msgid = None
    for i in range(limit):
        logging.info('upload news...%d', i)
        result = upload_news(result)
        if result:
            time.sleep(300)
            news = get_lastest_news()
            if time.time() - int(news['create_time']) < 1800:
                msgid = str(news['app_id'])
                break
        else:
            time.sleep(60)

    if not msgid:
        exit(1)
    for i in range(limit):
        logging.info('send message...%d', i)
        if send_message(msgid):
            break
        else:
            time.sleep(60)
