# -*- coding:utf8 -*-

from collections import defaultdict

cons = defaultdict(
    lambda: '?', {
        'AND': u'仙女座',
        'ANT': u'唧筒座',
        'APS': u'天燕座',
        'AQR': u'宝瓶座',
        'AQL': u'天鹰座',
        'ARA': u'天坛座',
        'ARI': u'白羊座',
        'AUR': u'御夫座',
        'BOO': u'牧夫座',
        'CAE': u'雕具座',
        'CAM': u'鹿豹座',
        'CNC': u'巨蟹座',
        'CVN': u'猎犬座',
        'CMA': u'大犬座',
        'CMI': u'小犬座',
        'CAP': u'摩羯座',
        'CAR': u'船底座',
        'CAS': u'仙后座',
        'CEN': u'半人马座',
        'CEP': u'仙王座',
        'CET': u'鲸鱼座',
        'CHA': u'蝘蜓座',
        'CIR': u'圆规座',
        'COL': u'天鸽座',
        'COM': u'后发座',
        'CRA': u'南冕座',
        'CRB': u'北冕座',
        'CRV': u'乌鸦座',
        'CRT': u'巨爵座',
        'CRU': u'南十字座',
        'CYG': u'天鹅座',
        'DEL': u'海豚座',
        'DOR': u'剑鱼座',
        'DRA': u'天龙座',
        'EQU': u'小马座',
        'ERI': u'波江座',
        'FOR': u'天炉座',
        'GEM': u'双子座',
        'GRU': u'天鹤座',
        'HER': u'武仙座',
        'HOR': u'时钟座',
        'HYA': u'长蛇座',
        'HYI': u'水蛇座',
        'IND': u'印第安座',
        'LAC': u'蝎虎座',
        'LEO': u'狮子座',
        'LMI': u'小狮座',
        'LEP': u'天兔座',
        'LIB': u'天秤座',
        'LUP': u'豺狼座',
        'LYN': u'天猫座',
        'LYR': u'天琴座',
        'MEN': u'山案座',
        'MIC': u'显微镜座',
        'MON': u'麒麟座',
        'MUS': u'苍蝇座',
        'NOR': u'矩尺座',
        'OCT': u'南极座',
        'OPH': u'蛇夫座',
        'ORI': u'猎户座',
        'PAV': u'孔雀座',
        'PEG': u'飞马座',
        'PER': u'英仙座',
        'PHE': u'凤凰座',
        'PIC': u'绘架座',
        'PSC': u'双鱼座',
        'PSA': u'南鱼座',
        'PUP': u'船尾座',
        'PYX': u'罗盘座',
        'RET': u'网罟座',
        'SGE': u'天箭座',
        'SGR': u'人马座',
        'SCO': u'天蝎座',
        'SCL': u'玉夫座',
        'SCT': u'盾牌座',
        'SER': u'巨蛇座',
        'SEX': u'六分仪座',
        'TAU': u'金牛座',
        'TEL': u'望远镜座',
        'TRI': u'三角座',
        'TRA': u'南三角座',
        'TUC': u'杜鹃座',
        'UMA': u'大熊座',
        'UMI': u'小熊座',
        'VEL': u'船帆座',
        'VIR': u'室女座',
        'VOL': u'飞鱼座',
        'VUL': u'狐狸座',
    })

types = {'ASTER': u'星群',
         'BRTNB': u'星云',
         'CL+NB': u'星云及其附属星团',
         'DRKNB': u'暗星云',
         'GALCL': u'星系团',
         'GALXY': u'星系',
         'GLOCL': u'球状星团',
         'GX+DN': u'星云, 位于河外星系中',
         'GX+GC': u'球状星团, 位于河外星系中',
         'G+C+N': u'星云及其附属星团, 位于河外星系中',
         'LMCCN': u'星云及其附属星团, 位于大麦哲伦星云中',
         'LMCDN': u'星云, 位于大麦哲伦星云中',
         'LMCGC': u'球状星团, 位于大麦哲伦星云中',
         'LMCOC': u'疏散星团, 位于大麦哲伦星云中',
         'OPNCL': u'疏散星团',
         'PLNNB': u'行星状星云',
         'SMCDN': u'星云, 位于小麦哲伦星云中',
         'SMCCN': u'星云及其附属星团, 位于小麦哲伦星云中',
         'SMCGC': u'球状星团, 位于小麦哲伦星云中',
         'SMCOC': u'疏散星团, 位于小麦哲伦星云中',
         'SNREM': u'超新星遗迹',
         'QUASR': u'类星体',
         '2STAR': u'双星',
         '3STAR': u'三合星',
         '4STAR': u'四合星',
         '8STAR': u'八合星'}


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
                desc = u'棒旋'
            elif galclass[0] == 'S':
                desc = u'旋涡'
            elif galclass[0] == 'E':
                desc = u'椭圆'
            elif galclass[0] == 'I':
                desc = u'不规则'
        article += u'是位于%s的%s%s. ' % (chinese_con, desc, types[info['type']])
    else:
        article += u'位于%s. ' % chinese_con
    if info.get('ra'):
        ras = info['ra'].split()
        f = u'赤经 %sh%sm' if len(ras) == 2 else u'赤经 %sh%sm%ss'
        article += f % tuple(ras)
    if info.get('dec'):
        decs = info['dec'].split()
        f = u', 赤纬 %s°%s\'' if len(decs) == 2 else u', 赤纬 %s°%s\'%s"'
        article += f % tuple(decs)
    if info.get('mag') and info['mag'] < 30:
        article += u', 视星等 %+.2f' % info['mag']
    if info.get('size'):
        article += u', 视面积 %s' % info['size']

    article += '.'
    return article
