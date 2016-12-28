#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import sqlite3
import os
import logging

import config
from item_detail import ItemDetail
import tools


_KeyOfDetails = [
    ("链家编号", "TEXT"), ("标题", "TEXT"),

    ("总价", "FLOAT"), ("首付", "FLOAT"), ("税费", "FLOAT"),

    ("建筑年代", "INTEGER"), ("配备电梯", "BOOLEAN"),
    ("梯户比例", "FLOAT"), ("建筑结构", "TEXT"),
    ("建筑类型", "TEXT"),

    ("所在楼层", "TEXT"), ("户型结构", "TEXT"),
    ("装修情况", "TEXT"), ("房屋朝向", "TEXT"),
    # ("房屋户型", "TEXT"),

    ("行政区", "TEXT"), ("板块", "TEXT"), ("小区", "TEXT"),

    ("建筑面积", "FLOAT"), ("套内面积", "FLOAT"),

    ("房本年限", "TEXT"), ("挂牌时间", "TEXT"), ("上次交易", "TEXT"),

    ("经度", "FLOAT"), ("纬度", "FLOAT"),

    ("产权所属", "TEXT"), ("房本备件", "TEXT"), ("房屋用途", "TEXT"),
    ("交易权属", "TEXT"), ("抵押信息", "TEXT"),

    ("供暖方式", "TEXT"),
]

_KeyOfHuxing = [
    ("室", "INTEGER"),
    ("厅", "INTEGER"),
    ("厨", "INTEGER"),
    ("卫", "INTEGER"),
]


def get_db_file():
    if tools.check_dir(config.db_dir):
        db_dir = config.db_dir
    else:
        logging.error("按照配置文件构建数据库存储目录失败，将在当前目录构建数据库文件!")
        db_dir = "./"
    return get_new_db_file(db_dir, config.db)


def get_new_db_file(db_dir, db_file):
    path_pre = os.path.join(db_dir, db_file)
    if not os.path.exists(path_pre):
        return path_pre
    path_suf = 0
    while os.path.exists("".join([path_pre, ".", str(path_suf)])):
        path_suf += 1
    return "".join([path_pre, ".", str(path_suf)])


def create_table(cursor):
    """
    创建数据库表
    :param cursor: 数据库连接提供的cursor
    :return:
    """
    sql_components = ["CREATE TABLE houses(id INTEGER PRIMARY KEY"]
    sql_components.extend(
        [''.join(["'", item[0], "' ", item[1]]) for item in _KeyOfDetails]
    )
    sql_components.extend(
        [''.join(["'", item[0], "' ", item[1]]) for item in _KeyOfHuxing]
    )

    sql = ", ".join(sql_components) + ");"
    logging.debug("数据表创建sql语句为: ")
    logging.debug(sql)
    cursor.execute(sql)


def construct_insert_sql():
    sql_components = [
        "INSERT INTO houses(",
        ",".join(["".join(["'", item[0], "'"]) for item in _KeyOfDetails]),
        ",",
        ",".join(["".join(["'", item[0], "'"]) for item in _KeyOfHuxing]),
        ") VALUES("
    ]
    data_len = len(_KeyOfDetails) + len(_KeyOfHuxing)
    sql_components.append(
        ",".join(("?" for _ in range(data_len)))
    )
    sql_components.append(");")
    sql = " ".join(sql_components)
    logging.debug("数据插入语句为: ")
    logging.debug(sql)
    return sql


def get_detail(page_link, title):
    detail_parser = ItemDetail()
    detail_parser.set_page_link(page_link, title)
    return detail_parser.detail


_DB_File = get_db_file()


def create_db():
    global _DB_File
    with sqlite3.connect(_DB_File) as db_conn:
        cursor = db_conn.cursor()
        create_table(cursor)
        db_conn.commit()


def write2db_for_pool_callback(future):
    global _DB_File
    detail = future.result()
    write2db(detail)

def write2db(detail):
    try:
        data = [detail[key[0]] for key in _KeyOfDetails]
        data.extend(
            [detail["房屋户型"][key[0]] for key in _KeyOfHuxing]
        )
        logging.info("房源 %s 处理完毕!" % detail["链家编号"])
    except KeyError as e:
        logging.error("房源 %s 处理有误:  %s" % (detail["链家编号"], e))
        return

    sql = construct_insert_sql()
    with sqlite3.connect(_DB_File) as db_conn:
        try:
            cursor = db_conn.cursor()
            cursor.execute(sql, data)
            db_conn.commit()
        except sqlite3.ProgrammingError as e:
            logging.error("房源 %s 数据写入数据库错误! %s" %
                          (detail["链家编号"], e))
