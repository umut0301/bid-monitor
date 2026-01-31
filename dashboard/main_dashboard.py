#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 17:00
@Author  : Manus AI
@File    : main_dashboard.py
@Desc    : Streamlit数据看板
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.bid_project import BidProject, CrawlLog
from sqlalchemy import func, desc


st.set_page_config(
    page_title="招投标监控系统",
    page_icon="🔍",
    layout="wide"
)


def get_statistics():
    """获取统计数据"""
    db = SessionLocal()
    try:
        # 总项目数
        total_projects = db.query(func.count(BidProject.project_id)).scalar()

        # 今日新增
        today = datetime.now().date()
        today_projects = db.query(func.count(BidProject.project_id)).filter(
            func.date(BidProject.created_at) == today
        ).scalar()

        # 高分项目（>= 3.0）
        high_score_projects = db.query(func.count(BidProject.project_id)).filter(
            BidProject.match_score >= 3.0
        ).scalar()

        # 最近一次爬取时间
        last_crawl = db.query(CrawlLog).order_by(desc(CrawlLog.start_time)).first()
        last_crawl_time = last_crawl.start_time if last_crawl else None

        return {
            'total': total_projects or 0,
            'today': today_projects or 0,
            'high_score': high_score_projects or 0,
            'last_crawl': last_crawl_time
        }
    finally:
        db.close()


def get_recent_projects(limit=20, min_score=0.0):
    """获取最近的项目列表"""
    db = SessionLocal()
    try:
        projects = db.query(BidProject).filter(
            BidProject.match_score >= min_score
        ).order_by(
            desc(BidProject.created_at)
        ).limit(limit).all()

        data = []
        for p in projects:
            data.append({
                '标题': p.title,
                '匹配分数': f"{p.match_score:.2f}",
                '业主单位': p.owner_unit or '未知',
                '预算(万元)': p.budget or '未知',
                '报名截止': p.registration_end or '未知',
                '抓取时间': p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else '',
                '详情链接': p.source_url
            })

        return pd.DataFrame(data)
    finally:
        db.close()


def get_crawl_logs(limit=10):
    """获取爬取日志"""
    db = SessionLocal()
    try:
        logs = db.query(CrawlLog).order_by(desc(CrawlLog.start_time)).limit(limit).all()

        data = []
        for log in logs:
            data.append({
                '任务ID': log.task_id[:8],
                '开始时间': log.start_time.strftime('%Y-%m-%d %H:%M'),
                '结束时间': log.end_time.strftime('%Y-%m-%d %H:%M') if log.end_time else '-',
                '成功数': log.success_count,
                '失败数': log.failed_count,
                '状态': log.status
            })

        return pd.DataFrame(data)
    finally:
        db.close()


def main():
    """主函数"""
    st.title("🔍 招投标监控系统")
    st.markdown("---")

    # 统计数据
    stats = get_statistics()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("总项目数", stats['total'])

    with col2:
        st.metric("今日新增", stats['today'])

    with col3:
        st.metric("高分项目", stats['high_score'])

    with col4:
        if stats['last_crawl']:
            last_crawl_str = stats['last_crawl'].strftime('%H:%M')
            st.metric("最近爬取", last_crawl_str)
        else:
            st.metric("最近爬取", "暂无")

    st.markdown("---")

    # 侧边栏筛选
    st.sidebar.header("筛选条件")
    min_score = st.sidebar.slider("最低匹配分数", 0.0, 10.0, 0.0, 0.5)
    limit = st.sidebar.slider("显示数量", 10, 100, 20, 10)

    # 项目列表
    st.header("📋 最近项目")
    df_projects = get_recent_projects(limit=limit, min_score=min_score)

    if not df_projects.empty:
        # 使用dataframe显示，支持排序
        st.dataframe(
            df_projects,
            use_container_width=True,
            hide_index=True
        )

        # 详情展开
        st.subheader("项目详情")
        selected_title = st.selectbox("选择项目查看详情", df_projects['标题'].tolist())

        if selected_title:
            selected_row = df_projects[df_projects['标题'] == selected_title].iloc[0]
            st.markdown(f"**标题**: {selected_row['标题']}")
            st.markdown(f"**匹配分数**: {selected_row['匹配分数']}")
            st.markdown(f"**业主单位**: {selected_row['业主单位']}")
            st.markdown(f"**预算**: {selected_row['预算(万元)']} 万元")
            st.markdown(f"**报名截止**: {selected_row['报名截止']}")
            st.markdown(f"**详情链接**: [{selected_row['详情链接']}]({selected_row['详情链接']})")
    else:
        st.info("暂无符合条件的项目")

    st.markdown("---")

    # 爬取日志
    st.header("📝 爬取日志")
    df_logs = get_crawl_logs(limit=10)

    if not df_logs.empty:
        st.dataframe(
            df_logs,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无爬取日志")


if __name__ == "__main__":
    main()
