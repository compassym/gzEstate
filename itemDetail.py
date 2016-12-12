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
    number_pattern = re.compile(r"(\d+(?:\.\d*)?).*")

    def __init__(self):
        self.driver = webdriver.PhantomJS(
            service_args=config.phantomjs_args
        )

    def set_page_link(self, page_link):
        self.page_link = page_link
        self.url = "http://"+ config.host + self.page_link
        self.bs_obj = None

        self.detail = {}
        self.detail["链家编号"] = page_link
        self._get_detail()

    def _get_detail(self):
        try:
            self.driver.get(url=self.url)
            if self.driver.page_source:
                self.bs_obj = BeautifulSoup(self.driver.page_source, "lxml")
                self.detail["纬度"], self.detail["经度"] = self.get_position(self.bs_obj)
                self._get_school()
                self._get_overview()
                self._get_base_detail()
                self._get_transaction_info()

                for label, value in self.detail.items():
                    logging.debug("%s: %s" % (label, value))
        except RemoteDisconnected as e:
            logging.error(e)

    def _get_overview(self):
        """
        从网页右上角提取房屋总体信息
        """
        try:
            self._read_price()
            self._read_niandai()
            self._read_xiaoqu()
        except AttributeError as e:
            logging.warning(e)

    def _read_price(self):
        try:
            total_price = self.bs_obj.find("div", {"class": "price"}) \
                                     .find("span", {"class": "total"}) \
                                     .get_text()
            self.detail["总价"] = float(total_price)
        except AttributeError as e:
            self.detail["总价"] = 0
            logging.warning("房源%s获取总价失败! %s" %
                            (self.page_link, e))

        try:
            shoufu_node = self.bs_obj.find("div", {"class": "tax"}) \
                                     .findAll("span")[0]
            shoufu = ItemDetail.number_pattern \
                               .search(shoufu_node.get_text()).groups()[0]
            self.detail["首付"] = float(shoufu)
        except AttributeError as e:
            self.detail["首付"] = 0
            logging.warning("房源%s获取首付失败! %s" %
                            (self.page_link, e))

        try:
            tax = self.bs_obj.find("span", {"id": "PanelTax"}).get_text()
            self.detail["税费"] = float(tax)
        except AttributeError as e:
            self.detail["税费"] = 0
            logging.warning("房源%s获取税费失败! %s" %
                            (self.page_link, e))

    def _read_niandai(self):
        try:
            niandai = self.bs_obj.find("div", {"class": "houseInfo"}) \
                .find("div", {"class": "area"}) \
                .find("div", {"class": "subInfo"}) \
                .get_text()
            niandai_match = ItemDetail.number_pattern.search(niandai)
            self.detail["建筑年代"] = int(niandai_match.groups()[0])
        except AttributeError as e:
            self.detail["建筑年代"] = -1
            logging.warning("房源%s获取建筑年代信息失败! %s" %
                            (self.page_link, e))

    def _read_xiaoqu(self):
        try:
            xiaoqu = self.bs_obj.find("div", {"class": "communityName"}) \
                .find("a", {"class": "info"})
            self.detail["小区"] = xiaoqu.get_text()
            areaName = self.bs_obj.find("div", {"class": "areaName"}) \
                .find("span", {"class": "info"}) \
                .findAll("a")
            self.detail["行政区"] = areaName[0].get_text()
            self.detail["板块"] = areaName[1].get_text()
        except AttributeError as e:
            logging.warning("房源%s获取小区/板块/区划信息失败! %s" %
                            (self.page_link, e))

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

    def _get_base_detail(self):
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
            self._wash_huxing()
            self._wash_louceng()
            self._wash_tihubili()
            self._wash_square()
            self._wash_dianti()
        except AttributeError:
            pass

    def _wash_huxing(self):
        try:
            huxing = self.detail["房屋户型"]
            self.detail["房屋户型"] = {}
            items = ("室", "厅", "厨", "卫")
            item_cnt = ItemDetail.huxing_pattern.match(huxing)
            for idx, item in enumerate(items):
                cnt = item_cnt.groups()[idx]
                self.detail["房屋户型"][item] = int(cnt)
        except (AttributeError, IndexError) as e:
            logging.warning("清洗房源%s户型数据失败! %s" %
                            (self.page_link, e))

    def _wash_louceng(self):
        try:
            self.detail["所在楼层"] = ItemDetail.louceng_pattern \
                .match(self.detail["所在楼层"]) \
                .groups()[0]
        except (AttributeError, IndexError) as e:
            logging.warning("清洗房源%s楼层数据失败! %s" %
                            (self.page_link, e))

    def _wash_square(self):
        pattern = ItemDetail.number_pattern
        try:
            square_match = pattern.match(self.detail["建筑面积"])
            self.detail["建筑面积"] = float(square_match.groups()[0])
        except (AttributeError, IndexError, ValueError) as e:
            logging.warning("清洗房源%s建筑面积数据失败! %s" %
                            (self.page_link, e))
        try:
            square_match = pattern.match(self.detail["套内面积"])
            self.detail["套内面积"] = float(square_match.groups()[0])
        except (AttributeError, IndexError, ValueError):
            pass

    def _wash_tihubili(self):
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
        except (AttributeError, IndexError) as e:
            logging.warning("清洗房源%s梯户比例数据失败! %s" %
                            (self.page_link, e))

    def _wash_dianti(self):
        self.detail["配备电梯"] = True \
            if self.detail.get("配备电梯") == "有" \
            else False

    def _get_school(self):
        """
        从BeautifulSoup对象提取房屋学位
        :return: None
        """
        try:
            node = self.bs_obj.find("div", {"id": "matchSchool"})
            self.detail["对口学校"] = node.find("span", {"class": "fortitle"}).find("a").get_text()
            logging.debug("对口学校: %s" % self.detail["对口学校"])
        except AttributeError as e:
            logging.warning("房源%s学位信息获取失败! %s" %
                            (self.page_link, e))
            self.detail["对口学校"] = None

    def _get_transaction_info(self):
        """
        获取网页中交易属性表格
        :return:
        """
        try:
            nodes = self.bs_obj.find("div", {"class": "transaction"}).findAll("li")
            for node in nodes:
                label = node.find("span").get_text()
                txt = node.get_text().replace(label, "").strip()
                self.detail[label.strip()] = txt
        except AttributeError:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    test_links = [
        "/ershoufang/GZ0002273962.html",
        "/ershoufang/GZ0002186316.html",
        "/ershoufang/GZ0002281204.html",
    ]
    detail_parser = ItemDetail()
    for link in test_links:
        house_detail = detail_parser.set_page_link(link)
