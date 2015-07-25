# -*- coding:utf8 -*-

from collections import defaultdict

seventimer_url = 'http://202.127.24.18/v4/bin/astro.php'

welcome_direction = u'''欢迎来到邻家天文馆! 在这里, 你可以/:?
1. 从晴天钟获取天气预报(输入地名或上传位置)
2. 查询全天88星座(如:白羊座)
3. 查询超过3万个深空天体(如:M42, NGC7000, 蟹状星云)
4. 解析星空照片
如需详细帮助, 请回复对应数字.'''

default_format = u'''"%s"是神马?可以吃吗?/:,@@其实你想查......
1.晴天钟
2.星座
3.深空天体
0.萌妹纸'''

default_response = u'''找不到相应的服务/:,@@其实你想查......
1.晴天钟
2.星座
3.深空天体
0.萌妹纸'''

text_commands = {
    u'天气': '1',
    u'晴天钟': '1',
    u'星座': '2',
    u'深空': '3',
    u'深空天体': '3',
    u'图片': '4',
    u'照片': '4',
    u'解析': '4',
    u'分析': '4',
    u'你好': '9',
    u'帮助': '9',
    u'怎么用': '9',
    'Help': '9',
    'help': '9',
    'hello': '9',
    'Hi': '9',
    'hi': '9',
}

command_dicts = defaultdict(lambda: u'找不到这个指令哦', {
    '1': u'怎么查晴天钟呢? 随便挑一种办法吧!\n'
    u'1.点击文本输入栏旁边的加号, 选择位置并发送\n'
    u'2.直接发送地名(加上"省市区县"这样的字能提高识别率哦)',
    '2': u'直接输入星座名称就可以啦, 比如"白羊座", "巨蟹"',
    '3': u'想在30000+深空天体中漫游么? 你可以输入编号查询, 如:M42, C4, NGC7000; 也可使用名称, 如"仙女座大星系", "加州星云"',
    '4': u'星空解析功能已经火热上线! 直接上传照片获取星空坐标和天体信息! 图像分析来自astrometry.net',
    '0': u'呵呵',
    '9': welcome_direction
})

