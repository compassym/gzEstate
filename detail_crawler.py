#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import requests
import sqlite3
import os
import logging

import config
from itemDetail import ItemDetail
import tools


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
    cursor.execute("""
        CREATE TABLE jobs(
        id INTEGER PRIMARY KEY,
        enterprise TEXT, job TEXT,
        lnt FLOAT, lat FLOAT,
        pay_lower INTEGER, pay_upper INTEGER, pay_unit TEXT,
        experience_lower INTEGER, experience_upper INTEGER,
        descriptions TEXT, requirements TEXT,
        company_size TEXT,
        company_field TEXT,
        company_financing TEXT
        );
    """)

def get_detail(sentinel, in_q):
    with sqlite3.connect(get_db_file()) as db_conn:
        cursor = db_conn.cursor()
        create_table(cursor)
        db_conn.commit()
        while True:
            try:
                enterprise_job_link = in_q.get()
                if enterprise_job_link is sentinel:
                    break
                enterprise, job, page_link = enterprise_job_link
                job_detail = ItemDetail(page_link=page_link)
                descriptions = "；".join(job_detail.descriptions)
                requirements = "；".join(job_detail.requirements)
                data = (enterprise, job,
                        job_detail.lnt, job_detail.lat,
                        job_detail.pay_lower, job_detail.pay_upper, job_detail.pay_unit,
                        job_detail.experience_lower, job_detail.experience_upper,
                        descriptions, requirements,
                        job_detail.company_size,
                        job_detail.company_field,
                        job_detail.company_financing)
                sql = """
                    INSERT INTO jobs(
                        enterprise, job,
                        lnt, lat,
                        pay_lower, pay_upper, pay_unit,
                        experience_lower, experience_upper,
                        descriptions, requirements,
                        company_size,
                        company_field,
                        company_financing
                    )
                    VALUES(?,?,
                    ?,?,
                    ?,?,?,
                    ?,?,
                    ?,?,
                    ?,?,?);
                """
                cursor.execute(sql, data)
                db_conn.commit()
            except requests.exceptions.ConnectionError:
                pass