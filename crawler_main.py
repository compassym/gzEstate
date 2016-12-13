#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
import os
from concurrent.futures import ThreadPoolExecutor

import config
import list_crawler
import detail_crawler
import tools


_ThreadPool = ThreadPoolExecutor(1)

def log_setting():
    if tools.check_dir(config.log_dir):
        log_file = os.path.join(config.log_dir, "log.txt")
        logging.basicConfig(level=config.log_level,
                            format=config.log_format,
                            filename=log_file
                            )
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger('').addHandler(console)
    else:
        logging.basicConfig(level=config.log_level,
                            format=config.log_format)

def consumer(page_link, title):
    global _ThreadPool
    future = _ThreadPool.submit(detail_crawler.get_detail,
                                page_link, title)
    future.add_done_callback(detail_crawler.write2db)


def main():
    log_setting()

    sentinel = object()
    detail_crawler.create_db()
    cnt = list_crawler.get_items(sentinel=sentinel, callback=consumer)
    logging.info("抓取结束，一共获得%s条房源信息" % cnt)


main()