#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 19:00
@Author  : Manus AI
@File    : run_crawler.py
@Desc    : 爬虫启动脚本（项目根目录运行）
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.scheduler import BidMonitorScheduler

if __name__ == "__main__":
    print("=" * 60)
    print("招投标监控系统 - 爬虫调度器")
    print("=" * 60)
    print("\n启动中...")
    
    # 启动调度器
    scheduler = BidMonitorScheduler(headless=True)
    scheduler.start()
