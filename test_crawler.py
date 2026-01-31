#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026/01/31 23:40
@Author  : Manus AI
@File    : test_crawler.py
@Desc    : 爬虫测试脚本（不依赖数据库）
"""

import sys
import os
import json
from datetime import datetime

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.engine import CrawlerEngine
from crawler.parsers.okcis_parser import OkcisParser
from app.core.matcher import KeywordMatcher
from loguru import logger


def test_crawler():
    """测试爬虫功能"""
    
    print("=" * 80)
    print("招投标监控系统 - 爬虫功能测试")
    print("=" * 80)
    print("\n⚠️  注意: 此测试脚本不会保存数据到数据库，仅用于验证爬虫功能\n")
    
    # 创建输出目录
    output_dir = "crawler_test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化组件
    print("1. 初始化爬虫引擎...")
    crawler_engine = CrawlerEngine(headless=False)  # 设置为False可以看到浏览器操作
    
    print("2. 初始化解析器...")
    parser = OkcisParser()
    
    print("3. 初始化关键词匹配器...")
    keywords_data = [
        {'keyword': '广告', 'weight': 1.5},
        {'keyword': '标识', 'weight': 1.2},
        {'keyword': '牌', 'weight': 1.0},
        {'keyword': '标志', 'weight': 1.2},
        {'keyword': '宣传', 'weight': 1.3},
        {'keyword': '栏', 'weight': 1.0},
        {'keyword': '文化', 'weight': 1.1},
    ]
    matcher = KeywordMatcher(keywords_data)
    
    results = []
    
    try:
        # 启动爬虫引擎
        print("\n4. 启动浏览器...")
        crawler_engine.start()
        
        # 获取列表页
        print("\n5. 访问招标公告列表页...")
        list_url = "https://www.okcis.cn/bn/"
        list_content = crawler_engine.fetch_page(list_url)
        
        if not list_content:
            print("❌ 列表页获取失败")
            return
        
        print("✅ 列表页获取成功")
        
        # 解析列表页
        print("\n6. 解析列表页URL...")
        detail_urls = parser.get_list_urls(list_content)
        print(f"✅ 从列表页解析到 {len(detail_urls)} 个详情页URL")
        
        if len(detail_urls) == 0:
            print("⚠️  未解析到任何URL，可能需要调整解析器")
            return
        
        # 只测试前3条
        test_count = min(3, len(detail_urls))
        print(f"\n7. 开始爬取前 {test_count} 条详情页...")
        
        for i, url in enumerate(detail_urls[:test_count], 1):
            print(f"\n--- 处理第 {i}/{test_count} 条 ---")
            print(f"URL: {url}")
            
            try:
                # 获取详情页
                detail_content = crawler_engine.fetch_page(url)
                if not detail_content:
                    print(f"❌ 详情页获取失败")
                    continue
                
                print("✅ 详情页获取成功")
                
                # 解析详情页
                project_data = parser.parse_detail_page(detail_content)
                project_data['source_url'] = url
                
                if not project_data.get('title'):
                    print("⚠️  未提取到标题，跳过")
                    continue
                
                print(f"标题: {project_data['title']}")
                
                # 关键词匹配
                match_text = f"{project_data.get('title', '')} {project_data.get('content_text', '')}"
                score, match_details = matcher.calculate_match_score(match_text)
                project_data['match_score'] = score
                project_data['match_details'] = match_details
                
                print(f"匹配分数: {score:.2f}")
                if match_details:
                    print(f"匹配关键词: {match_details}")
                else:
                    print("匹配关键词: 无")
                
                # 保存结果
                results.append({
                    'url': url,
                    'title': project_data.get('title'),
                    'owner_unit': project_data.get('owner_unit'),
                    'budget': project_data.get('budget'),
                    'registration_end': str(project_data.get('registration_end')),
                    'bidding_time': str(project_data.get('bidding_time')),
                    'location': project_data.get('location'),
                    'match_score': score,
                    'match_details': match_details,
                    'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                print("✅ 数据提取成功")
                
            except Exception as e:
                print(f"❌ 处理失败: {e}")
                logger.exception(e)
        
        # 保存结果到JSON文件
        output_file = os.path.join(output_dir, f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 80)
        print("测试完成！")
        print("=" * 80)
        print(f"\n✅ 成功爬取 {len(results)} 条数据")
        print(f"✅ 结果已保存到: {output_file}")
        
        # 显示统计信息
        if results:
            high_score_count = len([r for r in results if r['match_score'] >= 2.0])
            print(f"\n统计信息:")
            print(f"  - 总数: {len(results)}")
            print(f"  - 高分项目(≥2.0): {high_score_count}")
            print(f"  - 平均分数: {sum(r['match_score'] for r in results) / len(results):.2f}")
            
            print(f"\n高分项目列表:")
            for r in results:
                if r['match_score'] >= 2.0:
                    print(f"  - [{r['match_score']:.2f}] {r['title']}")
        
        print("\n提示:")
        print("  1. 如果验证码识别失败，请检查 PaddleOCR 是否正确安装")
        print("  2. 如果未提取到数据，可能需要调整解析器规则")
        print("  3. 详细日志请查看终端输出")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        logger.exception(e)
    
    finally:
        # 停止爬虫引擎
        print("\n8. 关闭浏览器...")
        crawler_engine.stop()
        print("✅ 测试结束")


if __name__ == "__main__":
    test_crawler()
