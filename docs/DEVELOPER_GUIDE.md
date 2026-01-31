# 开发指南 (Developer Guide)

本文档面向希望参与本项目开发、扩展或二次开发的开发者。

---

## 开发环境搭建

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/bid-monitor.git
cd bid-monitor
```

### 2. 创建虚拟环境

推荐使用虚拟环境隔离项目依赖：

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装开发依赖

```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8  # 开发工具
playwright install chromium
```

### 4. 配置IDE

推荐使用 **VS Code** 或 **PyCharm**。

**VS Code配置示例** (`.vscode/settings.json`):

```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"]
}
```

---

## 项目架构

### 目录结构

```
bid-monitor/
├── app/                          # 应用核心模块
│   ├── api/                      # FastAPI路由 (未实现)
│   ├── core/                     # 核心逻辑
│   │   ├── database.py           # 数据库连接与初始化
│   │   ├── matcher.py            # 关键词匹配器
│   │   └── notifier.py           # 消息推送器
│   ├── crud/                     # 数据库CRUD操作
│   │   └── bid_project_crud.py   # 招标项目CRUD
│   ├── models/                   # SQLAlchemy模型
│   │   └── bid_project.py        # 数据库模型定义
│   └── schemas/                  # Pydantic模型 (未实现)
├── crawler/                      # 爬虫模块
│   ├── parsers/                  # 网站解析器
│   │   ├── base_parser.py        # 抽象基类
│   │   └── okcis_parser.py       # 招标采购导航网解析器
│   ├── captcha_solver.py         # 验证码识别
│   ├── engine.py                 # 爬虫引擎
│   └── scheduler.py              # 任务调度器
├── dashboard/                    # 前端看板
│   └── main_dashboard.py         # Streamlit看板
├── tests/                        # 测试目录
│   ├── unit/                     # 单元测试
│   │   ├── test_parser.py
│   │   └── test_matcher.py
│   └── integration/              # 集成测试 (待实现)
├── docs/                         # 文档目录
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git忽略文件
├── requirements.txt              # Python依赖
└── README.md                     # 项目说明
```

### 核心模块说明

#### 1. 爬虫引擎 (`crawler/engine.py`)

**职责**: 使用Playwright模拟浏览器，处理验证码，获取页面内容。

**关键方法**:
- `start()`: 启动浏览器
- `fetch_page(url)`: 获取页面内容，自动处理验证码
- `_has_captcha(page)`: 检测是否有验证码
- `_solve_captcha(page)`: 识别并提交验证码

**扩展示例**: 如果需要支持其他类型的验证码（如滑块验证码），可以在 `_solve_captcha` 方法中添加新的识别逻辑。

#### 2. 解析器 (`crawler/parsers/`)

**职责**: 从HTML页面中提取结构化数据。

**抽象基类** (`base_parser.py`):
```python
class BaseParser(ABC):
    @abstractmethod
    def get_list_urls(self, page_content: str) -> List[str]:
        """从列表页解析详情页URL"""
        pass

    @abstractmethod
    def parse_detail_page(self, page_content: str) -> Dict[str, Any]:
        """从详情页解析结构化数据"""
        pass
```

**扩展示例**: 如果需要监控其他招标网站，只需：

1. 在 `crawler/parsers/` 目录下创建新的解析器文件（如 `new_site_parser.py`）
2. 继承 `BaseParser` 并实现两个抽象方法
3. 在 `scheduler.py` 中导入并使用新解析器

```python
# crawler/parsers/new_site_parser.py
from crawler.parsers.base_parser import BaseParser

class NewSiteParser(BaseParser):
    BASE_URL = "https://new-site.com"

    def get_list_urls(self, page_content: str) -> List[str]:
        # 实现列表页URL提取逻辑
        pass

    def parse_detail_page(self, page_content: str) -> Dict[str, Any]:
        # 实现详情页数据提取逻辑
        pass
