# -*- coding:utf-8 -*-

import os
import config

def check_dir(dir_path):
    if os.path.isdir(dir_path):
        return True
    try:
        os.mkdir(dir_path)
        return True
    except (PermissionError, FileExistsError):
        return False


def first_page(town):
    return "/ershoufang/%s/pg1" % (town.strip(),) \
            if town and town.strip() \
            else "/ershoufang/pg1"
