#! /usr/bin/env python3
# -*- coding:utf-8

import requests
from bs4 import BeautifulSoup
import time
import datetime
import random
import logging
import json

import config

random.seed(datetime.datetime.now())


def get_items_in_page(bs_obj, out_q=None):
    item_nodes = bs_obj.findAll("li", {"class": "clear"})
    logging.debug("抓取到%s条数据" % len(item_nodes))
    for item_node in item_nodes:
        try:
            container = item_node.find("div", {"class": "info clear"})
            title_node = container.find("div", {"class": "title"}).find("a")
            title = title_node.get_text()
            detail_page_link = title_node.attrs["href"]

            address_node = container.find("div", {"class": "houseInfo"})
            address_info = address_node.get_text()

            try:
                xiaoqu, huxing, mianji, chaoxiang, zhuangxiu = address_info.split("|")
            except ValueError:
                continue

            price_node = container.find("div", {"class": "totalPrice"})
            price = price_node.find("span").get_text()

            row = (detail_page_link, title, price,
                   xiaoqu, huxing, mianji, chaoxiang, zhuangxiu)
            row = tuple(item.strip() for item in row)
            logging.debug(row)
            if out_q:
                out_q.put(row)
        except AttributeError:
            pass


def _get_next_page_link(bs_obj):
    list_page_box = bs_obj.find("div", {"class": "page-box house-lst-page-box"})
    page_info = json.loads(list_page_box.attrs["page-data"])
    if page_info["totalPage"] == page_info["curPage"]:
        return None
    else:
        next_page = page_info["curPage"] + 1
        return "/ershoufang/pg%s" % next_page


def get_items(sentinel, out_q=None):
    """
    从目标网站抓取item列表
    :param sentinel: 标示数据结束的哨兵值
    :param out_q:　用于存储输出结果的数据结构，必须实现put()方法
    :return: 所抓取的条目数量
    """
    host = config.host
    headers = config.headers
    proxies = config.proxies
    first_page = config.first_page
    page = first_page
    cnt = 0
    while page:
        try:
            response = requests.get(url="http://"+host+page, headers=headers, proxies=proxies)
            if response.status_code == 200:
                bs_obj = BeautifulSoup(response.content, "lxml")
                get_items_in_page(bs_obj, out_q=out_q)
                next_page = _get_next_page_link(bs_obj)
                if page == next_page:
                    break
                page = next_page
            else:
                break
            time.sleep(random.randint(0, 5)+1)
            cnt += 1
        except requests.exceptions.ConnectionError:
            pass
    out_q.put(sentinel)
    return cnt


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