```

#### 3. 关键词匹配器 (`app/core/matcher.py`)

**职责**: 根据关键词和权重计算项目的匹配分数。

**评分算法**:
```python
score = weight × (1 + 0.5 × (count - 1))
```

**扩展示例**: 如果需要更复杂的评分算法（如TF-IDF），可以修改 `calculate_match_score` 方法。

#### 4. 任务调度器 (`crawler/scheduler.py`)

**职责**: 定时执行爬取任务，协调各模块工作。

**工作流程**:
1. 启动爬虫引擎
2. 获取列表页并解析URL
3. 遍历详情页并提取数据
4. 关键词匹配和评分
5. 保存到数据库
6. 触发预警推送
7. 记录日志

**扩展示例**: 如果需要并发爬取，可以使用 `asyncio` 或 `Celery`。

---

## 开发规范

### 1. 代码风格

本项目遵循 **PEP 8** 规范，并使用 **Black** 进行代码格式化。

**格式化代码**:
```bash
black .
```

**检查代码风格**:
```bash
flake8 .
```

### 2. 命名规范

- **变量和函数**: 使用 `snake_case`（如 `get_list_urls`）
- **类名**: 使用 `PascalCase`（如 `BaseParser`）
- **常量**: 使用 `UPPER_CASE`（如 `BASE_URL`）

### 3. 注释规范

所有公共函数和类都应包含文档字符串（Docstring）：

```python
def calculate_match_score(self, text: str) -> Tuple[float, Dict[str, int]]:
    """
    计算文本的关键词匹配分数

    :param text: 待匹配的文本（标题+正文）
    :return: (总分数, 各关键词出现次数字典)
    """
    pass
```

### 4. 日志规范

使用 `loguru` 记录日志，日志级别：

- `DEBUG`: 调试信息（如OCR识别的原始文本）
- `INFO`: 正常流程信息（如爬取成功）
- `WARNING`: 警告信息（如验证码识别失败）
- `ERROR`: 错误信息（如数据库连接失败）

**示例**:
```python
from loguru import logger

logger.info(f"页面获取成功: {url}")
logger.error(f"验证码识别失败: {e}")
```

---

## 测试

### 1. 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行特定测试文件
pytest tests/unit/test_parser.py

# 查看测试覆盖率
pytest --cov=app --cov=crawler tests/
```

### 2. 编写测试

**单元测试示例** (`tests/unit/test_matcher.py`):

```python
import pytest
from app.core.matcher import KeywordMatcher

class TestKeywordMatcher:
    def setup_method(self):
        self.keywords = [
            {'keyword': '广告', 'weight': 1.5},
            {'keyword': '标识', 'weight': 1.2},
        ]
        self.matcher = KeywordMatcher(self.keywords)

    def test_calculate_match_score(self):
        text = "某市广告牌制作项目"
        score, details = self.matcher.calculate_match_score(text)
        
        assert score > 0
        assert '广告' in details
```

### 3. 测试覆盖率目标

- **核心模块**: 100%
- **整体项目**: ≥ 80%

---

## 常见开发任务

### 任务1: 添加新的关键词

**方法1: 直接在数据库中添加**

```sql
INSERT INTO keywords (id, keyword, weight, category, is_active)
VALUES ('kw_展览', '展览', 1.2, '文化类', 'true');
```

**方法2: 修改初始化脚本**

在 `app/core/database.py` 的 `_init_keywords()` 函数中添加：

```python
keywords_data = [
    # 现有关键词...
    {'keyword': '展览', 'weight': 1.2, 'category': '文化类'},
]
```

### 任务2: 修改爬取频率

在 `crawler/scheduler.py` 中修改Cron表达式：

```python
# 每30分钟执行一次
self.scheduler.add_job(
    self.crawl_and_alert,
    trigger=CronTrigger(minute='*/30'),
    ...
)

# 每天早上9点执行一次
self.scheduler.add_job(
    self.crawl_and_alert,
    trigger=CronTrigger(hour='9', minute='0'),
    ...
)
```

