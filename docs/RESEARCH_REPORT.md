# 招投标监控系统技术调研报告

## 1. 目标网站分析

### 1.1 网站基本信息
- **网站名称**: 招标采购导航网
- **主域名**: https://www.okcis.cn/
- **网站性质**: 专业的招投标综合服务平台
- **背景**: 成立于2002年，源自工信部-中小企业发展促进中心

### 1.2 网站结构特征

#### 主要栏目
1. **招标中心**
   - 招标公告（最核心的数据源）
   - 招标预告
   - 免费招标公告
   - 中标结果
   - 文件下载
   - 招标变更

2. **项目中心**
   - 拟在建项目
   - 核实项目
   - 跟踪项目
   - 商业精选项目

3. **企业大数据**
   - 招标业主库
   - 项目业主库
   - 设计院单位库
   - 中标企业库

4. **业主专区**
   - 业主竞价采购
   - 业主询价

#### 数据展示特点
- 首页展示最新招标公告列表，每条包含标题和日期
- 列表项可点击进入详情页
- 支持关键词搜索（高级搜索功能）
- 数据按日期实时更新（观察到2026-01-31的数据）

### 1.3 技术特征分析

#### 前端技术
- **页面渲染**: 服务端渲染（SSR）+ 部分动态加载
- **数据加载**: 初始页面包含列表数据，可能有Ajax分页
- **URL模式**: 
  - 列表页: `/招标中心/招标公告/`
  - 详情页: 点击标题跳转（需进一步分析URL结构）

#### 爬虫策略建议
1. **初步判断**: 网站使用传统服务端渲染，适合使用 httpx + BeautifulSoup/Selectolax
2. **动态内容**: 部分列表可能需要Playwright处理（需验证）
3. **反爬机制**: 需要测试是否有IP限制、User-Agent检测等

### 1.4 关键词匹配目标

根据需求，需要匹配的关键词包括：
- 广告
- 标识
- 牌
- 标志
- 宣传
- 栏
- 文化

**匹配范围**:
- 标题（必须）
- 正文内容（必须）
- 附件文件（可选，技术难度较高）

## 2. 技术栈选型

### 2.1 爬虫引擎
- **首选方案**: httpx + Selectolax（高性能，适合静态内容）
- **备选方案**: Playwright（处理动态加载和复杂交互）
- **理由**: 初步观察网站为服务端渲染，优先使用轻量级方案

### 2.2 数据库设计
- **数据库**: PostgreSQL 15+
- **全文检索**: 使用 PostgreSQL 的 `tsvector` 和 GIN 索引
- **ORM**: SQLAlchemy 2.0+（支持异步）

### 2.3 后端框架
- **API框架**: FastAPI（异步高性能）
- **任务调度**: APScheduler（轻量级，适合中小规模）
- **备选**: Celery + Redis（大规模分布式场景）

### 2.4 前端看板
- **框架**: Streamlit（快速原型开发）
- **可视化**: Plotly（交互式图表）

### 2.5 预警推送
- **企业微信**: 使用企业微信机器人 Webhook API
- **钉钉**: 使用钉钉机器人 Webhook API
- **实现**: 封装统一的消息推送接口

## 3. 数据架构设计

### 3.1 核心表结构（初步设计）

