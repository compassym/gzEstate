#! /usr/bin/env python3
# -*- coding:utf-8 -*-


import pandas as pd
import sqlite3
import datetime
import json
from functools import partial
try:
    import baidu_api_ak
except ImportError:
    baidu_api_ak = None


Price_Query = """
                SELECT
                "链家编号", "标题", "总价", "建筑面积", "经度", "纬度"
                FROM houses;
              """
House_Age_Query = """
                SELECT
                "链家编号", "标题", "建筑年代", "经度", "纬度"
                FROM houses;
"""

API_Pattern_Html = "./baidu_api_pattern.html"

def round_off(x, point_pos):
    return int(x * point_pos + 0.5) / point_pos


def read_df(db_file, query):
    """
    从指定的数据库文件中读取数据，并调用wash函数对数据进行清洗
    :param db_file: sqlite3数据库文件
    :param query: sql查询语句 str类型
    :return: 对所读取数据调用wash后的结果
    """
    with sqlite3.connect(db_file) as con:
        df = pd.read_sql(query, con)
        return df


def product_html(center_lnt, center_lat, positions, api_pattern_html, dest_html):
    with open(api_pattern_html) as pattern_file, open(dest_html, "w") as dest_file:
        pattern = pattern_file.read()
        positions_repr = json.dumps(positions, ensure_ascii=False)
        positions_repr = positions_repr.replace("},", "},")

        ak = "您的密钥"
        if baidu_api_ak:
            ak = baidu_api_ak.ak
        query_str = "/api?v2.0&ak=%s" % ak
        pattern = pattern.replace("{{query_url}}", query_str)
        pattern = pattern.replace("{{center_lnt}}", str(center_lnt))
        pattern = pattern.replace("{{center_lat}}", str(center_lat))
        pattern = pattern.replace("{{points}}", positions_repr)
        dest_file.write(pattern)


def wash_price(df):
    df["单价"] = df["总价"] / df["建筑面积"]
    map_fn = partial(round_off, point_pos=10000.0)
    df["经度_集中"] = df["经度"].map(map_fn)
    df["纬度_集中"] = df["纬度"].map(map_fn)

    df_group = df.groupby([df["经度_集中"], df["纬度_集中"]]).mean()
    df_group["单价"] = df_group["单价"]\
                       .map(partial(round_off, point_pos=10.0)) * 10.0
    to_dict = lambda row : \
        {"lng": row["经度_集中"], "lat": row["纬度_集中"], "count": row["单价"]}
    positions = [to_dict(df_group.ix[index]) for index in df_group.index]

    return positions

def wash_house_age(df):
    df = df[df["建筑年代"] != -1]
    df["楼龄"] = df["建筑年代"] - datetime.datetime.today().year
    df["楼龄"] = df["楼龄"] * (-1)
    print(df)

    map_fn = partial(round_off, point_pos=10000.0)
    df["经度_集中"] = df["经度"].map(map_fn)
    df["纬度_集中"] = df["纬度"].map(map_fn)

    df_group = df.groupby([df["经度_集中"], df["纬度_集中"]]).mean()
    to_dict = lambda row : \
        {"lng": row["经度_集中"], "lat": row["纬度_集中"], "count": row["楼龄"]}
    positions = [to_dict(df_group.ix[index]) for index in df_group.index]

    return positions


def handle(db_file, wash, query, dest_html_pretend, api_pattern_html=API_Pattern_Html):
    df = read_df(db_file, query)
    positions = wash(df)

    center_lnt = (df["经度"].max() + df["经度"].min())/2.0
    center_lat = (df["纬度"].max() + df["纬度"].min())/2.0

    dest_html = ".".join([db_file, dest_html_pretend, ".html"])
    product_html(center_lnt, center_lat, positions, api_pattern_html, dest_html)

handle_price = partial(handle,
                       wash=wash_price,
                       query=Price_Query,
                       dest_html_pretend="price",
                       api_pattern_html=API_Pattern_Html)

handle_house_age = partial(handle,
                           wash=wash_house_age,
                           query=House_Age_Query,
                           dest_html_pretend="house_age",
                           api_pattern_html=API_Pattern_Html)

if __name__ == "__main__":
    def main():
        db_files = [ "./data/gz.houses.db.20170108", ]
        for db_file in db_files:
            handle_price(db_file)
            handle_house_age(db_file)

    main()


