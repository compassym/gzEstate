#! /usr/bin/env python3
# -*- coding:utf-8

import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import datetime
import random
import logging

import config

random.seed(datetime.datetime.now())

_job_table = {}


def _get_job_table_in_page(bs_obj, out_q=None):
    global _job_table
    job_nodes = bs_obj.findAll("li", {"class": "jobinfo brjob clearfix"})
    for job_node in job_nodes:
        try:
            job_tag = job_node.find("a", {"href": re.compile("^/j/[0-9]+")})
            job = job_tag.strong.get_text()
            enterprise = job_node.find("div", {"class": "jobnote-r"}).strong.get_text()
            key = (enterprise, job)
            if key not in _job_table:
                _job_table[key] = job_tag.attrs["href"]
                row = (enterprise, job, _job_table[key])
                if out_q:
                    out_q.put(row)
                logging.debug(row)
        except AttributeError:
            pass


def _get_next_page_link(bs_obj):
    page_link = bs_obj.find("div", {"class": "t_pagelink"})
    next_page_link = page_link.find("a", {"class": "next"})
    if next_page_link is not None:
        return next_page_link.attrs["href"]


def get_jobs(sentinel, out_q=None):
    """
    从“内推网”抓取职位列表
    :param sentinel: 标示数据结束的哨兵值
    :param out_q:　用于存储输出结果的数据结构，必须实现put()方法
    :return: dict对象，形式为{(公司，职位): 链接}
    """
    host = config.host
    headers = config.headers
    proxies = config.proxies
    first_page = config.first_page
    page = first_page
    while page:
        try:
            response = requests.get(url="http://"+host+page, headers=headers, proxies=proxies)
            if response.status_code == 200:
                bs_obj = BeautifulSoup(response.content, "lxml")
                _get_job_table_in_page(bs_obj, out_q=out_q)
                next_page = _get_next_page_link(bs_obj)
                if page == next_page:
                    break
                page = next_page
            else:
                break
            time.sleep(random.randint(0, 5)+1)
        except requests.exceptions.ConnectionError:
            pass
    out_q.put(sentinel)
    return _job_table


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    from queue import Queue
    from threading import Thread

    q = Queue()

    def consumer(in_q):
        while True:
            print(in_q.get())

    job_list_file = config.job_list_file
    with open(job_list_file, "w+") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(("enterprise", "job", "link"))

        t1 = Thread(target=get_jobs, args=(q,))
        t2 = Thread(target=consumer, args=(q,))
        t1.start()
        t2.start()