```sql
-- 招标项目主表
CREATE TABLE bid_projects (
    project_id VARCHAR(100) PRIMARY KEY,  -- 唯一标识（防重）
    source_url TEXT NOT NULL,             -- 原始链接
    title TEXT NOT NULL,                  -- 标题
    owner_unit VARCHAR(500),              -- 业主单位
    procurement_type VARCHAR(50),         -- 采购类型
    budget NUMERIC(15, 2),                -- 预算金额
    registration_start TIMESTAMP,         -- 报名开始时间
    registration_end TIMESTAMP,           -- 报名截止时间
    bidding_time TIMESTAMP,               -- 开标时间
    location TEXT,                        -- 实施地址
    content_raw TEXT,                     -- 原始正文
    content_tsvector TSVECTOR,            -- 全文检索向量
    match_score FLOAT DEFAULT 0,          -- 关键词匹配度评分
    created_at TIMESTAMP DEFAULT NOW(),   -- 抓取时间
    updated_at TIMESTAMP DEFAULT NOW()    -- 更新时间
);

-- 创建GIN索引用于全文检索
CREATE INDEX idx_content_fts ON bid_projects USING GIN(content_tsvector);

-- 创建匹配度索引
CREATE INDEX idx_match_score ON bid_projects(match_score DESC);

-- 创建时间索引
CREATE INDEX idx_created_at ON bid_projects(created_at DESC);
```

### 3.2 关键词匹配表

```sql
-- 关键词配置表
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(50) NOT NULL UNIQUE,  -- 关键词
    weight FLOAT DEFAULT 1.0,             -- 权重
    category VARCHAR(50),                 -- 分类（如：广告类、标识类）
    is_active BOOLEAN DEFAULT TRUE,       -- 是否启用
    created_at TIMESTAMP DEFAULT NOW()
);

-- 初始化关键词
INSERT INTO keywords (keyword, weight, category) VALUES
('广告', 1.5, '广告类'),
('标识', 1.2, '标识类'),
('牌', 1.0, '标识类'),
('标志', 1.2, '标识类'),
('宣传', 1.3, '宣传类'),
('栏', 1.0, '宣传类'),
('文化', 1.1, '文化类');
```

### 3.3 爬取日志表

```sql
-- 爬取日志表
CREATE TABLE crawl_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL,         -- 任务ID
    start_time TIMESTAMP NOT NULL,        -- 开始时间
    end_time TIMESTAMP,                   -- 结束时间
    total_fetched INT DEFAULT 0,          -- 抓取总数
    success_count INT DEFAULT 0,          -- 成功数
    failed_count INT DEFAULT 0,           -- 失败数
    error_message TEXT,                   -- 错误信息
    status VARCHAR(20) DEFAULT 'running'  -- 状态：running/success/failed
);
```

## 4. 下一步行动

### 4.1 技术验证
1. ✅ 访问目标网站，确认结构
2. ⏳ 点击进入招标公告列表页，分析列表URL模式
3. ⏳ 点击具体招标详情，分析详情页结构
4. ⏳ 测试爬虫可行性（反爬机制检测）

### 4.2 开发计划
1. 搭建项目基础架构
2. 实现爬虫解析器（BaseParser接口）
3. 实现数据库存储层
4. 实现关键词匹配算法
5. 实现定时任务调度
6. 实现预警推送功能
7. 开发前端看板
8. 编写单元测试和集成测试

### 4.3 需要明确的问题
- [ ] 预警推送的具体渠道（企微还是钉钉？）
- [ ] 爬取频率要求（每小时？每天？）
- [ ] 关键词匹配的最低分数阈值
- [ ] 是否需要处理附件（PDF、Word等）

---
*调研时间: 2026-01-31*
*调研人员: Manus AI Agent*


## 5. 反爬机制发现

### 5.1 验证码拦截
- **触发条件**: 直接访问招标公告列表页 `/bn/` 时触发验证码
- **验证码类型**: 算术验证码（图片显示算术题，需要输入结果）
- **影响**: 需要实现验证码识别或使用其他策略绕过

### 5.2 应对策略

#### 策略一：使用搜索接口（推荐）
- 通过首页搜索功能获取数据，可能不触发验证码
- 测试关键词搜索的URL模式和返回结果

#### 策略二：模拟正常用户行为
- 从首页开始浏览，逐步点击进入列表页
- 设置合理的请求间隔和User-Agent
- 维护Session和Cookie

#### 策略三：使用Playwright + 验证码识别
- 使用Playwright模拟真实浏览器行为
- 集成OCR识别算术验证码（如PaddleOCR）
- 自动填写验证码并提交

