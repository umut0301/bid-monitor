#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 16:50
@Author  : Manus AI
@File    : scheduler.py
@Desc    : 定时任务调度器
"""

import uuid
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from crawler.engine import CrawlerEngine
from crawler.parsers.okcis_parser import OkcisParser
from app.core.database import SessionLocal, init_database
from app.crud.bid_project_crud import create_bid_project, get_all_keywords, update_match_score
from app.core.matcher import KeywordMatcher
from app.core.notifier import Notifier
from app.models.bid_project import CrawlLog


class BidMonitorScheduler:
    """招投标监控调度器"""

    def __init__(self, headless: bool = True):
        """
        初始化调度器

        :param headless: 是否使用无头浏览器
        """
        self.scheduler = BlockingScheduler()
        self.crawler_engine = CrawlerEngine(headless=headless)
        self.parser = OkcisParser()
        self.notifier = Notifier()
        self.alert_threshold = 2.0  # 预警阈值

        logger.info("调度器初始化完成")

    def start(self):
        """启动调度器"""
        try:
            # 初始化数据库
            init_database()

            # 添加定时任务（每小时执行一次）
            self.scheduler.add_job(
                self.crawl_and_alert,
                trigger=CronTrigger(hour='*', minute='0'),  # 每小时整点执行
                id='crawl_job',
                name='招标信息爬取任务',
                replace_existing=True
            )

            logger.info("定时任务已添加：每小时执行一次")

            # 立即执行一次
            logger.info("执行首次爬取任务...")
            self.crawl_and_alert()

            # 启动调度器
            logger.info("调度器启动，等待定时任务...")
            self.scheduler.start()

        except (KeyboardInterrupt, SystemExit):
            logger.info("调度器停止")
            self.stop()

    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
        self.crawler_engine.stop()
        logger.info("调度器已停止")

    def crawl_and_alert(self):
        """爬取任务：抓取数据、匹配关键词、发送预警"""
        task_id = str(uuid.uuid4())
        start_time = datetime.now()

        logger.info(f"开始执行爬取任务，任务ID: {task_id}")

        # 创建日志记录
        db = SessionLocal()
        crawl_log = CrawlLog(
            id=str(uuid.uuid4()),
            task_id=task_id,
            start_time=start_time,
            status='running'
        )
        db.add(crawl_log)
        db.commit()

        total_fetched = 0
        success_count = 0
        failed_count = 0

        try:
            # 启动爬虫引擎
            self.crawler_engine.start()

            # 1. 获取列表页
            list_url = "https://www.okcis.cn/bn/"
            list_content = self.crawler_engine.fetch_page(list_url)

            if not list_content:
                logger.error("列表页获取失败")
                crawl_log.status = 'failed'
                crawl_log.error_message = '列表页获取失败'
                db.commit()
                return

            # 2. 解析列表页，获取详情页URL
            detail_urls = self.parser.get_list_urls(list_content)
            total_fetched = len(detail_urls)
            logger.info(f"从列表页解析到 {total_fetched} 个详情页URL")

            # 3. 获取关键词配置
            keywords = get_all_keywords(db)
            keyword_data = [{'keyword': kw.keyword, 'weight': kw.weight} for kw in keywords]
            matcher = KeywordMatcher(keyword_data)

            # 4. 遍历详情页
            for url in detail_urls[:10]:  # 限制每次处理10条（测试阶段）
                try:
                    # 获取详情页内容
                    detail_content = self.crawler_engine.fetch_page(url)
                    if not detail_content:
                        failed_count += 1
                        continue

                    # 解析详情页
                    project_data = self.parser.parse_detail_page(detail_content)
                    project_data['source_url'] = url

                    if not project_data.get('title'):
                        logger.warning(f"详情页解析失败，未提取到标题: {url}")
                        failed_count += 1
                        continue

                    # 关键词匹配
                    match_text = f"{project_data.get('title', '')} {project_data.get('content_text', '')}"
                    score, match_details = matcher.calculate_match_score(match_text)
                    project_data['match_score'] = score

                    # 保存到数据库
                    project = create_bid_project(db, project_data)
                    if project:
                        success_count += 1

                        # 如果分数达到阈值，发送预警
                        if score >= self.alert_threshold:
                            logger.info(f"项目达到预警阈值，准备推送: {project.title}")
                            self.notifier.send_alert(
                                {
                                    'title': project.title,
                                    'match_score': project.match_score,
                                    'owner_unit': project.owner_unit,
                                    'budget': project.budget,
                                    'registration_end': project.registration_end,
                                    'bidding_time': project.bidding_time,
                                    'location': project.location,
                                    'source_url': project.source_url
                                },
                                match_details
                            )
                    else:
                        failed_count += 1

                except Exception as e:
                    logger.error(f"处理详情页失败: {url}, 错误: {e}")
                    failed_count += 1

            # 更新日志
            crawl_log.end_time = datetime.now()
            crawl_log.total_fetched = str(total_fetched)
            crawl_log.success_count = str(success_count)
            crawl_log.failed_count = str(failed_count)
            crawl_log.status = 'success'
            db.commit()

            logger.info(f"爬取任务完成，成功: {success_count}, 失败: {failed_count}")

        except Exception as e:
            logger.error(f"爬取任务异常: {e}")
            crawl_log.status = 'failed'
            crawl_log.error_message = str(e)
            crawl_log.end_time = datetime.now()
            db.commit()

        finally:
            db.close()
            self.crawler_engine.stop()


if __name__ == "__main__":
    # 启动调度器
    scheduler = BidMonitorScheduler(headless=True)
    scheduler.start()
