#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 16:40
@Author  : Manus AI
@File    : notifier.py
@Desc    : 消息推送模块，支持企业微信和钉钉
"""

import os
import requests
from typing import Dict, List
from loguru import logger


class Notifier:
    """消息推送器"""

    def __init__(self):
        """初始化推送器，从环境变量读取Webhook URL"""
        self.wecom_webhook = os.getenv('WECOM_WEBHOOK_URL')
        self.dingtalk_webhook = os.getenv('DINGTALK_WEBHOOK_URL')

        if not self.wecom_webhook and not self.dingtalk_webhook:
            logger.warning("未配置任何推送渠道的Webhook URL")

    def send_alert(self, project: Dict, match_details: Dict[str, int]) -> bool:
        """
        发送项目预警消息

        :param project: 项目数据字典
        :param match_details: 关键词匹配详情
        :return: 是否发送成功
        """
        success = False

        # 构建消息内容
        message = self._build_message(project, match_details)

        # 发送到企业微信
        if self.wecom_webhook:
            if self._send_to_wecom(message):
                logger.info(f"企业微信推送成功: {project['title']}")
                success = True

        # 发送到钉钉
        if self.dingtalk_webhook:
            if self._send_to_dingtalk(message):
                logger.info(f"钉钉推送成功: {project['title']}")
                success = True

        return success

    def _build_message(self, project: Dict, match_details: Dict[str, int]) -> str:
        """
        构建消息内容

        :param project: 项目数据
        :param match_details: 匹配详情
        :return: 格式化的消息文本
        """
        # 格式化匹配关键词
        keywords_str = ", ".join([f"{kw}({count}次)" for kw, count in match_details.items()])

        message = f"""
🔔 **招标机会预警**

**项目标题**: {project.get('title', '未知')}

**匹配分数**: {project.get('match_score', 0):.2f}
**匹配关键词**: {keywords_str}

**业主单位**: {project.get('owner_unit', '未知')}
**预算金额**: {project.get('budget', '未知')} 万元
**报名截止**: {project.get('registration_end', '未知')}
**开标时间**: {project.get('bidding_time', '未知')}
**实施地址**: {project.get('location', '未知')}

**详情链接**: {project.get('source_url', '')}

---
*招投标监控系统自动推送*
        """.strip()

        return message

    def _send_to_wecom(self, message: str) -> bool:
        """
        发送消息到企业微信

        :param message: 消息内容
        :return: 是否成功
        """
        try:
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": message
                }
            }

            response = requests.post(
                self.wecom_webhook,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    return True
                else:
                    logger.error(f"企业微信推送失败: {result.get('errmsg')}")
            else:
                logger.error(f"企业微信推送失败: HTTP {response.status_code}")

            return False

        except Exception as e:
            logger.error(f"企业微信推送异常: {e}")
            return False

    def _send_to_dingtalk(self, message: str) -> bool:
        """
        发送消息到钉钉

        :param message: 消息内容
        :return: 是否成功
        """
        try:
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "招标机会预警",
                    "text": message
                }
            }

            response = requests.post(
                self.dingtalk_webhook,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    return True
                else:
                    logger.error(f"钉钉推送失败: {result.get('errmsg')}")
            else:
                logger.error(f"钉钉推送失败: HTTP {response.status_code}")

            return False

        except Exception as e:
            logger.error(f"钉钉推送异常: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    notifier = Notifier()

    test_project = {
        'title': '某市文化广场标识标牌制作安装项目',
        'match_score': 5.2,
        'owner_unit': '某市文化局',
        'budget': 500,
        'registration_end': '2026-02-15 17:00',
        'bidding_time': '2026-02-20 09:00',
        'location': '某市文化广场',
        'source_url': 'https://www.okcis.cn/test.html'
    }

    test_match_details = {
        '广告': 2,
        '标识': 3,
        '宣传': 1,
        '文化': 2
    }

    # notifier.send_alert(test_project, test_match_details)