#### 策略四：寻找API接口
- 分析网站是否有移动端API或内部接口
- 检查Network请求，寻找JSON数据接口

### 5.3 下一步验证
1. 测试搜索功能是否触发验证码
2. 分析首页列表数据的加载方式
3. 检查是否有移动端或API接口


## 6. 搜索功能测试

### 6.1 测试结果
- **搜索框输入测试**: 在首页搜索框输入关键词"广告"后按回车
- **页面响应**: 页面未跳转到搜索结果页,仍停留在首页
- **可能原因分析**:
  1. 搜索功能需要登录后才能使用
  2. 搜索采用JavaScript动态加载,需要等待更长时间
  3. 搜索表单提交方式特殊(可能是Ajax异步提交)

### 6.2 技术路线调整

基于以上发现,建议采用以下技术路线:

#### 方案A: 直接爬取列表页 + 验证码处理（推荐）
1. **列表页爬取**: 
   - URL: https://www.okcis.cn/bn/ (招标公告列表)
   - 使用Playwright模拟浏览器访问
   - 实现验证码自动识别（OCR）
   - 通过分页参数遍历所有页面

2. **详情页爬取**:
   - 从列表页获取详情页链接
   - 访问详情页获取完整内容(正文、附件、业主信息等)

3. **关键词匹配策略**:
   - 在本地PostgreSQL数据库中进行全文检索
   - 避免依赖网站搜索功能

#### 方案B: 首页数据抓取（备选）
1. **首页列表数据**:
   - 首页展示了多个最新招标公告
   - 可以定时抓取首页数据作为补充
   - 无需验证码,但数据量有限

2. **结合详情页**:
   - 从首页链接进入详情页
   - 获取完整信息

### 6.3 反爬对策

1. **Playwright配置**:
   - 使用真实浏览器指纹
   - 设置合理的请求间隔(建议3-5秒)
   - 添加User-Agent和Referer等请求头

2. **验证码处理**:
   - 集成PaddleOCR或Tesseract识别算术验证码
   - 失败重试机制(最多3次)
   - 记录验证码识别成功率

3. **代理策略**:
   - 初期使用单IP测试
   - 如触发IP封禁,考虑使用代理IP池

### 6.4 下一步行动
1. ✅ 测试搜索功能
2. ⏳ 点击具体招标公告,分析详情页结构
3. ⏳ 检查是否有附件下载功能
4. ⏳ 确认分页机制和URL规律
5. ⏳ 实现验证码识别POC


## 7. 验证码机制详细分析

### 7.1 验证码触发规律
- **触发场景**: 
  1. 直接访问招标公告列表页 `/bn/`
  2. 直接访问具体招标详情页（如 `/20260131-n2-20260131120106106984.html`）
  3. 从首页点击链接进入详情页也会触发验证码

- **验证码特征**:
  - **类型**: 算术验证码（图片显示算术题，如 "10 × 2 + 2 = ?"）
  - **难度**: 简单算术运算（加减乘除）
  - **验证方式**: 输入计算结果后点击"验证"按钮
  - **刷新机制**: 提供"换一张"链接刷新验证码

### 7.2 技术路线确认

基于以上测试，**确定采用以下技术方案**：

#### 核心策略：Playwright + OCR验证码识别

1. **爬虫引擎**: Playwright（必须使用，httpx无法绕过验证码）
2. **验证码处理**: PaddleOCR + 算术表达式解析
3. **数据获取流程**:
   ```
   启动Playwright浏览器
   → 访问目标页面（列表页或详情页）
   → 检测验证码页面
   → OCR识别算术题
   → 计算结果并提交
   → 验证通过后获取页面内容
   → 解析数据并存储
   ```

### 7.3 验证码识别技术方案

#### 方案选择：PaddleOCR（推荐）
- **优势**:
  - 中文OCR识别准确率高
  - 支持数字和运算符识别
  - 开源免费，社区活跃
  - 安装简单：`pip install paddleocr paddlepaddle`

