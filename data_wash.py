#! /usr/bin/env python3
# -*- coding:utf-8 -*-


import pandas as pd
import sqlite3


_DB_File = "./data/houses.db"

keys =[
    "链家编号", "标题",
    "总价",  "首付",  "税费",
    "建筑年代",  "配备电梯",
    "梯户比例",  "建筑结构", "建筑类型", "所在楼层",
    "装修情况",  "房屋朝向",
    "行政区",  "板块",  "小区",
    "建筑面积",  "房本年限",  "挂牌时间",  "上次交易",
    "产权所属",  "房屋用途", "交易权属"
]

query = " ".join(
    ["SELECT ", ", ".join(keys), " FROM houses;"]
)

db_conn = sqlite3.connect(_DB_File)

df = pd.io.sql.read_sql(query, db_conn)

print(df)

