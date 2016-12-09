#! /usr/bin/env python3
# -*- coding:utf-8 -*-

from http.client import RemoteDisconnected
from selenium import webdriver
from bs4 import BeautifulSoup
import logging
import re

import config


class ItemDetail:
    huxing_pattern = re.compile(r"(\d)室(\d)厅(\d)厨(\d)卫")
    louceng_pattern = re.compile(r"(.*)楼层.*")
    tihu_pattern = re.compile(r"(.*)梯(.*)户")
    square_pattern = re.compile(r"(\d*(?:\.\d*)?).*")

    def __init__(self, page_link):
        self.driver = webdriver.PhantomJS(
            service_args=config.phantomjs_args
        )

        self.url = "http://"+ config.host + page_link
        self.bs_obj = None

        self.detail = {}

        self._get_detail()

    def _get_detail(self):
        try:
            self.driver.get(url=self.url)
            if self.driver.page_source:
                self.bs_obj = BeautifulSoup(self.driver.page_source, "lxml")
                self.detail["纬度"], self.detail["经度"] = self.get_position(self.bs_obj)
                self.get_school()
                self.get_base_detail()
                # self.get_price_shoufu()
                # self.get_nianxian()
                # self.get_transaction_info()
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

    def get_base_detail(self):
        """
        从网页的“基本属性”表格中获取房屋的基本信息
        包括: 户型，楼层，建筑面积，建筑类型，房屋朝向，建筑结构，梯户比例，
        电梯与否等
        :return:
        """
        try:
            nodes = self.bs_obj.find("div", {"class": "base"}).findAll("li")
            for node in nodes:
                label = node.find("span").get_text()
                txt = node.get_text().replace(label, "").strip()
                self.detail[label.strip()] = txt
            self.wash_huxing()
            self.wash_louceng()
            self.wash_tihubili()
            self.wash_square()
            self.wash_dianti()

            for label, value in self.detail.items():
                logging.debug("%s: %s" % (label, value))
        except AttributeError:
            pass

    def wash_huxing(self):
        try:
            huxing = self.detail["房屋户型"]
            self.detail["房屋户型"] = {}
            items = ("室", "厅", "厨", "卫")
            item_cnt = ItemDetail.huxing_pattern.match(huxing)
            for idx, item in enumerate(items):
                cnt = item_cnt.groups()[idx]
                self.detail["房屋户型"][item] = int(cnt)
        except (AttributeError, IndexError):
            pass

    def wash_louceng(self):
        try:
            self.detail["所在楼层"] = ItemDetail.louceng_pattern \
                .match(self.detail["所在楼层"]) \
                .groups()[0]
        except (AttributeError, IndexError):
            pass

    def wash_square(self):
        try:
            pattern = ItemDetail.square_pattern
            square_match = pattern.match(self.detail["建筑面积"])
            self.detail["建筑面积"] = float(square_match.groups()[0])
            square_match = pattern.match(self.detail["套内面积"])
            self.detail["套内面积"] = float(square_match.groups()[0])
        except (AttributeError, IndexError, ValueError):
            pass

    def wash_tihubili(self):
        try:
            cn_cnt = {
                "一": 1, "二": 2, "两": 2,
                "三": 3, "四": 4, "五": 5,
                "六": 6, "七": 7, "八": 8,
                "九": 9, "十": 10, "十一": 11,
                "十二": 12, "十三": 13, "十四": 14
            }
            match = ItemDetail.tihu_pattern.match(self.detail["梯户比例"])
            ti, hu = match.groups()
            self.detail["梯户比例"] = float(cn_cnt[ti])/float(cn_cnt[hu])
        except (AttributeError, IndexError):
            pass

    def wash_dianti(self):
        self.detail["配备电梯"] = True \
            if self.detail["配备电梯"] == "有" \
            else False

    def get_price_shoufu(self):
        """
        从BeautifulSoup对象提取首付及税费信息
        :return: None
        """
        try:
            tax_node = self.bs_obj.find("div", {"class": "tax"})
            price_shoufu_txt = tax_node.find("span").get_text()
            self.detail["首付"] = re.match(r"[^0-9]*((?:\d+)(?:\.\d+|)).*", price_shoufu_txt).groups()[0]
            logging.debug("首付: %s, 税费: %s" % (self.detail["首付"], self.detail["税费"]))
        except AttributeError:
            pass

    def get_nianxian(self):
        """
        从BeautifulSoup对象提取房屋年限信息
        :return: None
        """
        try:
            area_node = self.bs_obj.find("div", {"class": "area"})
            self.detail["建筑年限"] = area_node.find("div", {"class": "subInfo"}).get_text()
            logging.debug("建筑年限: %s" % self.detail["建筑年限"])
        except AttributeError:
            pass

    def get_school(self):
        """
        从BeautifulSoup对象提取房屋学位
        :return: None
        """
        try:
            node = self.bs_obj.find("div", {"id": "matchSchool"})
            self.detail["对口学校"] = node.find("span", {"class": "fortitle"}).find("a").get_text()
            logging.debug("对口学校: %s" % self.detail["对口学校"])
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
            self.detail["挂牌时间"] = self.remove_label(info_node[0])
            self.last_transaction = self.remove_label(info_node[2])
            self.detail["房本年限"] = self.remove_label(info_node[4])
            logging.debug("挂牌时间: %s, 上次交易: %s, 房本年限: %s"
                          % (self.detail["挂牌时间"], self.last_transaction, self.detail["房本年限"]))

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