#### 识别流程:
1. **截取验证码图片**: 使用Playwright定位验证码图片元素并截图
2. **OCR文字识别**: 使用PaddleOCR识别图片中的算术表达式
3. **表达式解析**: 使用Python的`eval()`或正则表达式解析算术题
4. **计算结果**: 执行算术运算得到答案
5. **提交验证**: 填写答案并点击验证按钮

#### 代码示例（伪代码）:
```python
from paddleocr import PaddleOCR
from playwright.sync_api import sync_playwright
import re

ocr = PaddleOCR(use_angle_cls=True, lang='ch')

def solve_captcha(page):
    # 1. 截取验证码图片
    captcha_img = page.locator('img.captcha').screenshot()
    
    # 2. OCR识别
    result = ocr.ocr(captcha_img, cls=True)
    text = result[0][0][1][0]  # 提取文字
    
    # 3. 解析算术表达式（如 "10 × 2 + 2 = ?"）
    # 替换中文符号为Python运算符
    expr = text.replace('×', '*').replace('÷', '/').replace('=', '').replace('?', '').strip()
    
    # 4. 计算结果
    answer = eval(expr)
    
    # 5. 提交验证
    page.fill('input[type="text"]', str(answer))
    page.click('input[type="submit"]')
    
    return answer
```

### 7.4 反爬对策完整方案

#### 1. 浏览器指纹伪装
```python
context = browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    viewport={'width': 1920, 'height': 1080},
    locale='zh-CN',
    timezone_id='Asia/Shanghai'
)
```

#### 2. 请求频率控制
- 每次请求间隔：**3-5秒**（随机）
- 验证码识别失败重试：**最多3次**
- 连续失败后暂停：**30分钟**

#### 3. 错误处理与日志
- 记录每次验证码识别结果（成功/失败）
- 记录OCR识别的原始文本
- 统计验证码识别成功率
- 失败时保存验证码图片用于后续优化

#### 4. 代理IP策略（可选）
- 初期使用单IP测试
- 如触发IP封禁，考虑使用代理IP池
- 推荐服务：阿里云代理、快代理等

### 7.5 数据获取策略

#### 策略A：列表页遍历（推荐）
1. 访问招标公告列表页：`https://www.okcis.cn/bn/`
2. 通过验证码后，解析列表页获取所有招标公告链接
3. 分析分页参数（如 `?page=2`），遍历所有页面
4. 逐个访问详情页获取完整内容

#### 策略B：首页增量抓取（辅助）
1. 定时访问首页：`https://www.okcis.cn/`
2. 首页展示最新招标公告，无需验证码
3. 提取首页列表中的链接
4. 访问详情页时处理验证码

#### 策略C：RSS/API探测（待验证）
1. 检查是否有RSS订阅功能
2. 分析移动端是否有API接口
3. 使用开发者工具监控XHR请求

### 7.6 下一步开发计划

#### Phase 1: POC验证（1-2天）
- [x] 完成网站结构分析
- [ ] 实现Playwright + PaddleOCR验证码识别POC
- [ ] 测试验证码识别成功率（目标：>90%）
- [ ] 验证列表页和详情页数据提取

#### Phase 2: 核心功能开发（3-5天）
- [ ] 搭建项目架构（FastAPI + PostgreSQL）
- [ ] 实现BaseParser抽象接口
- [ ] 实现招标采购导航网解析器
- [ ] 实现数据存储层（SQLAlchemy）
- [ ] 实现关键词匹配算法

#### Phase 3: 调度与预警（2-3天）
- [ ] 实现APScheduler定时任务
- [ ] 实现企业微信/钉钉推送接口
- [ ] 实现预警规则引擎

#### Phase 4: 前端与测试（2-3天）
- [ ] 开发Streamlit看板
- [ ] 编写单元测试（pytest）
- [ ] 编写集成测试
- [ ] 性能测试与优化

---
*更新时间: 2026-01-31*
