#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 15:00
@Author  : Manus AI
@File    : base_parser.py
@Desc    : 解析器抽象基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseParser(ABC):
    """所有网站解析器的抽象基类，定义了标准接口。"""

    @abstractmethod
    def get_list_urls(self, page_content: str) -> List[str]:
        """
        从列表页的HTML内容中解析出所有详情页的URL链接。

        :param page_content: 列表页的HTML字符串。
        :return: 一个包含所有详情页URL的列表。
        """
        pass

    @abstractmethod
    def parse_detail_page(self, page_content: str) -> Dict[str, Any]:
        """
        从详情页的HTML内容中解析出结构化的招标项目信息。

        :param page_content: 详情页的HTML字符串。
        :return: 一个包含结构化项目信息的字典，字段需与数据库模型对应。
        """
        pass
