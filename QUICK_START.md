# 快速开始（无需数据库）

如果您想先测试爬虫功能，暂时不配置数据库，可以使用以下测试脚本。

---

## 环境准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 测试脚本

我们提供了两个测试脚本，无需配置数据库即可运行：

---

## 测试1: 验证码识别测试

**脚本**: `test_captcha.py`

**功能**: 测试验证码识别是否正常工作

**运行**:
```bash
python test_captcha.py
```

**预期结果**:
- 浏览器会自动打开（可见模式）
- 访问招标网站列表页
- 自动识别并提交验证码
- 显示"✅ 页面访问成功！"

**如果失败**:
1. 检查 PaddleOCR 是否正确安装: `pip install paddleocr`
2. 查看验证码图片: `/tmp/bid_monitor_captcha/`
3. 检查网络连接

---

## 测试2: 完整爬虫测试

**脚本**: `test_crawler.py`

**功能**: 测试完整的爬虫流程（列表页 → 详情页 → 数据提取 → 关键词匹配）

**运行**:
```bash
python test_crawler.py
```

**功能说明**:
1. 访问招标公告列表页
2. 解析所有详情页URL
3. 爬取前3条详情页（可修改数量）
4. 提取项目信息（标题、业主、预算等）
5. 进行关键词匹配和评分
6. 将结果保存到JSON文件

**输出**:
- 终端显示详细的爬取过程
- 结果保存在 `crawler_test_output/test_results_YYYYMMDD_HHMMSS.json`

**JSON文件内容示例**:
```json
[
  {
    "url": "https://www.okcis.cn/xxx.html",
    "title": "某市文化广场标识标牌制作项目",
    "owner_unit": "某市文化局",
    "budget": 500.0,
    "match_score": 5.2,
    "match_details": {
      "广告": 2,
      "标识": 3,
      "文化": 2
    },
    "crawled_at": "2026-01-31 23:45:00"
  }
]
```

---

## 调整测试参数

### 修改爬取数量

编辑 `test_crawler.py`，找到以下行：

```python
# 只测试前3条
test_count = min(3, len(detail_urls))
```

修改为：

```python
# 测试前10条
test_count = min(10, len(detail_urls))
```

### 修改关键词和权重

编辑 `test_crawler.py`，找到以下部分：

```python
keywords_data = [
    {'keyword': '广告', 'weight': 1.5},
    {'keyword': '标识', 'weight': 1.2},
    # ... 添加或修改关键词
]
```

### 显示浏览器操作

如果想看到浏览器的实际操作过程，将 `headless` 设置为 `False`：

```python
crawler_engine = CrawlerEngine(headless=False)  # 已默认设置为False
```

---

## 常见问题

### Q1: 验证码识别失败

**现象**: 终端显示"验证码识别失败"或"页面访问失败"

**解决方案**:
1. 确认 PaddleOCR 已正确安装:
   ```bash
   pip install paddleocr paddlepaddle
   ```

2. 查看保存的验证码图片:
   ```bash
   ls /tmp/bid_monitor_captcha/
   ```

3. 如果图片模糊或识别不清，可能需要调整OCR参数

### Q2: 未提取到数据

**现象**: 显示"未提取到标题"或"未解析到任何URL"

**解决方案**:
1. 网站结构可能发生变化
2. 需要调整解析器规则（`crawler/parsers/okcis_parser.py`）
3. 检查网页源代码，确认选择器是否正确

### Q3: 浏览器启动失败

**现象**: 报错 "playwright not found"

**解决方案**:
```bash
playwright install chromium
```

---

## 下一步

测试通过后，您可以：

1. **配置数据库**: 参考 [使用指南](docs/USER_GUIDE.md) 配置PostgreSQL
2. **运行完整系统**: 
   ```bash
   python init_database.py  # 初始化数据库
   python run_crawler.py    # 启动定时爬虫
   ```
3. **查看数据看板**:
   ```bash
   streamlit run dashboard/main_dashboard.py
   ```

---

## 技术支持

如果遇到问题，请：
1. 查看详细日志输出
2. 检查 [常见问题](README.md#常见问题)
3. 提交 [GitHub Issue](https://github.com/umut0301/bid-monitor/issues)
