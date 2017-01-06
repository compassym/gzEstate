# -*- coding:utf-8

import logging

######################################################################
# 目标参数
host = "gz.lianjia.com"
first_page = "/ershoufang/haizhu/pg1"

######################################################################
# 爬虫参数
# HTTP Headers
headers = {
    "Host": host,
    "User-Agent": "Mozilla/5.0(X11;Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Accept": "text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip,deflate",
    "Referer": "http://gz.lianjia.com",
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
    # "http": "socks5://localhost:1080",
    # "https": "socks5://localhost:1080"
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
# 数据存储相关参数
# 用于存储item列表，可供后续采集详细的描述信息提供链接
item_list_file = "./data/item_list.csv"

# 存储所爬取职位信息的数据库文件
db = "haizhu.houses.db"
db_dir = "./data"


######################################################################
# 买家自身特性参数
# 买家是否首套
shoutao = True