# 招投标监控预警系统 - 系统设计文档 (SDD)

**版本**: 1.0
**日期**: 2026-01-31
**作者**: Manus AI Agent

---

## 1. 概述

### 1.1 项目愿景与目标

本项目旨在构建一套全自动化的招投标信息监控与预警系统。该系统将替代传统的人工“盯盘”模式，通过程序化手段定时监控、采集、分析和推送相关的招标采购信息，最终实现从“人找信息”到“信息找人”的智能化转变。

- **核心目的**: 提升商机发现效率，降低人工筛选成本。
- **业务目标**: 捕捉与核心业务（广告、标识、宣传、文化等）相关的招标机会，并通过即时通讯工具（企业微信/钉钉）向相关人员发送实时预警。
- **衡量标准**: 预警信息的**准确率**、**覆盖率**和**时效性**。

### 1.2 设计原则

- **规范优先 (Spec-First)**: 任何功能或架构的变更，必须首先更新本文档，确保设计与实现的一致性。
- **高可靠性 (High Reliability)**: 系统需具备强大的容错和恢复能力，包括失败重试、详细日志记录和状态监控。
- **可扩展性 (Scalability)**: 架构设计应支持未来新增数据源、扩展匹配算法和增加预警渠道。
- **测试驱动 (Test-Driven)**: 核心模块（如解析器、数据库操作）必须有对应的单元测试和集成测试，保证代码质量。

## 2. 系统架构

### 2.1 整体架构图

```mermaid
graph TD
    subgraph "数据采集层 (Crawler Service)"
        A[定时任务调度器<br>(APScheduler)] --> B{爬虫引擎<br>(Playwright)};
        B --> C{验证码识别<br>(PaddleOCR)};
        C --> D[目标网站<br>(okcis.cn)];
        D --> E{HTML解析器<br>(Selectolax)};
        E --> F[原始数据<br>(Raw Data)];
    end

    subgraph "数据处理与存储层 (Data Service)"
        F --> G[数据清洗与标准化];
        G --> H{关键词匹配与评分};
        H --> I[PostgreSQL数据库];
        I -- 全文检索 --> H;
    end

    subgraph "应用服务层 (API Service)"
        J[FastAPI 后端] <--> I;
        K[Streamlit 前端看板] <--> J;
    end

    subgraph "预警与通知层 (Alert Service)"
        H -- 触发预警 --> L{预警规则引擎};
        L --> M[消息推送模块];
        M --> N[企业微信/钉钉];
    end

    subgraph "运维与监控 (Ops)"
        O[日志系统<br>(Logging)]
        P[监控面板<br>(Grafana/Streamlit)]
        B --记录--> O;
        H --记录--> O;
        J --记录--> O;
        L --记录--> O;
    end
```

### 2.2 组件说明

| 组件 | 技术选型 | 核心职责 |
| :--- | :--- | :--- |
| **定时任务调度器** | `APScheduler` | 按预设频率（如每小时）触发爬虫任务。 |
| **爬虫引擎** | `Playwright` | 模拟真实浏览器环境，处理动态加载和JavaScript渲染，核心是绕过验证码。 |
| **验证码识别** | `PaddleOCR` | 识别目标网站的算术验证码，实现自动化登录/访问。 |
| **HTML解析器** | `Selectolax` | 从爬取到的HTML页面中高效、精准地提取所需数据字段。 |
| **数据处理模块** | `Python` | 对原始数据进行清洗、格式化（如日期、金额），并执行关键词匹配和评分。 |
| **数据库** | `PostgreSQL` | 持久化存储所有招标信息，并利用其强大的全文检索功能优化查询。 |
| **后端API** | `FastAPI` | 提供RESTful API接口，供前端看板查询数据，并可能用于未来系统集成。 |
| **前端看板** | `Streamlit` | 快速构建一个数据聚合看板，用于展示已抓取的项目、匹配结果和系统状态。 |
| **预警引擎** | `Python` | 根据关键词匹配分数和预设规则，判断是否触发预警。 |
| **消息推送** | `requests` | 调用企业微信/钉钉的Webhook接口，发送格式化的预警消息。 |

## 3. 数据架构

### 3.1 数据库ER图

```mermaid
erDiagram
    BID_PROJECTS {
        varchar(100) project_id PK "唯一标识"
        text source_url "原始链接"
        text title "标题"
        varchar(500) owner_unit "业主单位"
        varchar(50) procurement_type "采购类型"
        numeric(15,2) budget "预算金额"
        timestamp registration_start "报名开始时间"
        timestamp registration_end "报名截止时间"
        timestamp bidding_time "开标时间"
        text location "实施地址"
        text content_raw "原始正文"
        tsvector content_tsvector "全文检索向量"
        float match_score "关键词匹配度评分"
        timestamp created_at "抓取时间"
        timestamp updated_at "更新时间"
    }

    KEYWORDS {
        serial id PK
        varchar(50) keyword UK "关键词"
        float weight "权重"
        varchar(50) category "分类"
        boolean is_active "是否启用"
        timestamp created_at
    }

    CRAWL_LOGS {
        serial id PK
        varchar(50) task_id "任务ID"
        timestamp start_time
        timestamp end_time
        int total_fetched
        int success_count
        int failed_count
        text error_message
        varchar(20) status
    }
```

### 3.2 核心表结构

#### `bid_projects` - 招标项目主表

