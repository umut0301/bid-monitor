#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 15:45
@Author  : Manus AI
@File    : okcis_parser.py
@Desc    : 招标采购导航网(okcis.cn)解析器
"""

import re
import hashlib
from typing import List, Dict, Any
from selectolax.parser import HTMLParser
from loguru import logger

from crawler.parsers.base_parser import BaseParser


class OkcisParser(BaseParser):
    """招标采购导航网解析器"""

    BASE_URL = "https://www.okcis.cn"

    def get_list_urls(self, page_content: str) -> List[str]:
        """
        从列表页解析所有详情页URL

        :param page_content: 列表页HTML
        :return: 详情页URL列表
        """
        urls = []
        try:
            tree = HTMLParser(page_content)

            # 查找所有招标公告链接（根据实际HTML结构调整选择器）
            # 示例：<a hint="标题">...</a>
            links = tree.css('a[hint]')

            for link in links:
                href = link.attributes.get('href')
                if href and href.startswith('/'):
                    full_url = self.BASE_URL + href
                    urls.append(full_url)
                elif href and href.startswith('http'):
                    urls.append(href)

            logger.info(f"从列表页解析到 {len(urls)} 个URL")

        except Exception as e:
            logger.error(f"列表页URL解析失败: {e}")

        return urls

    def parse_detail_page(self, page_content: str) -> Dict[str, Any]:
        """
        从详情页解析招标项目信息

        :param page_content: 详情页HTML
        :return: 结构化项目数据
        """
        data = {
            'project_id': None,
            'source_url': None,
            'title': None,
            'owner_unit': None,
            'procurement_type': None,
            'budget': None,
            'registration_start': None,
            'registration_end': None,
            'bidding_time': None,
            'location': None,
            'content_raw': page_content,
            'content_text': None
        }

        try:
            tree = HTMLParser(page_content)

            # 1. 提取标题
            title_node = tree.css_first('h1, .title, #title')
            if title_node:
                data['title'] = title_node.text(strip=True)

            # 2. 提取正文内容
            content_node = tree.css_first('.content, #content, .detail')
            if content_node:
                data['content_text'] = content_node.text(strip=True)
            else:
                # 如果没有特定class，提取body文本
                body = tree.css_first('body')
                if body:
                    data['content_text'] = body.text(strip=True)

            # 3. 提取业主单位（通过正则匹配）
            if data['content_text']:
                owner_match = re.search(r'(业主单位|招标人|采购人)[：:]\s*([^\n]+)', data['content_text'])
                if owner_match:
                    data['owner_unit'] = owner_match.group(2).strip()

            # 4. 提取预算金额（通过正则匹配）
            if data['content_text']:
                budget_match = re.search(r'(预算|总投资|投资额)[：:]\s*([\d,.]+)\s*(万元|元)', data['content_text'])
                if budget_match:
                    amount_str = budget_match.group(2).replace(',', '')
                    unit = budget_match.group(3)
                    amount = float(amount_str)
                    # 统一转换为万元
                    if unit == '元':
                        amount = amount / 10000
                    data['budget'] = round(amount, 2)

            # 5. 提取时间信息（报名截止、开标时间）
            if data['content_text']:
                # 报名截止时间
                reg_end_match = re.search(r'(报名截止|投标截止)[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?\s*\d{1,2}:\d{2})', data['content_text'])
                if reg_end_match:
                    data['registration_end'] = self._parse_datetime(reg_end_match.group(2))

                # 开标时间
                bid_time_match = re.search(r'(开标时间)[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?\s*\d{1,2}:\d{2})', data['content_text'])
                if bid_time_match:
                    data['bidding_time'] = self._parse_datetime(bid_time_match.group(2))

            # 6. 提取地址
            if data['content_text']:
                location_match = re.search(r'(项目地址|实施地点|地址)[：:]\s*([^\n]+)', data['content_text'])
                if location_match:
                    data['location'] = location_match.group(2).strip()

            # 7. 生成project_id（使用URL的MD5）
            if data['title']:
                data['project_id'] = hashlib.md5(data['title'].encode('utf-8')).hexdigest()

            logger.info(f"详情页解析成功: {data['title']}")

        except Exception as e:
            logger.error(f"详情页解析失败: {e}")

        return data

    def _parse_datetime(self, datetime_str: str) -> str:
        """
        解析日期时间字符串，转换为标准格式

        :param datetime_str: 原始日期时间字符串
        :return: 标准格式日期时间（YYYY-MM-DD HH:MM:SS）
        """
        try:
            # 替换中文字符
            datetime_str = datetime_str.replace('年', '-').replace('月', '-').replace('日', '')
            # 简单处理，实际应使用dateutil.parser
            return datetime_str.strip()
        except Exception as e:
            logger.warning(f"日期解析失败: {datetime_str}, 错误: {e}")
            return None


if __name__ == "__main__":
    # 测试代码
    parser = OkcisParser()

    # 测试列表页解析
    test_list_html = """
    <html>
        <body>
            <a hint="测试项目1" href="/20260131-n1.html">项目1</a>
            <a hint="测试项目2" href="/20260131-n2.html">项目2</a>
        </body>
    </html>
    """
    urls = parser.get_list_urls(test_list_html)
    print(f"解析到的URL: {urls}")

    # 测试详情页解析
    test_detail_html = """
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
    data = parser.parse_detail_page(test_detail_html)
    print(f"解析到的数据: {data}")
