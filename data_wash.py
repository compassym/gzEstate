#! /usr/bin/env python3
# -*- coding:utf-8 -*-


import numpy as np
import pandas as pd
import sqlite3
import logging


_DB_File = "./data/houses.db"

_Fields = [
    "链家编号", "标题",
    "总价",  "首付",  "税费",
    "建筑年代",  "配备电梯",
    "梯户比例",  "建筑结构", "建筑类型", "所在楼层",
    "装修情况",  "房屋朝向",
    "行政区",  "板块",  "小区",
    "建筑面积",  "房本年限",  "挂牌时间",  "上次交易",
    "产权所属",  "房屋用途", "交易权属",
    "室", "厅", "厨", "卫"
]


class NormalizeMap:
    """
    归一化的映射表，支持正反向查询
    """

    def __init__(self, dataset: pd.DataFrame):
        """
        根据数据集建立每一列数据的归一化映射表
        :param dataset: 待处理的数据集
        """
        self._normalize_map = {
            column: self.map_field2number(dataset[column])
            for column in dataset.columns
            if dataset[column].dtype.name == "object"
            }
        for column in dataset.columns:
            if dataset[column].dtype.name != "object":
                self._normalize_map[column] = \
                    (dataset[column].min(), dataset[column].max())
        logging.debug("归一化映射表为: %s" % (self._normalize_map,))

    def normalize(self, field:str, value):
        """
        将field数据域的原始数据值value进行归一化计算后返回
        :param field: dataset数据集中field数据域键名
        :param value: 待归一化的数据
        :return: float 归一化后的数据值
        """
        table = self._normalize_map[field]
        if(isinstance(table, tuple)):
            min, max = table
            return (float(value)-min)/(max-min)
        else:
            return table[value]

    def de_normalize(self, field:str, value:float):
        """
        将field数据域对应的归一化数据之value还原为原始数据值
        :param field: dataset数据集中field数据域键名
        :param value: 已归一化的数据
        :return:  还原为原始数据后的值
        """
        table = self._normalize_map[field]
        if(isinstance(table, tuple)):
            min, max = table
            return min + value*(max-min)
        else:
            for k,v in table.items():
                if abs(value-v) < 0.00000001:
                    return k


    @staticmethod
    def map_field2number(series: pd.Series):
        """
        根据一个序列，建立元素到归一化数值的映射表，
        :param series: pandas.Series类型
        :return: dict类型, 从元素到归一化数值的映射表

        Example:
        >>> HouseFrame.map_field2number(pd.Series(["1", "foo", "1", "bar"]))
        {'1': 0.0, 'bar': 0.5, 'foo': 1.0}

        >>> HouseFrame.map_field2number(pd.Series(["2", "foo", "foo"]))
        {'2': 0.0, 'foo': 1.0}

        """
        unique_values = series.sort_values().unique()
        if len(unique_values) == 1:
            return {unique_values[0]: 1}
        step = 1.0/(len(unique_values)-1)

        return {item: step*index
                for index, item in enumerate(unique_values)}


class HouseFrame:
    """
    处理房源列表
    """

    def __init__(self, db_conn, table, fields):
        """
        读取数据，并初始化HouseFrame
        :param db_conn: 数据库链接，HouseFrame实例将从该链接读取数据
        :param table: 数据库中存储目标数据的表
        :param fields: table表中将要读取的数据域
        """
        self._df = None
        self._dataset = None
        self._read_frame(db_conn, table, fields)
        logging.debug(self.df)
        self._normalize_map = NormalizeMap(self.df)
        self._normalize()

    def _read_frame(self, db_conn, table, fields):
        query = " ".join(
            ["SELECT ",
             ", ".join(fields),
             " FROM ",
             table,
             ";"]
        )
        self._df = pd.io.sql.read_sql(query, db_conn)

        def convert2number(x):
            try:
                return float(x)
            except ValueError:
                return np.NaN

        self._df["梯户比例"] = self._df["梯户比例"].map(convert2number)

    def _normalize(self):
        for column in self.df.columns:
            self.df[column] = self.df[column].map(
                lambda x: self._normalize_map.normalize(column, x)
            )

    @property
    def df(self):
        """
        获取内部数据
        :return: pandas.DataFrame对象实例
        """
        return self._df

    @property
    def dataset(self):
        """
        返回供机器学习使用的数据集
        :return:
        """
        if self._dataset is not None:
            return self._dataset
        else:
            self._dataset = {
                "input": pd.DataFrame(),
                "target": pd.DataFrame()
            }
            target_columns = ("总价", "首付", "税费")
            for column in target_columns:
                self._dataset["target"][column] = self._df[column]
            for column in self._df.columns:
                if column not in target_columns:
                    self._dataset["input"][column] = self._df[column]
            return self._dataset


if __name__ == "__main__":
    def _main():
        logging.basicConfig(level=logging.DEBUG)
        with sqlite3.connect(_DB_File) as db_conn:
            house_frame = HouseFrame(db_conn, "houses", _Fields)
            dataset = house_frame.dataset
            print("输入数据:")
            print(dataset["input"])
            print("\n目标数据:")
            print(dataset["target"])

    _main()
