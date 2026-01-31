#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 15:30
@Author  : Manus AI
@File    : engine.py
@Desc    : 爬虫核心引擎，集成Playwright和OCR验证码识别
"""

import time
import random
from pathlib import Path
from typing import Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from crawler.captcha_solver import CaptchaSolver


class CrawlerEngine:
    """爬虫引擎，负责浏览器控制和验证码处理"""

    def __init__(self, headless: bool = True):
        """
        初始化爬虫引擎

        :param headless: 是否使用无头模式
        """
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.captcha_solver = CaptchaSolver()
        self.temp_dir = Path("/tmp/bid_monitor_captcha")
        self.temp_dir.mkdir(exist_ok=True)

    def start(self):
        """启动浏览器"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )

            # 创建浏览器上下文，模拟真实用户
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='zh-CN',
                timezone_id='Asia/Shanghai'
            )

            logger.info("浏览器启动成功")
        except Exception as e:
            logger.error(f"浏览器启动失败: {e}")
            raise

    def stop(self):
        """关闭浏览器"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"浏览器关闭异常: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
    def fetch_page(self, url: str) -> Optional[str]:
        """
        获取页面内容，自动处理验证码

        :param url: 目标URL
        :return: 页面HTML内容，失败返回None
        """
        page = None
        try:
            page = self.context.new_page()
            logger.info(f"正在访问: {url}")

            # 访问页面
            page.goto(url, wait_until='domcontentloaded', timeout=30000)

            # 随机等待，模拟人类行为
            time.sleep(random.uniform(1, 3))

            # 检查是否有验证码
            if self._has_captcha(page):
                logger.info("检测到验证码，开始识别...")
                success = self._solve_captcha(page)
                if not success:
                    logger.error("验证码识别失败")
                    return None

                # 验证码通过后，等待页面加载
                page.wait_for_load_state('domcontentloaded', timeout=10000)
                time.sleep(random.uniform(1, 2))

            # 获取页面内容
            content = page.content()
            logger.info(f"页面获取成功: {url}")
            return content

        except Exception as e:
            logger.error(f"页面获取失败: {url}, 错误: {e}")
            raise  # 让retry装饰器处理重试

        finally:
            if page:
                page.close()

    def _has_captcha(self, page: Page) -> bool:
        """
        检测页面是否包含验证码

        :param page: Playwright页面对象
        :return: True表示有验证码
        """
        try:
            # 检查标题或特定元素
            title = page.title()
            if "验证码" in title:
                return True

            # 检查验证码输入框
            captcha_input = page.locator('input[placeholder*="验证"]').count()
            if captcha_input > 0:
                return True

            return False

        except Exception as e:
            logger.warning(f"验证码检测异常: {e}")
            return False

    def _solve_captcha(self, page: Page) -> bool:
        """
        识别并提交验证码

        :param page: Playwright页面对象
        :return: True表示验证成功
        """
        try:
            # 定位验证码图片
            captcha_img = page.locator('img').first

            if captcha_img.count() == 0:
                logger.error("未找到验证码图片")
                return False

            # 截取验证码图片
            img_path = self.temp_dir / f"captcha_{int(time.time())}.png"
            captcha_img.screenshot(path=str(img_path))
            logger.debug(f"验证码图片已保存: {img_path}")

            # OCR识别
            answer = self.captcha_solver.solve(str(img_path))
            if answer is None:
                logger.error("验证码识别失败")
                return False

            # 填写答案
            input_box = page.locator('input[type="text"]').first
            input_box.fill(str(answer))

            # 点击验证按钮
            submit_btn = page.locator('input[type="submit"]').first
            submit_btn.click()

            # 等待验证结果
            time.sleep(2)

            # 检查是否验证成功（如果还在验证码页面则失败）
            if self._has_captcha(page):
                logger.error("验证码提交后仍在验证页面，可能答案错误")
                return False

            logger.info("验证码验证成功")
            return True

        except Exception as e:
            logger.error(f"验证码处理异常: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    engine = CrawlerEngine(headless=False)
    engine.start()

    try:
        # 测试访问招标公告列表页
        content = engine.fetch_page("https://www.okcis.cn/bn/")
        if content:
            print(f"页面内容长度: {len(content)}")
            print("前500字符:")
            print(content[:500])
    finally:
        engine.stop()
