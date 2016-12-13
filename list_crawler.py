#! /usr/bin/env python3
# -*- coding:utf-8

import requests
from bs4 import BeautifulSoup
import datetime
import random
import logging
import json
import re

import config

random.seed(datetime.datetime.now())

_PreURLPattern = re.compile(r"((?:http://)?gz.lianjia.com)?")


def get_items_in_page(bs_obj, out_q=None, callback=None):
    item_nodes = bs_obj.findAll("li", {"class": "clear"})
    logging.debug("抓取到%s条数据" % len(item_nodes))
    for item_node in item_nodes:
        try:
            container = item_node.find("div", {"class": "info clear"})
            title_node = container.find("div", {"class": "title"}).find("a")
            title = title_node.get_text()
            detail_page_link = title_node.attrs["href"]
            detail_page_link = _PreURLPattern.sub("", detail_page_link)

            row = (detail_page_link, title)
            logging.debug(row)
            if out_q:
                out_q.put(row)
            if callback:
                callback(detail_page_link, title)
        except AttributeError:
            pass
    return len(item_nodes)


def _get_next_page_link(bs_obj):
    try:
        list_page_box = bs_obj.find("div", {"class": "page-box house-lst-page-box"})
        page_info = json.loads(list_page_box.attrs["page-data"])
        if page_info["totalPage"] == page_info["curPage"]:
            return None
        else:
            next_page = page_info["curPage"] + 1
            return "/ershoufang/pg%s" % next_page
    except (AttributeError, KeyError):
        pass


def get_items(sentinel, out_q=None, callback=None):
    """
    从目标网站抓取item列表
    :param sentinel: 标示数据结束的哨兵值
    :param out_q:　用于存储输出结果的数据结构，必须实现put()方法
    :param callback:　针对每一条房源记录的回调函数
    :return: 所抓取的条目数量
    """
    host = config.host
    headers = config.headers
    proxies = config.proxies
    first_page = config.first_page
    page = first_page
    house_cnt = 0
    retry_cnt = config.retry_cnt

    while page:
        logging.info("开始抓取页面: %s" % page)
        try:
            response = requests.get(url="http://"+host+page,
                                    headers=headers,
                                    proxies=proxies)
            if response.status_code != 200:
                if retry_cnt>0:
                    logging.warning("获取列表页失败，最多再尝试%s次"
                                    % retry_cnt)
                    retry_cnt -= 1
                    continue
                else:
                    break

            bs_obj = BeautifulSoup(response.content, "lxml")
            new_items_cnt = get_items_in_page(bs_obj,
                                              out_q=out_q,
                                              callback=callback)
            house_cnt += new_items_cnt
            next_page = _get_next_page_link(bs_obj)
            if next_page is None or page == next_page:
                if retry_cnt>0:
                    logging.warning("获取列表页失败，最多再尝试%s次"
                                    % retry_cnt)
                    retry_cnt -= 1
                    continue
                else:
                    break
            page = next_page
            retry_cnt = config.retry_cnt
        except requests.exceptions.ConnectionError:
            pass

    logging.info("抓取结束，一共获得%s条房源信息" % house_cnt)
    if out_q:
        out_q.put(sentinel)
    return house_cnt


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    from queue import Queue
    from threading import Thread

    q = Queue()
    sentinel = object()

    def consumer(sentinel, in_q):
        while True:
            data = in_q.get()
            print(data)
            if data is sentinel:
                break


    t1 = Thread(target=get_items, args=(sentinel, q))
    t2 = Thread(target=consumer, args=(sentinel, q))
    t1.start()
    t2.start()
