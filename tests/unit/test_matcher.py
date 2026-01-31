#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 17:15
@Author  : Manus AI
@File    : test_matcher.py
@Desc    : 关键词匹配器单元测试
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from app.core.matcher import KeywordMatcher


class TestKeywordMatcher:
    """测试关键词匹配器"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.keywords = [
            {'keyword': '广告', 'weight': 1.5},
            {'keyword': '标识', 'weight': 1.2},
            {'keyword': '宣传', 'weight': 1.3},
            {'keyword': '文化', 'weight': 1.1},
        ]
        self.matcher = KeywordMatcher(self.keywords)

    def test_calculate_match_score_single_keyword(self):
        """测试单个关键词匹配"""
        text = "某市广告牌制作项目"
        score, details = self.matcher.calculate_match_score(text)

        assert score > 0
        assert '广告' in details
        assert details['广告'] == 1

    def test_calculate_match_score_multiple_keywords(self):
        """测试多个关键词匹配"""
        text = "某市文化广场标识标牌制作安装项目，包括宣传栏、广告牌等"
        score, details = self.matcher.calculate_match_score(text)

        assert score > 0
        assert '广告' in details
        assert '标识' in details
        assert '宣传' in details
        assert '文化' in details

    def test_calculate_match_score_no_match(self):
        """测试无匹配"""
        text = "某市道路建设项目"
        score, details = self.matcher.calculate_match_score(text)

        assert score == 0.0
        assert len(details) == 0

    def test_is_relevant(self):
        """测试相关性判断"""
        text1 = "某市文化广场标识标牌制作项目"
        text2 = "某市道路建设项目"

        assert self.matcher.is_relevant(text1, threshold=2.0) is True
        assert self.matcher.is_relevant(text2, threshold=2.0) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
