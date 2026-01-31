#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 16:10
@Author  : Manus AI
@File    : database.py
@Desc    : 数据库连接和会话管理
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from app.models.bid_project import Base

# 从环境变量读取数据库配置
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/bid_monitor'
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """初始化数据库：创建表和索引"""
    try:
        logger.info("开始初始化数据库...")

        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")

        # 创建全文检索索引
        with engine.connect() as conn:
            # 检查索引是否存在
            result = conn.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'bid_projects' AND indexname = 'idx_content_fts';
            """))

            if not result.fetchone():
                conn.execute(text("""
                    CREATE INDEX idx_content_fts ON bid_projects USING GIN(content_tsvector);
                """))
                conn.commit()
                logger.info("全文检索索引创建成功")

            # 创建其他索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_match_score ON bid_projects(match_score DESC);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON bid_projects(created_at DESC);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_registration_end ON bid_projects(registration_end DESC);
            """))
            conn.commit()
            logger.info("其他索引创建成功")

        # 初始化关键词数据
        _init_keywords()

        logger.info("数据库初始化完成")

    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def _init_keywords():
    """初始化关键词数据"""
    from app.models.bid_project import Keyword

    keywords_data = [
        {'keyword': '广告', 'weight': 1.5, 'category': '广告类'},
        {'keyword': '标识', 'weight': 1.2, 'category': '标识类'},
        {'keyword': '牌', 'weight': 1.0, 'category': '标识类'},
        {'keyword': '标志', 'weight': 1.2, 'category': '标识类'},
        {'keyword': '宣传', 'weight': 1.3, 'category': '宣传类'},
        {'keyword': '栏', 'weight': 1.0, 'category': '宣传类'},
        {'keyword': '文化', 'weight': 1.1, 'category': '文化类'},
    ]

    db = SessionLocal()
    try:
        for kw_data in keywords_data:
            # 检查是否已存在
            existing = db.query(Keyword).filter(Keyword.keyword == kw_data['keyword']).first()
            if not existing:
                keyword = Keyword(
                    id=f"kw_{kw_data['keyword']}",
                    **kw_data
                )
                db.add(keyword)

        db.commit()
        logger.info("关键词数据初始化成功")

    except Exception as e:
        db.rollback()
        logger.error(f"关键词初始化失败: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    # 测试数据库连接
    init_database()
