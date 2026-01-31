#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 19:00
@Author  : Manus AI
@File    : run_dashboard.py
@Desc    : 数据看板启动脚本（项目根目录运行）
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 60)
    print("招投标监控系统 - 数据看板")
    print("=" * 60)
    print("\n提示: 请使用以下命令启动看板:")
    print("  streamlit run dashboard/main_dashboard.py")
    print("\n或者直接运行:")
    print("  python -m streamlit run dashboard/main_dashboard.py")
