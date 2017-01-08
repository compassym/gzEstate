#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from queue import Queue

import config
import list_crawler
import detail_crawler
import tools


_ThreadPool = ThreadPoolExecutor(1)

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


def _crawl(db_file, first_page):
    sentinel = object()
    buffer = Queue()
    list_crawler_thread = Thread(target=list_crawler.get_items,
                                 kwargs={"sentinel": sentinel,
                                         "first_page": first_page,
                                         "out_q": buffer,
                                         "callback": None,
                                         })
    detail_crawler_threads = [Thread(target=consumer_of_thread,
                                     args=(buffer, sentinel))
                              for _ in range(config.cnt_of_worker) ]
    list_crawler_thread.start()
    for t in detail_crawler_threads:
        t.start()

    logging.debug("爬虫工作中...")
    list_crawler_thread.join()
    logging.debug("房源列表爬取结束")
    for t in detail_crawler_threads:
        t.join()

def _crawl_data2_discrete_db(towns, city):
    db_files = []
    for town in towns:
        db_file = detail_crawler.init_db(town=town, city=city)
        first_page = tools.first_page(town)
        if db_file:
            _crawl(db_file, first_page)
            db_files.append(db_file)
    return db_files

def _crawl_data2_lump_db(towns, city):
    db_file = detail_crawler.init_db(town=None, city=city)
    if db_file:
        for town in towns:
            first_page = tools.first_page(town)
            _crawl(db_file, first_page)
        return [db_file]


def crawl(towns, city, discrete=True):
    if discrete:
        return _crawl_data2_discrete_db(towns, city)
    else:
        return _crawl_data2_lump_db(towns, city)

