#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 16:00
@Author  : Manus AI
@File    : bid_project.py
@Desc    : 招标项目数据库模型
"""

from sqlalchemy import Column, String, Text, Numeric, TIMESTAMP, Float, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BidProject(Base):
    """招标项目表"""

    __tablename__ = 'bid_projects'

    project_id = Column(String(100), primary_key=True, comment='唯一标识')
    source_url = Column(Text, nullable=False, comment='原始链接')
    title = Column(Text, nullable=False, comment='标题')
    owner_unit = Column(String(500), comment='业主单位')
    procurement_type = Column(String(50), comment='采购类型')
    budget = Column(Numeric(15, 2), comment='预算金额(万元)')
    registration_start = Column(TIMESTAMP(timezone=True), comment='报名开始时间')
    registration_end = Column(TIMESTAMP(timezone=True), comment='报名截止时间')
    bidding_time = Column(TIMESTAMP(timezone=True), comment='开标时间')
    location = Column(Text, comment='实施地址')
    content_raw = Column(Text, comment='原始正文HTML')
    content_text = Column(Text, comment='提取后的纯文本正文')
    content_tsvector = Column(TSVECTOR, comment='全文检索向量')
    match_score = Column(Float, default=0.0, comment='关键词匹配度评分')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment='抓取时间')
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment='更新时间')

    def __repr__(self):
        return f"<BidProject(project_id='{self.project_id}', title='{self.title}')>"


class Keyword(Base):
    """关键词配置表"""

    __tablename__ = 'keywords'

    id = Column(String(50), primary_key=True)
    keyword = Column(String(50), nullable=False, unique=True, comment='关键词')
    weight = Column(Float, default=1.0, comment='权重')
    category = Column(String(50), comment='分类')
    is_active = Column(String(10), default='true', comment='是否启用')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Keyword(keyword='{self.keyword}', weight={self.weight})>"


class CrawlLog(Base):
    """爬取日志表"""

    __tablename__ = 'crawl_logs'

    id = Column(String(50), primary_key=True)
    task_id = Column(String(50), nullable=False, comment='任务ID')
    start_time = Column(TIMESTAMP(timezone=True), nullable=False, comment='开始时间')
    end_time = Column(TIMESTAMP(timezone=True), comment='结束时间')
    total_fetched = Column(String(10), default='0', comment='抓取总数')
    success_count = Column(String(10), default='0', comment='成功数')
    failed_count = Column(String(10), default='0', comment='失败数')
    error_message = Column(Text, comment='错误信息')
    status = Column(String(20), default='running', comment='状态')

    def __repr__(self):
        return f"<CrawlLog(task_id='{self.task_id}', status='{self.status}')>"
