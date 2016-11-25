# -*- coding:utf-8

import logging

host = "www.neitui.me"
first_page = "/?name=neitui&handle=lists&fr=search&keyword=&kcity=%E5%B9%BF%E5%B7%9E"

headers = {
    "Host": host,
    "User-Agent": "Mozilla/5.0(X11;Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Accept": "text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip,deflate",
    "Referer": "http://www.neitui.me",
    "Cookie": "PHPSESSID=aa5aa357ae30130dbe38d1dc3dd69517; search_city=%E5%9F%8E%E5%B8%82; gr_user_id=2f050123-d3aa-426f-a0b6-39e3d78f35ab; gr_session_id_8593d48fe0be173e=60ecd8c2-fb63-40cf-8b1e-7ba399704621; Hm_lvt_21de977c0eb6fd0c491abddcb289ff96=1477832275; Hm_lpvt_21de977c0eb6fd0c491abddcb289ff96=1477832275; __NEITUI_CITY_LOG_STAMP__=%u5E7F%u5DDE"
}


proxies = {
    "http": "socks5://localhost:1080",
    "https": "socks5://localhost:1080"
}

# 用于存储job列表，包括enterprise(公司)，职位(job)，对应的链接地址(link)三列
# 可供后续采集详细的职位描述信息提供链接
job_list_file = "./data/job_list.csv"


# 日志系统配置
log_dir = "./log"
log_format = "%(asctime)s %(levelname)s: %(message)s"
log_level = logging.DEBUG

# 存储所爬取职位信息的数据库文件
db = "job_list.db"
db_dir = "./data"
