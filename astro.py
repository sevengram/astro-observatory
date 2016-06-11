# -*- coding: utf-8 -*-

from collections import defaultdict

cons = defaultdict(
    lambda: '?', {
        'AND': '仙女座',
        'ANT': '唧筒座',
        'APS': '天燕座',
        'AQR': '宝瓶座',
        'AQL': '天鹰座',
        'ARA': '天坛座',
        'ARI': '白羊座',
        'AUR': '御夫座',
        'BOO': '牧夫座',
        'CAE': '雕具座',
        'CAM': '鹿豹座',
        'CNC': '巨蟹座',
        'CVN': '猎犬座',
        'CMA': '大犬座',
        'CMI': '小犬座',
        'CAP': '摩羯座',
        'CAR': '船底座',
        'CAS': '仙后座',
        'CEN': '半人马座',
        'CEP': '仙王座',
        'CET': '鲸鱼座',
        'CHA': '蝘蜓座',
        'CIR': '圆规座',
        'COL': '天鸽座',
        'COM': '后发座',
        'CRA': '南冕座',
        'CRB': '北冕座',
        'CRV': '乌鸦座',
        'CRT': '巨爵座',
        'CR': '南十字座',
        'CYG': '天鹅座',
        'DEL': '海豚座',
        'DOR': '剑鱼座',
        'DRA': '天龙座',
        'EQ': '小马座',
        'ERI': '波江座',
        'FOR': '天炉座',
        'GEM': '双子座',
        'GR': '天鹤座',
        'HER': '武仙座',
        'HOR': '时钟座',
        'HYA': '长蛇座',
        'HYI': '水蛇座',
        'IND': '印第安座',
        'LAC': '蝎虎座',
        'LEO': '狮子座',
        'LMI': '小狮座',
        'LEP': '天兔座',
        'LIB': '天秤座',
        'LUP': '豺狼座',
        'LYN': '天猫座',
        'LYR': '天琴座',
        'MEN': '山案座',
        'MIC': '显微镜座',
        'MON': '麒麟座',
        'MUS': '苍蝇座',
        'NOR': '矩尺座',
        'OCT': '南极座',
        'OPH': '蛇夫座',
        'ORI': '猎户座',
        'PAV': '孔雀座',
        'PEG': '飞马座',
        'PER': '英仙座',
        'PHE': '凤凰座',
        'PIC': '绘架座',
        'PSC': '双鱼座',
        'PSA': '南鱼座',
        'PUP': '船尾座',
        'PYX': '罗盘座',
        'RET': '网罟座',
        'SGE': '天箭座',
        'SGR': '人马座',
        'SCO': '天蝎座',
        'SCL': '玉夫座',
        'SCT': '盾牌座',
        'SER': '巨蛇座',
        'SEX': '六分仪座',
        'TA': '金牛座',
        'TEL': '望远镜座',
        'TRI': '三角座',
        'TRA': '南三角座',
        'TUC': '杜鹃座',
        'UMA': '大熊座',
        'UMI': '小熊座',
        'VEL': '船帆座',
        'VIR': '室女座',
        'VOL': '飞鱼座',
        'VUL': '狐狸座',
    })

types = {'ASTER': '星群',
         'BRTNB': '星云',
         'CL+NB': '星云及其附属星团',
         'DRKNB': '暗星云',
         'GALCL': '星系团',
         'GALXY': '星系',
         'GLOCL': '球状星团',
         'GX+DN': '星云, 位于河外星系中',
         'GX+GC': '球状星团, 位于河外星系中',
         'G+C+N': '星云及其附属星团, 位于河外星系中',
         'LMCCN': '星云及其附属星团, 位于大麦哲伦星云中',
         'LMCDN': '星云, 位于大麦哲伦星云中',
         'LMCGC': '球状星团, 位于大麦哲伦星云中',
         'LMCOC': '疏散星团, 位于大麦哲伦星云中',
         'OPNCL': '疏散星团',
         'PLNNB': '行星状星云',
         'SMCDN': '星云, 位于小麦哲伦星云中',
         'SMCCN': '星云及其附属星团, 位于小麦哲伦星云中',
         'SMCGC': '球状星团, 位于小麦哲伦星云中',
         'SMCOC': '疏散星团, 位于小麦哲伦星云中',
         'SNREM': '超新星遗迹',
         'QUASR': '类星体',
         '2STAR': '双星',
         '3STAR': '三合星',
         '4STAR': '四合星',
         '8STAR': '八合星'}


def alias_filter(alias):
    return not (alias.startswith('Messier') or
                alias.startswith('Caldwell') or
                alias.startswith('PK') or
                alias.startswith('PGC') or
                alias.startswith('ESO') or
                alias.startswith('NPM') or
                alias.startswith('CGCG') or
                alias.startswith('PNG') or
                alias.startswith('CS') or
                alias.startswith('VV') or
                alias.startswith('IRAS') or
                alias.startswith('KCPG') or
                alias.startswith('MCG'))


def get_description(info):
    article = info['object']
    chinese_con = cons[info['con']] if 'con' in info else '?'
    if 'alias' in info:
        aliases = filter(alias_filter, info['alias'])
        if aliases:
            article += ' ( %s ) ' % ', '.join(aliases)
    if info.get('type') in types:
        desc = ''
        if info['type'] == 'GALXY' and info.get('class'):
            galclass = info['class']
            if galclass.startswith('SB'):
                desc = '棒旋'
            elif galclass[0] == 'S':
                desc = '旋涡'
            elif galclass[0] == 'E':
                desc = '椭圆'
            elif galclass[0] == 'I':
                desc = '不规则'
        article += '是位于%s的%s%s. ' % (chinese_con, desc, types[info['type']])
    else:
        article += '位于%s. ' % chinese_con
    if info.get('ra'):
        ras = info['ra'].split()
        f = '赤经 %sh%sm' if len(ras) == 2 else '赤经 %sh%sm%ss'
        article += f % tuple(ras)
    if info.get('dec'):
        decs = info['dec'].split()
        f = ', 赤纬 %s°%s\'' if len(decs) == 2 else ', 赤纬 %s°%s\'%s"'
        article += f % tuple(decs)
    if info.get('mag') and info['mag'] < 30:
        article += ', 视星等 %+.2f' % info['mag']
    if info.get('size'):
        article += ', 视面积 %s' % info['size']

    article += '.'
    return article
