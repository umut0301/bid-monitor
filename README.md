> ## 招投标监控预警系统

这是一个自动化的招投标信息监控与预警系统，旨在通过程序化手段定时监控、采集、分析和推送相关的招标采购信息，实现从“人找信息”到“信息找人”的智能化转变。

---

### 功能特性

- **自动化爬虫**: 使用 `Playwright` 模拟真人行为，定时爬取“招标采购导航网”的最新招标公告。
- **智能验证码识别**: 集成 `PaddleOCR`，自动识别并处理算术验证码，实现无人值守稳定运行。
- **多维关键词匹配**: 基于自定义关键词（如广告、标识、宣传、文化）和权重，对项目标题和正文进行匹配度评分。
- **实时预警推送**: 当项目匹配分数达到预设阈值时，通过企业微信或钉钉机器人发送实时预警通知。
- **数据持久化与检索**: 使用 `PostgreSQL` 存储所有项目数据，并利用其全文检索功能进行高效查询。
- **可视化数据看板**: 提供 `Streamlit` 构建的Web看板，直观展示已抓取的项目、匹配结果和系统运行日志。

---

### 技术栈

| 分类 | 技术 | 版本/说明 |
| :--- | :--- | :--- |
| **编程语言** | Python | 3.11+ |
| **爬虫引擎** | Playwright | 处理动态加载和验证码 |
| **验证码识别** | PaddleOCR | 识别算术验证码 |
| **HTML解析** | Selectolax | 高性能HTML解析 |
| **后端框架** | FastAPI | (可选) 提供API接口 |
| **数据库** | PostgreSQL | 12+，支持全文检索 |
| **任务调度** | APScheduler | 执行定时爬取任务 |
| **前端看板** | Streamlit | 快速构建数据看板 |
| **消息推送** | requests | 调用企业微信/钉钉Webhook |

---

### 快速开始

#### 1. 环境准备

- Python 3.11+
- PostgreSQL 12+
- Playwright 浏览器驱动

#### 2. 安装依赖

```bash
# 安装Python库
pip install -r requirements.txt

# 安装Playwright浏览器驱动
playwright install chromium
```

#### 3. 配置环境变量

创建 `.env` 文件，并参考 `.env.example` 配置以下变量：

```
# 数据库连接URL
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<dbname>

# 企业微信机器人Webhook URL (可选)
WECOM_WEBHOOK_URL=

# 钉钉机器人Webhook URL (可选)
DINGTALK_WEBHOOK_URL=
```

#### 4. 初始化数据库

在首次运行前，需要初始化数据库，创建所需的表和索引。

```bash
python app/core/database.py
```

#### 5. 运行爬虫调度器

这将启动一个阻塞式的调度器，默认每小时执行一次爬取任务，并立即执行首次任务。

```bash
python crawler/scheduler.py
```

#### 6. 启动数据看板

在另一个终端中，运行Streamlit看板。

```bash
streamlit run dashboard/main_dashboard.py
```

访问 `http://localhost:8501` 即可查看数据看板。

---

### 项目结构

```
.bid-monitor/
├── app/                      # 应用核心模块
│   ├── core/                 # 核心逻辑 (数据库, 匹配, 推送)
│   ├── crud/                 # 数据库增删改查
│   ├── models/               # SQLAlchemy模型
│   └── ...
├── crawler/                  # 爬虫模块
│   ├── parsers/              # 解析器 (包含BaseParser)
│   ├── engine.py             # 爬虫引擎 (Playwright + OCR)
│   ├── captcha_solver.py     # 验证码识别
│   └── scheduler.py          # 任务调度器
├── dashboard/                # Streamlit看板
│   └── main_dashboard.py
├── tests/                    # 测试目录
│   ├── unit/                 # 单元测试
│   └── integration/          # 集成测试
├── .env.example              # 环境变量示例
├── requirements.txt          # Python依赖
└── README.md                 # 项目说明
```

---

*本系统由 Manus AI Agent 构建* Agent 构建。*
