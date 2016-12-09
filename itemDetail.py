#! /usr/bin/env python3
# -*- coding:utf-8 -*-

from http.client import RemoteDisconnected
from selenium import webdriver
from bs4 import BeautifulSoup
import logging
import re

import config


class ItemDetail:
    def __init__(self, page_link):
        self.driver = webdriver.PhantomJS(service_args=config.phantomjs_args)

        self.url="http://"+ config.host + page_link
        self.bs_obj = None

        self.lat = None
        self.lnt = None
        self.price_shoufu = None
        self.price_tax = None
        self.nianxian = None
        self.fangben = None
        self.guapai_shijian = None
        self.last_transaction = None
        self.school = None

        self._get_detail(page_link)

    def _get_detail(self, page_link):
        try:
            self.driver.get(url=self.url)
            if self.driver.page_source:
                self.bs_obj = BeautifulSoup(self.driver.page_source, "lxml")
                self.lat, self.lnt = self.get_position(self.bs_obj)
                self.get_price_shoufu()
                self.get_nianxian()
                self.get_school()
                self.get_transaction_info()
        except RemoteDisconnected as e:
            logging.error(e)
        finally:
            self.driver.quit()

    def get_position(self, bs_obj):
        """
        从BeautifulSoup对象提取地址信息
        :param bs_obj: 从网页构造的BeautifulSoup对象
        :return: tuple对象，("纬度值", "经度值")
        """
        try:
            # 纬度
            lat = bs_obj.find("input", {"id": "lat"}).attrs["value"]
            # 经度
            lnt = bs_obj.find("input", {"id": "lnt"}).attrs["value"]
            logging.debug("Position: (%s, %s)" % (lat, lnt))
            return lat.strip(), lnt.strip()
        except AttributeError:
            return None, None

    def get_price_shoufu(self):
        """
        从BeautifulSoup对象提取首付及税费信息
        :return: None
        """
        try:
            tax_node = self.bs_obj.find("div", {"class": "tax"})
            price_shoufu_txt = tax_node.find("span").get_text()
            self.price_shoufu = re.match(r"[^0-9]*((?:\d+)(?:\.\d+|)).*", price_shoufu_txt).groups()[0]
            logging.debug("首付: %s, 税费: %s" % (self.price_shoufu, self.price_tax))
        except AttributeError:
            pass

    def get_nianxian(self):
        """
        从BeautifulSoup对象提取房屋年限信息
        :return: None
        """
        try:
            area_node = self.bs_obj.find("div", {"class": "area"})
            self.nianxian = area_node.find("div", {"class": "subInfo"}).get_text()
            logging.debug("年限: %s" % self.nianxian)
        except AttributeError:
            pass

    def get_school(self):
        """
        从BeautifulSoup对象提取房屋学位
        :return: None
        """
        try:
            node = self.bs_obj.find("div", {"id": "matchSchool"})
            self.school = node.find("span", {"class": "fortitle"}).find("a").get_text()
            logging.debug("对口学校: %s" % self.school)
        except AttributeError:
            pass

    def get_transaction_info(self):
        """
        从BeautifulSoup对象提取房屋交易信息
        :return: None
        """
        try:
            info_node = self.bs_obj.find("div", {"class": "introContent"})\
                                   .find("div", {"class": "transaction"})\
                                   .findAll("li")
            self.guapai_shijian = self.remove_label(info_node[0])
            self.last_transaction = self.remove_label(info_node[2])
            self.fangben = self.remove_label(info_node[4])
            logging.debug("挂牌时间: %s, 上次交易: %s, 房本年限: %s"
                          % (self.guapai_shijian, self.last_transaction, self.fangben))

        except AttributeError:
            pass

    def remove_label(self, bs_obj):
        txt = bs_obj.get_text()
        label = bs_obj.find("span").get_text()
        return txt.replace(label, "")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    test_links = ["/ershoufang/GZ0002238316.html", "/ershoufang/GZ0002197589.html"]
    for link in test_links:
        house_detail = ItemDetail(link)
