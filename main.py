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
    discrete = not config.use_single_db
    db_files = crawler.crawl(towns, config.city, discrete=discrete)
    for db_file in db_files:
        heat_visualize.handle_price(db_file)
        heat_visualize.handle_house_age(db_file)


main()
