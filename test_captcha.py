#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 23:45
@Author  : Manus AI
@File    : test_captcha.py
@Desc    : 验证码识别测试脚本
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.engine import CrawlerEngine
from loguru import logger


def test_captcha():
    """测试验证码识别功能"""
    
    print("=" * 80)
    print("验证码识别测试")
    print("=" * 80)
    print("\n此脚本将访问招标网站并测试验证码识别功能\n")
    
    # 初始化爬虫引擎（非无头模式，可以看到浏览器操作）
    print("1. 初始化爬虫引擎（浏览器可见模式）...")
    crawler_engine = CrawlerEngine(headless=False)
    
    try:
        # 启动浏览器
        print("\n2. 启动浏览器...")
        crawler_engine.start()
        
        # 测试访问列表页
        print("\n3. 访问招标公告列表页...")
        test_url = "https://www.okcis.cn/bn/"
        
        print(f"   URL: {test_url}")
        print("   正在访问...")
        
        content = crawler_engine.fetch_page(test_url)
        
        if content:
            print("\n✅ 页面访问成功！")
            print(f"   页面内容长度: {len(content)} 字符")
            print("\n验证码识别功能正常工作！")
        else:
            print("\n❌ 页面访问失败")
            print("   可能的原因:")
            print("   1. 验证码识别失败（已重试3次）")
            print("   2. 网络连接问题")
            print("   3. 网站结构变化")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        logger.exception(e)
    
    finally:
        # 停止爬虫引擎
        print("\n4. 关闭浏览器...")
        crawler_engine.stop()
        print("✅ 测试结束")
        
        print("\n提示:")
        print("  - 如果验证码识别失败，请检查 PaddleOCR 是否正确安装")
        print("  - 验证码图片保存在 /tmp/bid_monitor_captcha/ 目录")
        print("  - 可以查看保存的图片来判断识别失败的原因")


if __name__ == "__main__":
    test_captcha()
