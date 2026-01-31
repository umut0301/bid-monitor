#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 16:30
@Author  : Manus AI
@File    : matcher.py
@Desc    : 关键词匹配与评分算法
"""

import re
from typing import List, Dict, Tuple
from loguru import logger


class KeywordMatcher:
    """关键词匹配器"""

    def __init__(self, keywords: List[Dict[str, any]]):
        """
        初始化匹配器

        :param keywords: 关键词列表，每个元素包含 {'keyword': str, 'weight': float}
        """
        self.keywords = keywords
        logger.info(f"关键词匹配器初始化完成，共 {len(keywords)} 个关键词")

    def calculate_match_score(self, text: str) -> Tuple[float, Dict[str, int]]:
        """
        计算文本的关键词匹配分数

        :param text: 待匹配的文本（标题+正文）
        :return: (总分数, 各关键词出现次数字典)
        """
        if not text:
            return 0.0, {}

        total_score = 0.0
        match_details = {}

        for kw_data in self.keywords:
            keyword = kw_data['keyword']
            weight = kw_data['weight']

            # 统计关键词出现次数
            count = len(re.findall(keyword, text))

            if count > 0:
                match_details[keyword] = count
                # 计算分数：出现次数 × 权重
                # 使用对数函数避免单个关键词出现过多次导致分数过高
                score = weight * (1 + 0.5 * (count - 1))  # 第一次出现得满分，后续递减
                total_score += score

                logger.debug(f"关键词 '{keyword}' 出现 {count} 次，得分 {score:.2f}")

        logger.info(f"文本匹配总分: {total_score:.2f}, 匹配关键词: {list(match_details.keys())}")
        return round(total_score, 2), match_details

    def is_relevant(self, text: str, threshold: float = 1.0) -> bool:
        """
        判断文本是否与业务相关

        :param text: 待判断的文本
        :param threshold: 分数阈值
        :return: True表示相关
        """
        score, _ = self.calculate_match_score(text)
        return score >= threshold


if __name__ == "__main__":
    # 测试代码
    test_keywords = [
        {'keyword': '广告', 'weight': 1.5},
        {'keyword': '标识', 'weight': 1.2},
        {'keyword': '宣传', 'weight': 1.3},
        {'keyword': '文化', 'weight': 1.1},
    ]

    matcher = KeywordMatcher(test_keywords)

    # 测试文本
    test_text = """
    某市文化广场标识标牌制作安装项目招标公告
    项目内容：制作安装文化广场标识标牌、宣传栏、广告牌等。
    本项目包括文化宣传设施的设计、制作和安装。
    """

    score, details = matcher.calculate_match_score(test_text)
    print(f"匹配分数: {score}")
    print(f"匹配详情: {details}")
    print(f"是否相关: {matcher.is_relevant(test_text, threshold=3.0)}")
