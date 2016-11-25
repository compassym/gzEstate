# -*- coding:utf-8 -*-

import os

def check_dir(dir_path):
    if os.path.isdir(dir_path):
        return True
    try:
        os.mkdir(dir_path)
        return True
    except (PermissionError, FileExistsError):
        return False
