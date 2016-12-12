#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
import os
from queue import Queue
from threading import Thread

import config
import list_crawler
from detail_crawler import consumer
import tools


def log_setting():
    if tools.check_dir(config.log_dir):
        log_file = os.path.join(config.log_dir, "log.txt")
        logging.basicConfig(level=config.log_level,
                            format=config.log_format,
                            # filename=log_file
                            )
    else:
        logging.basicConfig(level=config.log_level,
                            format=config.log_format)


def main():
    log_setting()

    sentinel = object()
    q = Queue(config.size_of_queue)
    t1 = Thread(target=list_crawler.get_items, args=(sentinel, q))
    t2 = Thread(target=consumer, args=(sentinel, q))
    t1.start()
    t2.start()
    q.join()
    t1.join()
    t2.join()


main()