#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 19:00
@Author  : Manus AI
@File    : init_database.py
@Desc    : 数据库初始化脚本（项目根目录运行）
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database

if __name__ == "__main__":
    print("=" * 60)
    print("招投标监控系统 - 数据库初始化")
    print("=" * 60)
    
    try:
        init_database()
        print("\n✅ 数据库初始化成功！")
        print("\n下一步:")
        print("  1. 配置 .env 文件（复制 .env.example 并填写配置）")
        print("  2. 运行爬虫调度器: python crawler/scheduler.py")
        print("  3. 启动数据看板: streamlit run dashboard/main_dashboard.py")
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        print("\n请检查:")
        print("  1. PostgreSQL 服务是否正在运行")
        print("  2. .env 文件中的数据库连接URL是否正确")
        print("  3. 数据库用户是否有足够的权限")
        sys.exit(1)
