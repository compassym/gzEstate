#! /usr/bin/env python3
# -*- coding:utf-8 -*-

from http.client import RemoteDisconnected
import requests
from bs4 import BeautifulSoup
import logging
import re

import config


class ItemDetail:
    def __init__(self, page_link):
        self.bs_obj = None
        self.lat = None
        self.lnt = None
        self.job_name = None
        self.enterprise = None
        self.pay_upper = None
        self.pay_lower = None
        self.pay_unit = None
        self.experience_lower = None
        self.experience_upper = None
        self.experience_unit = None
        self.descriptions = None
        self.requirements = None
        self.company_size = None
        self.company_field = None
        self.company_financing = None

        self._get_detail(page_link)

    def _get_detail(self, page_link):
        headers = config.headers
        host = config.host
        proxies = config.proxies
        try:
            response = requests.get(url="http://"+host + page_link,
                                    headers=headers,
                                    proxies=proxies)
            if response.status_code == 200:
                self.bs_obj = BeautifulSoup(response.content, "lxml")
                self.lat, self.lnt = self.get_position(self.bs_obj)
                self.job_name, self.enterprise = self.get_job_name(self.bs_obj)
                self.pay_lower, self.pay_upper, self.pay_unit = self.get_pay(self.bs_obj)
                self.experience_lower, self.experience_upper, self.experience_unit \
                    = self.get_experience(self.bs_obj)
                self.descriptions, self.requirements \
                    = self.get_description_requirement(self.bs_obj)
                self.company_size, self.company_field, self.company_financing \
                    = self.get_company_info(self.bs_obj)
        except RemoteDisconnected as e:
            logging.error(e)

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

    def get_job_name(self, bs_obj):
        """
        从BeautifulSoup对象提取职位名称，对应的公司
        :param bs_obj: 从网页构造的BeautifulSoup对象
        :return: tuple对象, ("职位名称"，"公司")
        """
        try:
            job_name = bs_obj.find("div", {"class": "cont"})\
                             .find("strong", {"class": "padding-r10"})\
                             .get_text()
            enterprise = bs_obj.find("div", {"class": "c_name"})\
                               .find("a")\
                               .get_text()
            logging.debug("Job: (%s, %s)" % (job_name, enterprise))
            return job_name.strip(), enterprise.strip()
        except AttributeError:
            return None, None

    def get_pay(self, bs_obj):
        """
        从BeautifulSoup对象提取薪水
        :param bs_obj: 从网页构造的BeautifulSoup对象
        :return: tuple对象，("下限"，"上限"，"单位")
        """
        try:
            pay = bs_obj.find("span", {"class": "padding-r10 pay"}) \
                .get_text()
            lower, upper, unit = self.get_range(pay)
            logging.debug("薪资范围: [%s-%s]%s" %
                          (lower, upper, unit))
            return lower.strip(), upper.strip(), unit.strip()
        except AttributeError:
            return None, None, None

    def get_experience(self, bs_obj):
        """
        从BeautifulSoup对象提取公司要求的经验值
        :param bs_obj: 从网页构造的BeautifulSoup对象
        :return: tuple对象，("下限"，"上限"，"单位")
        """
        try:
            pay = bs_obj.find("span", {"class": "padding-r10 experience"}) \
                .get_text()
            lower, upper, unit = self.get_range(pay)
            logging.debug("经验要求: [%s-%s]%s" %
                          (lower, upper, unit))
            return lower.strip(), upper.strip(), unit.strip()
        except AttributeError:
            return None, None, None

    def get_range(self, txt):
        """
        从形式"[x-yUnit]"的文本中提取数值范围
        :param txt: 以文本形式提供的数值范围
        :return: tuple，（x, y, Unit)
        """
        try:
            pattern = "\[(\d+\s*)-(\d+\s*)(.*)\]"
            return re.match(pattern, txt).groups()
        except AttributeError:
            return None, None, None

    def get_description_requirement(self, bs_obj):
        """
        从BeautifulSoup对象提取职位描述信息
        :param bs_obj: 从网页构造的BeautifulSoup对象
        :return: tuple of list ([description1, description2, ...],
                                [requirement1, requirement2, ...])
        """
        try:
            txt = bs_obj.find("div", {"class": "jobdetail nooverflow"})\
                        .get_text().strip()
            items = re.sub(r"[:：;；。]", "\n", txt)
            items = [item.strip() for item in items.split("\n") if item.strip() != ""]
            descriptions = []
            requirements = []
            is_description = True
            for item in items[1:]:
                if not re.match("^\d+.*$", item):
                    is_description = False
                    continue
                if is_description:
                    descriptions.append(item)
                else:
                    requirements.append(item)
            logging.debug("职位描述:")
            for item in descriptions:
                logging.debug(item)
            logging.debug("职责需求:")
            for item in requirements:
                logging.debug(item)
            return descriptions, requirements
        except AttributeError:
            return None, None

    def get_company_info(self, bs_obj):
        """
        获取提供职位的公司相关信息，公司规模，业务领域，融资信息等
        :param bs_obj: 从网页构造的BeautifulSoup对象
        :return: tuple (公司规模, 业务领域, 融资信息)
        """
        try:
            info_obj = bs_obj.find("div", {"class": "plate company_information"})
            ci_obj = info_obj.findAll("dl", {"class": "ci_body"})[1]
            info_item_obj = ci_obj.findAll("dd")
            info_items = [item.get_text() for item in info_item_obj]
            logging.debug("公司信息: %s" % info_items)
            return info_items[0].strip(), info_items[1].strip(), info_items[2].strip()
        except (AttributeError, IndexError):
            return None, None, None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    test_links = ["/j/467362", "/j/704560", "/j/730233"]
    for link in test_links:
        job_detail = ItemDetail(link)
