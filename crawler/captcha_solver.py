#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 15:20
@Author  : Manus AI
@File    : captcha_solver.py
@Desc    : 验证码识别模块 - 使用PaddleOCR识别算术验证码
"""

import re
from typing import Optional
from paddleocr import PaddleOCR
from loguru import logger


class CaptchaSolver:
    """算术验证码识别器"""

    def __init__(self):
        """初始化PaddleOCR"""
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='ch',
                use_gpu=False,
                show_log=False
            )
            logger.info("PaddleOCR初始化成功")
        except Exception as e:
            logger.error(f"PaddleOCR初始化失败: {e}")
            raise

    def solve(self, image_path: str) -> Optional[int]:
        """
        识别验证码图片并计算结果

        :param image_path: 验证码图片路径
        :return: 计算结果（整数），识别失败返回None
        """
        try:
            # OCR识别
            result = self.ocr.ocr(image_path, cls=True)

            if not result or not result[0]:
                logger.warning(f"OCR未识别到文字: {image_path}")
                return None

            # 提取识别的文字
            text = " ".join([line[1][0] for line in result[0]])
            logger.debug(f"OCR识别原始文本: {text}")

            # 解析算术表达式
            answer = self._parse_expression(text)
            if answer is not None:
                logger.info(f"验证码识别成功: {text} = {answer}")
            else:
                logger.warning(f"验证码解析失败: {text}")

            return answer

        except Exception as e:
            logger.error(f"验证码识别异常: {e}")
            return None

    def _parse_expression(self, text: str) -> Optional[int]:
        """
        解析算术表达式

        :param text: OCR识别的文本
        :return: 计算结果
        """
        try:
            # 清理文本，移除空格和特殊字符
            text = text.replace(" ", "").replace("=", "").replace("?", "").replace("？", "")

            # 替换中文运算符为Python运算符
            text = text.replace("×", "*").replace("X", "*").replace("x", "*")
            text = text.replace("÷", "/")
            text = text.replace("加", "+").replace("减", "-").replace("乘", "*").replace("除", "/")

            # 提取数字和运算符（支持多位数）
            pattern = r'(\d+|[+\-*/()])'
            tokens = re.findall(pattern, text)

            if not tokens:
                return None

            # 拼接表达式
            expression = "".join(tokens)
            logger.debug(f"解析后的表达式: {expression}")

            # 计算结果
            result = eval(expression)

            # 确保返回整数
            return int(result)

        except Exception as e:
            logger.error(f"表达式解析失败: {text}, 错误: {e}")
            return None


if __name__ == "__main__":
    # 测试代码
    solver = CaptchaSolver()
    # test_result = solver.solve("test_captcha.png")
    # print(f"测试结果: {test_result}")
