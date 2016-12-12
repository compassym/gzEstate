#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import sqlite3
import os
import logging
from concurrent.futures import ThreadPoolExecutor

import config
from itemDetail import ItemDetail
import tools


_KeyOfDetails = [
    ("链家编号", "TEXT"),

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

    ("经度", "TEXT"), ("纬度", "TEXT"),

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
        [ ''.join(["'", item[0], "' ", item[1]]) for item in _KeyOfDetails]
    )
    sql_components.extend(
        [ ''.join(["'", item[0], "' ", item[1]]) for item in _KeyOfHuxing]
    )

    sql = ", ".join(sql_components)
    sql = sql + ");"
    logging.debug("数据表创建sql语句为: ")
    logging.debug(sql)
    cursor.execute(sql)

def construct_insert_sql():
    sql_components = ["INSERT INTO houses("]
    sql_components.append(",".join(
        ["".join(["'", item[0], "'"]) for item in _KeyOfDetails]
    ))
    sql_components.append(",")
    sql_components.append(",".join(
        ["".join(["'", item[0], "'"]) for item in _KeyOfHuxing]
    ))
    sql_components.append(") VALUES(")
    data_len = len(_KeyOfDetails) + len(_KeyOfHuxing)
    sql_components.append(
        ",".join(("?" for _ in range(data_len)))
    )
    sql_components.append(");")
    sql = " ".join(sql_components)
    logging.debug("数据插入语句为: ")
    logging.debug(sql)
    return sql

def get_detail(parser, page_link):
    parser.set_page_link(page_link)
    return parser.detail

def consumer(sentinel, in_q):
    pool = ThreadPoolExecutor(128)
    db_file = get_db_file()

    def call_back(future):
        detail = future.result()
        data = [detail[key[0]] for key in _KeyOfDetails]
        data.extend(
            [detail["房屋户型"][key[0]] for key in _KeyOfHuxing]
        )
        with sqlite3.connect(db_file) as db_conn:
            try:
                cursor = db_conn.cursor()
                cursor.execute(sql, data)
                db_conn.commit()
            except sqlite3.ProgrammingError as e:
                logging.error(e)

    with sqlite3.connect(db_file) as db_conn:
        cursor = db_conn.cursor()
        create_table(cursor)
        db_conn.commit()

    house_detail_parser = ItemDetail()
    sql = construct_insert_sql()

    while True:
        try:
            house_meta_data = in_q.get()
            if house_meta_data is sentinel:
                break
            page_link = house_meta_data[0]
            submit = pool.submit(get_detail,
                                 house_detail_parser,
                                 page_link)
            submit.add_done_callback(call_back)
        except KeyError as e:
            logging.error("房源%s记录发生错误: %s" % (page_link, e))
            pass