### 任务3: 添加新的数据源

1. 创建新的解析器（继承 `BaseParser`）
2. 在 `scheduler.py` 中添加新的爬取任务

```python
# 在 crawl_and_alert 方法中
new_parser = NewSiteParser()
new_list_url = "https://new-site.com/list"
new_list_content = self.crawler_engine.fetch_page(new_list_url)
new_detail_urls = new_parser.get_list_urls(new_list_content)
# ... 处理详情页
```

### 任务4: 优化验证码识别

如果验证码识别准确率不高，可以：

1. 收集失败的验证码图片（保存在 `/tmp/bid_monitor_captcha/`）
2. 分析失败原因（OCR识别错误 / 表达式解析错误）
3. 在 `captcha_solver.py` 中优化 `_parse_expression` 方法

```python
def _parse_expression(self, text: str) -> Optional[int]:
    # 添加更多的文字替换规则
    text = text.replace("〇", "0")  # 处理中文数字
    text = text.replace("一", "1")
    # ...
```

---

## 性能优化

### 1. 数据库优化

- 确保已创建必要的索引（GIN索引、匹配分数索引等）
- 定期清理旧数据（如删除6个月前的项目）

```sql
DELETE FROM bid_projects WHERE created_at < NOW() - INTERVAL '6 months';
```

### 2. 爬虫优化

- 使用连接池复用浏览器实例
- 实现增量爬取（只爬取新发布的项目）
- 使用代理IP池避免IP封禁

### 3. 并发爬取

如果需要提高爬取速度，可以使用 `asyncio` 或 `Celery`：

```python
# 使用asyncio并发爬取
import asyncio
from playwright.async_api import async_playwright

async def fetch_multiple_pages(urls):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        tasks = [fetch_page(browser, url) for url in urls]
        results = await asyncio.gather(*tasks)
        await browser.close()
    return results
```

---

## 贡献指南

欢迎贡献代码！请遵循以下流程：

1. **Fork** 本仓库
2. 创建新分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建 **Pull Request**

**注意事项**:
- 确保所有测试通过
- 添加必要的文档和注释
- 遵循项目的代码风格

---

## 调试技巧

### 1. 调试爬虫

在 `crawler/engine.py` 中将 `headless` 设置为 `False`，可以看到浏览器的实际操作：

```python
engine = CrawlerEngine(headless=False)
```

### 2. 调试验证码识别

查看保存的验证码图片：

```bash
ls /tmp/bid_monitor_captcha/
```

手动测试验证码识别：

```python
from crawler.captcha_solver import CaptchaSolver

solver = CaptchaSolver()
result = solver.solve("/tmp/bid_monitor_captcha/captcha_xxx.png")
print(f"识别结果: {result}")
```

### 3. 调试数据库

使用 `psql` 命令行工具：

```bash
psql -U bid_user -d bid_monitor

# 查看所有项目
SELECT title, match_score FROM bid_projects ORDER BY created_at DESC LIMIT 10;

# 查看关键词配置
SELECT * FROM keywords;
```

---

## 常见问题

### Q: 如何禁用某个模块的日志？

**A**: 在相应模块中设置日志级别：

```python
from loguru import logger

logger.remove()  # 移除默认handler
logger.add(sys.stderr, level="WARNING")  # 只显示WARNING及以上
```

### Q: 如何在生产环境中运行？

**A**: 推荐使用 `systemd` 或 `supervisor` 管理进程：

**systemd示例** (`/etc/systemd/system/bid-monitor.service`):

```ini
[Unit]
Description=Bid Monitor Service
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bid-monitor
ExecStart=/usr/bin/python3 /home/ubuntu/bid-monitor/crawler/scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable bid-monitor
sudo systemctl start bid-monitor
sudo systemctl status bid-monitor
```

---

**祝开发愉快！**
