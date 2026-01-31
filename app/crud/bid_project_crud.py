#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 16:20
@Author  : Manus AI
@File    : bid_project_crud.py
@Desc    : 招标项目的数据库操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from loguru import logger

from app.models.bid_project import BidProject, Keyword


def create_bid_project(db: Session, project_data: dict) -> Optional[BidProject]:
    """
    创建招标项目记录

    :param db: 数据库会话
    :param project_data: 项目数据字典
    :return: 创建的项目对象
    """
    try:
        # 检查是否已存在
        existing = db.query(BidProject).filter(
            BidProject.project_id == project_data['project_id']
        ).first()

        if existing:
            logger.warning(f"项目已存在: {project_data['project_id']}")
            return existing

        # 创建tsvector（全文检索向量）
        if project_data.get('content_text'):
            project_data['content_tsvector'] = func.to_tsvector('chinese', project_data['content_text'])

        # 创建新项目
        project = BidProject(**project_data)
        db.add(project)
        db.commit()
        db.refresh(project)

        logger.info(f"项目创建成功: {project.project_id}")
        return project

    except Exception as e:
        db.rollback()
        logger.error(f"项目创建失败: {e}")
        return None


def get_bid_project(db: Session, project_id: str) -> Optional[BidProject]:
    """
    根据ID获取项目

    :param db: 数据库会话
    :param project_id: 项目ID
    :return: 项目对象
    """
    return db.query(BidProject).filter(BidProject.project_id == project_id).first()


def get_projects_by_score(db: Session, min_score: float = 0.0, limit: int = 100) -> List[BidProject]:
    """
    根据匹配分数获取项目列表

    :param db: 数据库会话
    :param min_score: 最低分数
    :param limit: 返回数量限制
    :return: 项目列表
    """
    return db.query(BidProject).filter(
        BidProject.match_score >= min_score
    ).order_by(
        BidProject.match_score.desc()
    ).limit(limit).all()


def search_projects_by_keywords(db: Session, keywords: List[str], limit: int = 100) -> List[BidProject]:
    """
    使用PostgreSQL全文检索搜索项目

    :param db: 数据库会话
    :param keywords: 关键词列表
    :param limit: 返回数量限制
    :return: 项目列表
    """
    try:
        # 构建搜索查询
        query_str = ' | '.join(keywords)  # 使用OR逻辑

        results = db.query(BidProject).filter(
            text(f"content_tsvector @@ to_tsquery('chinese', '{query_str}')")
        ).order_by(
            BidProject.created_at.desc()
        ).limit(limit).all()

        return results

    except Exception as e:
        logger.error(f"全文检索失败: {e}")
        return []


def get_all_keywords(db: Session) -> List[Keyword]:
    """
    获取所有启用的关键词

    :param db: 数据库会话
    :return: 关键词列表
    """
    return db.query(Keyword).filter(Keyword.is_active == 'true').all()


def update_match_score(db: Session, project_id: str, score: float) -> bool:
    """
    更新项目的匹配分数

    :param db: 数据库会话
    :param project_id: 项目ID
    :param score: 匹配分数
    :return: 是否成功
    """
    try:
        project = get_bid_project(db, project_id)
        if project:
            project.match_score = score
            db.commit()
            logger.info(f"项目 {project_id} 匹配分数更新为 {score}")
            return True
        return False

    except Exception as e:
        db.rollback()
        logger.error(f"匹配分数更新失败: {e}")
        return False
