#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 17:10
@Author  : Manus AI
@File    : test_parser.py
@Desc    : 解析器单元测试
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from crawler.parsers.okcis_parser import OkcisParser


class TestOkcisParser:
    """测试招标采购导航网解析器"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.parser = OkcisParser()

    def test_get_list_urls(self):
        """测试列表页URL解析"""
        test_html = """
        <html>
            <body>
                <a hint="测试项目1" href="/20260131-n1.html">项目1</a>
                <a hint="测试项目2" href="/20260131-n2.html">项目2</a>
                <a href="https://www.okcis.cn/20260131-n3.html">项目3</a>
            </body>
        </html>
        """

        urls = self.parser.get_list_urls(test_html)

        assert len(urls) == 2  # 只有带hint属性的链接会被解析
        assert "https://www.okcis.cn/20260131-n1.html" in urls
        assert "https://www.okcis.cn/20260131-n2.html" in urls

    def test_parse_detail_page(self):
        """测试详情页解析"""
        test_html = """
        <html>
            <body>
                <h1>某市文化广场标识标牌制作安装项目招标公告</h1>
                <div class="content">
                    业主单位: 某市文化局
                    预算: 500万元
                    报名截止: 2026-02-15 17:00
                    开标时间: 2026-02-20 09:00
                    项目地址: 某市文化广场
                    项目内容: 制作安装文化广场标识标牌、宣传栏等。
                </div>
            </body>
        </html>
        """

        data = self.parser.parse_detail_page(test_html)

        assert data['title'] == '某市文化广场标识标牌制作安装项目招标公告'
        assert data['owner_unit'] == '某市文化局'
        assert data['budget'] == 500.0
        assert data['location'] == '某市文化广场'
        assert data['project_id'] is not None

    def test_parse_detail_page_empty(self):
        """测试空详情页"""
        test_html = "<html><body></body></html>"

        data = self.parser.parse_detail_page(test_html)

        assert data['title'] is None
        assert data['owner_unit'] is None
        assert data['budget'] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