loc_keys = [
    u'上海',
    u'北京',
    u'广州',
    u'深圳',
    u'苏州',
    u'天津',
    u'重庆',
    u'杭州',
    u'无锡',
    u'青岛',
    u'佛山',
    u'成都',
    u'武汉',
    u'大连',
    u'宁波',
    u'沈阳',
    u'南京',
    u'长沙',
    u'唐山',
    u'烟台',
    u'东莞',
    u'郑州',
    u'济南',
    u'哈尔滨',
    u'泉州',
    u'南通',
    u'石家庄',
    u'长春',
    u'西安',
    u'潍坊',
    u'福州',
    u'常州',
    u'温州',
    u'大庆',
    u'徐州',
    u'淄博',
    u'绍兴',
    u'合肥',
    u'鄂尔多斯',
    u'济宁',
    u'包头',
    u'台州',
    u'临沂',
    u'东营',
    u'邯郸',
    u'洛阳',
    u'嘉兴',
    u'盐城',
    u'扬州',
    u'南昌',
    u'沧州',
    u'鞍山',
    u'昆明',
    u'金华',
    u'厦门',
    u'泰安',
    u'保定',
    u'泰州',
    u'镇江',
    u'南阳',
    u'威海',
    u'呼和浩特',
    u'中山',
    u'吉林',
    u'南宁',
    u'太原',
    u'榆林',
    u'惠州',
    u'德州',
    u'聊城',
    u'滨州',
    u'江门',
    u'宜昌',
    u'岳阳',
    u'襄阳',
    u'茂名',
    u'常德',
    u'衡阳',
    u'湛江',
    u'漳州',
    u'枣庄',
    u'淮安',
    u'廊坊',
    u'许昌',
    u'平顶山',
    u'安阳',
    u'乌鲁木齐',
    u'湖州',
    u'柳州',
    u'株洲',
    u'焦作',
    u'周口',
    u'邢台',
    u'汕头',
    u'珠海',
    u'新乡',
    u'通辽',
    u'菏泽',
    u'连云港',
    u'商丘',
    u'贵阳',
    u'赣州',
    u'清远',
    u'芜湖',
    u'桂林',
    u'松原',
    u'兰州',
    u'咸阳',
    u'信阳',
    u'郴州',
    u'赤峰',
    u'肇庆',
    u'驻马店',
    u'九江',
    u'日照',
    u'宿迁',
    u'揭阳',
    u'曲靖',
    u'营口',
    u'龙岩',
    u'安庆',
    u'宝鸡',
    u'三明',
    u'张家口',
    u'绵阳',
    u'呼伦贝尔',
    u'秦皇岛',
    u'开封',
    u'盘锦',
    u'德阳',
    u'长治',
    u'遵义',
    u'锦州',
    u'上饶',
    u'湘潭',
    u'临汾',
    u'抚顺',
    u'延安',
    u'承德',
    u'三门峡',
    u'宜宾',
    u'宜春',
    u'黄冈',
    u'本溪',
    u'齐齐哈尔',
    u'吕梁',
    u'荆州',
    u'玉林',
    u'南充',
    u'运城',
    u'达州',
    u'莆田',
    u'马鞍山',
    u'渭南',
    u'孝感',
    u'四平',
    u'凉山',
    u'衡水',
    u'牡丹江',
    u'濮阳',
    u'永州',
    u'晋中',
    u'银川',
    u'衢州',
    u'乐山',
    u'十堰',
    u'玉溪',
    u'宁德',
    u'辽阳',
    u'绥化',
    u'晋城',
    u'邵阳',
    u'荆门',
    u'丹东',
    u'南平',
    u'铁岭',
    u'阜阳',
    u'吉安',
    u'泸州',
    u'益阳',
    u'克拉玛依',
    u'滁州',
    u'大同',
    u'内江',
    u'黄石',
    u'韶关',
    u'漯河',
    u'娄底',
    u'六安',
    u'怀化',
    u'朔州',
    u'资阳',
    u'朝阳',
    u'红河',
    u'宿州',
    u'自贡',
    u'丽水',
    u'阳江',
    u'巴音郭楞',
    u'蚌埠',
    u'舟山',
    u'新余',
    u'抚州',
    u'西宁',
    u'通化',
    u'巢湖',
    u'梅州',
    u'阿克苏',
    u'淮南',
    u'巴彦淖尔',
    u'毕节',
    u'锡林郭勒',
    u'海口',
    u'梧州',
    u'乌兰察布',
    u'百色',
    u'潮州',
    u'昌吉',
    u'眉山',
    u'莱芜',
    u'广安',
    u'延边',
    u'葫芦岛',
    u'贵港',
    u'宣城',
    u'攀枝花',
    u'萍乡',
    u'咸宁',
    u'亳州',
    u'佳木斯',
    u'汉中',
    u'钦州',
    u'六盘水',
    u'遂宁',
    u'河源',
    u'大理',
    u'汕尾',
    u'河池',
    u'铜陵',
    u'淮北',
    u'景德镇',
    u'白城',
    u'忻州',
    u'白山',
    u'阳泉',
    u'鹤壁',
    u'鸡西',
    u'伊犁',
    u'辽源',
    u'酒泉',
    u'楚雄',
    u'随州',
    u'北海',
    u'鄂州',
    u'云浮',
    u'乌海',
    u'崇左',
    u'来宾',
    u'昭通',
    u'双鸭山',
    u'喀什',
    u'海西',
    u'阜新',
    u'庆阳',
    u'黔南',
    u'恩施',
    u'鹰潭',
    u'文山',
    u'安康',
    u'黔西南',
    u'广元',
    u'防城港',
    u'黔东南',
    u'白银',
    u'黄山',
    u'阿拉善盟',
    u'七台河',
    u'湘西',
    u'池州',
    u'天水',
    u'塔城',
    u'石嘴山',
    u'贺州',
    u'铜仁',
    u'雅安',
    u'商洛',
    u'巴中',
    u'兴安盟',
    u'黑河',
    u'保山',
    u'鹤岗',
    u'普洱',
    u'张家界',
    u'安顺',
    u'平凉',
    u'三亚',
    u'武威',
    u'临沧',
    u'张掖',
    u'金昌',
    u'吴忠',
    u'伊春',
    u'铜川',
    u'吐鲁番',
    u'嘉峪关',
    u'拉萨',
    u'海东',
    u'陇南',
    u'中卫',
    u'哈密',
    u'西双版纳',
    u'定西',
    u'丽江',
    u'德宏',
    u'阿勒泰',
    u'阿坝',
    u'博尔塔拉',
    u'甘孜',
    u'临夏',
    u'固原',
    u'和田',
    u'大兴安岭',
    u'日喀则',
    u'迪庆',
    u'海南',
    u'甘南',
    u'昌都',
    u'怒江',
    u'海北',
    u'林芝',
    u'山南',
    u'那曲',
    u'黄南',
    u'克孜勒苏',
    u'玉树',
    u'果洛',
    u'阿里',
    u'台北',
    u'新北',
    u'台中',
    u'台南',
    u'高雄',
    u'基隆',
    u'新竹',
    u'嘉义',
    u'桃园',
    u'苗栗',
    u'彰化',
    u'南投',
    u'云林',
    u'嘉义',
    u'屏东',
    u'宜兰',
    u'花莲',
    u'台东',
    u'澎湖',
    u'金门',
    u'连江',
    u'省',
    u'市',
    u'县',
    u'区',
    u'州',
    u'东',
    u'南',
    u'西',
    u'北',
    u'中',
    u'京',
    u'山',
    u'河',
    u'海',
    u'湖',
    u'江',
    u'苏',
    u'宁',
    u'浙',
    u'镇',
    u'乡',
    u'村',
    u'旗',
    u'盟',
    u'港',
    u'城',
    u'昌',
    u'治',
    u'溪',
    u'浦',
    u'定',
    u'水',
    u'口',
    u'家',
    u'庄',
    u'汇',
    u'岭',
    u'林',
    u'杭',
    u'峰',
    u'津',
    u'滨',
    u'淮',
    u'岗',
    u'岛',
    u'安',
    u'田',
    u'营',
    u'川',
    u'阳',
    u'阴',
    u'萨',
    u'阿',
    u'常',
    u'原',
    u'鲁',
    u'藏',
    u'蒙',
    u'陇',
    u'德',
    u'洛',
    u'汉',
    u'道',
    u'庆',
    u'通',
    u'巴',
    u'都',
    u'金',
    u'关',
    u'界',
    u'锡',
    u'峡',
    u'错',
    u'丘',
    u'泰',
    u'台'
]
