# -*- coding:utf-8

import logging

######################################################################
# 目标参数
# 目标城市，需要自行到链家首页找到对应城市的缩写，
# 如广州链家的网址是"http://gz.lianjia.com"，则广州对应"gz"
city = "gz"
# 目标城市下面的行政区，需要自行到链家网页找到对应行政区的缩写，不要想当然，
# 比如广州黄埔区，对应的url是http://gz.lianjia.com/huangpugz"，
# 因此广州黄浦区对应的是"huangpugz"，而不是"huangpu"，
# 我估计是因为很多城市存在相同名字的行政区的缘故，
#
# 如果towns为空，则一次性抓取city对应城市的所有数据，但是一般不建议这么做，
# 我也不知道怎么回事，链家网站的房源信息最多只能显示100页，每页30个房源，
# 因此如果一次抓取整个城市的话，最多只能抓取3000个左右的房源信息。
# 如果需要将整个城市的房源信息集中处理，可以设置下面的use_single_db为True
towns = ["tianhe", "haizhu", "yuexiu", "liwan", "baiyun", "huangpugz"]

# 存储所爬取数据的数据库文件
db = "houses.db"
db_dir = "./data"
# 将所有区的数据都存储到单一数据库文件并统一处理，
# 如果为False，则每个区单独建立数据库文件，并各自独立处理
use_single_db = True



######################################################################
# 爬虫参数
# HTTP Headers
host = "%s.lianjia.com" % (city,)
headers = {
    "Host": host,
    "User-Agent": "Mozilla/5.0(X11;Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Accept": "text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip,deflate",
    "Referer": "http://%s" % host,
    "Cookie": "select_city=440100; all-lj=75cfc00b9f12050e3970154c91c12727;"
              " lianjia_ssid=4563aa73-3a86-4eea-b5b4-9df0af3beedd; "
              "lianjia_uuid=73f97095-56fa-4716-a585-219125ac851f; "
              "_smt_uid=58381222.b152f5f; "
              "CNZZDATA1255849599=1732419078-1480065634-%7C1480071035; "
              "CNZZDATA1254525948=1030351673-1480066471-%7C1480071871; "
              "CNZZDATA1255633284=2033318703-1480064312-%7C1480069712; "
              "CNZZDATA1255604082=698056229-1480065104-%7C1480070504; "
              "_ga=GA1.2.1290060188.1480069680; _gat=1; _gat_global=1; "
              "_gat_new_global=1; _gat_dianpu_agent=1"
}

# proxies for requests
proxies = {
    "http": "socks5://localhost:1080",
    "https": "socks5://localhost:1080"
}

# proxies for phantomjs
phantomjs_args = [
    "--proxy=localhost:1080",
    "--proxy-type=socks5"
]

# 缓冲区大小
size_of_queue = 90

# 工作线程数量
cnt_of_worker = 6

# 读取列表项错误时的最大重试次数
retry_cnt = 10

######################################################################
# 日志参数
# 日志系统配置
log_dir = "./log"
log_format = "%(asctime)s %(levelname)s: %(message)s"
log_level = logging.DEBUG

######################################################################
# 买家自身特性参数
# 买家是否首套
shoutao = True