```sql
-- 存储所有抓取到的招标项目信息
CREATE TABLE bid_projects (
    project_id VARCHAR(100) PRIMARY KEY,      -- 唯一标识（防重），建议使用URL的MD5或特定部分
    source_url TEXT NOT NULL,                 -- 原始链接
    title TEXT NOT NULL,                      -- 标题
    owner_unit VARCHAR(500),                  -- 业主单位
    procurement_type VARCHAR(50),             -- 采购类型（如：公开招标、邀请招标）
    budget NUMERIC(15, 2),                    -- 预算金额（统一单位：万元）
    registration_start TIMESTAMP WITH TIME ZONE, -- 报名开始时间
    registration_end TIMESTAMP WITH TIME ZONE,   -- 报名截止时间
    bidding_time TIMESTAMP WITH TIME ZONE,       -- 开标时间
    location TEXT,                            -- 实施地址
    content_raw TEXT,                         -- 原始正文HTML
    content_text TEXT,                        -- 提取后的纯文本正文
    content_tsvector TSVECTOR,                -- 用于全文检索的向量
    match_score FLOAT DEFAULT 0,              -- 关键词匹配度评分
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- 抓取时间
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()  -- 更新时间
);

-- 创建GIN索引以加速全文检索
CREATE INDEX idx_content_fts ON bid_projects USING GIN(content_tsvector);

-- 创建其他常用查询索引
CREATE INDEX idx_match_score ON bid_projects(match_score DESC);
CREATE INDEX idx_created_at ON bid_projects(created_at DESC);
CREATE INDEX idx_registration_end ON bid_projects(registration_end DESC);
```

#### `keywords` - 关键词配置表

```sql
-- 管理用于匹配的关键词及其权重
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(50) NOT NULL UNIQUE,      -- 关键词
    weight FLOAT DEFAULT 1.0,                 -- 权重，用于计算匹配分
    category VARCHAR(50),                     -- 分类（如：广告类、标识类）
    is_active BOOLEAN DEFAULT TRUE,           -- 是否启用
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 初始化核心关键词
INSERT INTO keywords (keyword, weight, category) VALUES
(
    '广告', 1.5, '广告类'
),(
    '标识', 1.2, '标识类'
),(
    '牌', 1.0, '标识类'
),(
    '标志', 1.2, '标识类'
),(
    '宣传', 1.3, '宣传类'
),(
    '栏', 1.0, '宣传类'
),(
    '文化', 1.1, '文化类'
);
```

#### `crawl_logs` - 爬取日志表

```sql
-- 记录每次爬虫任务的执行情况
CREATE TABLE crawl_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL,             -- 任务唯一ID，建议使用UUID
    start_time TIMESTAMP WITH TIME ZONE NOT NULL, -- 开始时间
    end_time TIMESTAMP WITH TIME ZONE,           -- 结束时间
    total_fetched INT DEFAULT 0,              -- 尝试抓取的总URL数
    success_count INT DEFAULT 0,              -- 成功解析的URL数
    failed_count INT DEFAULT 0,               -- 失败的URL数
    error_details JSONB,                      -- 存储详细错误信息（如URL、失败原因）
    status VARCHAR(20) DEFAULT 'running'      -- 状态：running / success / failed
);
```

## 4. 工程规范

### 4.1 代码结构

```
.bid-monitor/
├── app/                      # FastAPI应用
│   ├── api/                  # API路由
│   ├── core/                 # 核心配置、中间件
│   ├── crud/                 # 数据库增删改查操作
│   ├── models/               # SQLAlchemy模型
│   ├── schemas/              # Pydantic模型
│   └── main.py               # 应用入口
├── crawler/                  # 爬虫模块
│   ├── parsers/              # 解析器实现 (okcis_parser.py)
│   │   └── base_parser.py    # 抽象基类
│   ├── engine.py             # 爬虫引擎 (Playwright + OCR)
│   └── scheduler.py          # 任务调度器
├── dashboard/                # Streamlit看板
│   └── main_dashboard.py
├── tests/                    # 测试目录
│   ├── unit/                 # 单元测试 (e.g., test_parser.py)
│   └── integration/          # 集成测试 (e.g., test_db_write.py)
├── .env                      # 环境变量
├── requirements.txt          # Python依赖
└── README.md
```

### 4.2 可靠性策略

- **失败重试 (Retry Policy)**: 
  - **实现**: 使用 `tenacity` 库对网络请求和验证码识别进行装饰。
  - **策略**: 失败后重试 **3** 次。
  - **间隔**: 采用**指数退避**策略（如 2s, 4s, 8s），增加随机抖动以避免同步请求。

- **详细日志 (Logging)**: 
  - **库**: `loguru`
  - **日志内容**: 
    - **爬虫**: 记录每个URL的抓取状态（成功/失败）、验证码识别结果、失败原因。
    - **数据处理**: 记录数据清洗前后的变化、关键词匹配分数。
    - **预警**: 记录触发预警的项目ID、推送渠道和推送结果。
  - **日志即资产**: 所有日志应结构化（JSON格式），便于后续分析和问题排查。

### 4.3 接口抽象

爬虫解析层必须抽象出 `BaseParser` 接口，所有具体网站的解析器都应继承此接口。这确保了未来在增加新数据源（如其他招标网站）时，只需实现新的解析器即可，无需改动核心引擎代码。

```python
# crawler/parsers/base_parser.py
from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def get_list_urls(self, page_content: str) -> list[str]:
        """从列表页HTML中解析出所有详情页的URL"""
        pass

    @abstractmethod
    def parse_detail_page(self, page_content: str) -> dict:
        """从详情页HTML中解析出结构化数据"""
        pass
```

## 5. 部署方案

- **部署方式**: Docker Compose
- **服务容器**: 
  1. `crawler-service`: 运行爬虫和调度器。
  2. `api-service`: 运行FastAPI后端。
  3. `dashboard-service`: 运行Streamlit前端。
  4. `postgres-db`: PostgreSQL数据库服务。
- **持续集成/持续部署 (CI/CD)**: （可选）使用GitHub Actions在代码合并到主分支后自动构建Docker镜像并部署。

---
**文档结束**
