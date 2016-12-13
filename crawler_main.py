#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from queue import Queue

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

def consumer_of_pool(page_link, title):
    global _ThreadPool
    future = _ThreadPool.submit(detail_crawler.get_detail,
                                page_link, title)
    future.add_done_callback(detail_crawler.write2db_for_pool_callback)


def consumer_of_thread(in_q, sentinel):
    while True:
        row = in_q.get()
        if row is sentinel:
            return
        page_link, title = row
        detail = detail_crawler.get_detail(page_link, title)
        detail_crawler.write2db(detail)


def main():
    log_setting()

    sentinel = object()
    buffer = Queue()
    detail_crawler.create_db()
    list_crawler_thread = Thread(target=list_crawler.get_items,
                                 kwargs={"sentinel": sentinel,
                                         "out_q": buffer,
                                         "callback": None
                                         })
    detail_crawler_threads = [Thread(target=consumer_of_thread,
                                     args=(buffer, sentinel))
                                for _ in range(config.cnt_of_worker) ]
    list_crawler_thread.start()
    for t in detail_crawler_threads:
        t.start()

    list_crawler_thread.join()
    for t in detail_crawler_threads:
        t.join()



main()