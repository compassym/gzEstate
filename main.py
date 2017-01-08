#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import logging, os
import tools, config
import crawler
import heat_visualize

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



def main():
    log_setting()

    towns = config.towns
    if not towns:
        towns = [""]
    for index in range(len(towns)):
        db_file = crawler.crawl(towns[index], config.city)
        heat_visualize.handle_price(db_file)


main()
