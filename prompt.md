# 金融日报系统 - 完整架构文档

## 📋 项目概述

这是一个自动化的金融信息聚合与分析系统，通过多种方式采集金融相关信息源，使用 AI 进行智能总结，生成每日金融报告并自动发送到指定邮箱。

---

## 🏗️ 系统架构

### 技术栈
- **后端框架**: FastAPI
- **数据库**: SQLite
- **AI 模型**: DeepSeek API
- **任务调度**: APScheduler
- **前端**: HTML + CSS + JavaScript
- **PDF 生成**: WeasyPrint
- **邮件服务**: SMTP (网易邮箱)

### 项目结构
```
financial-daily-report/
├── app/
│   ├── api/              # API 路由
│   ├── crawlers/         # 爬虫模块
│   ├── models/           # 数据模型
│   ├── services/         # 业务逻辑
│   └── scheduler/        # 定时任务
├── static/               # 静态资源
├── templates/            # HTML 模板
├── prompts/              # AI 提示词
├── data/                 # 数据存储
└── config.yaml           # 配置文件
```

---

## 🔄 核心模块运行逻辑

### 1. 信息源采集模块 (Crawler Module)

#### 1.1 采集策略优先级

**优先级顺序**:
1. **原生 RSS 订阅源** (最优先)
2. **RSSHub 订阅源** (http://101.42.187.241:1200/)
3. **自定义网络爬虫** (最后选择)

#### 1.2 爬虫架构设计

**基础爬虫类** (`app/crawlers/base.py`):
```python
class BaseCrawler:
    - fetch_articles()      # 抓取文章
    - parse_content()       # 解析内容
    - validate_article()    # 验证有效性
    - save_to_db()         # 保存到数据库
```

**策略模式** (`app/crawlers/strategies/`):
- `rss_strategy.py`: RSS 订阅源策略
- `rsshub_strategy.py`: RSSHub 策略
- `http_strategy.py`: HTTP 爬虫策略

**自定义爬虫** (`app/crawlers/custom/`):
每个信息源一个独立文件，继承 BaseCrawler:
- `miit_crawler.py`: 工信部爬虫
- `xinhua_crawler.py`: 新华社爬虫
- `kr36_crawler.py`: 36氪爬虫
- `csrc_crawler.py`: 证监会爬虫
- 等等...

#### 1.3 数据采集流程

```
开始
  ↓
读取 config.yaml 配置
  ↓
遍历所有启用的信息源
  ↓
判断采集策略 (RSS/RSSHub/自定义)
  ↓
执行对应的爬虫
  ↓
提取必要字段:
  - 标题 (title)
  - 链接 (url)
  - 内容 (content)
  - 发布时间 (published_at)
  ↓
验证内容有效性 (字数检查)
  ↓
保存到数据库 (articles 表)
  - 添加保存时间 (created_at)
  ↓
结束
```


#### 1.4 信息源分类

**政治层面 (国内)**:
- 新闻联播
- 工业和信息化部 (MIIT)
- 人民日报
- 新华社
- 中国证券监督管理委员会 (CSRC)

**经济层面**:
- 艾瑞咨询 (iResearch)
- 头豹研究院 (LeadLeo)
- 36氪 (36Kr)
- 财新网 (Caixin)
- 虎嗅 (Huxiu)

**技术层面**:
- 量子位 (QbitAI)
- arXiv 计算金融 (cs.FI)
- 机器之心
- AI 前线
- 第一财经

**金融科技层面**:
- 未央网 (WeiyangX)

---

### 2. 数据清洗模块 (Cleaner Module)

#### 2.1 清洗逻辑 (`app/services/cleaner_service.py`)

**时间过滤**:
```python
def filter_by_date(articles, target_date):
    # 仅保留指定日期的文章
    # 默认保留昨天的文章
    return filtered_articles
```

**内容过滤**:
```python
def filter_financial_content(articles):
    # 使用关键词或 AI 判断是否与金融相关
    # 去除无关信息
    return relevant_articles
```

**数据验证**:
- 检查必填字段完整性
- 验证 URL 格式
- 检查内容长度 (最小字数要求)
- 去重处理

#### 2.2 清洗流程

```
原始文章数据
  ↓
时间过滤 (保留昨天的文章)
  ↓
内容验证 (字数、格式检查)
  ↓
金融相关性过滤
  ↓
去重处理
  ↓
清洗后的文章数据
```


---

### 3. AI 总结模块 (AI Service Module)

#### 3.1 AI 服务配置 (`app/services/ai_service.py`)

**默认模型**: DeepSeek API
**可扩展**: 支持接入其他 AI 模型

**配置项**:
```python
AI_CONFIG = {
    "provider": "deepseek",  # 可切换为其他模型
    "api_key": "从环境变量读取",
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 2000
}
```

#### 3.2 提示词管理 (`prompts/`)

**单篇文章总结** (`prompts/article_summary.txt`):
- 生成 100-200 字摘要
- 提取关键词 (3-5个)
- 分析文章重要性

**每日报告总结** (`prompts/daily_report.txt`):
- 按层面归纳信息
- 提取核心观点
- 生成趋势分析

**提示词特点**:
- 独立文件存储，便于优化
- 支持变量替换
- 可自定义模板

#### 3.3 AI 处理流程

```
清洗后的文章
  ↓
读取提示词模板 (article_summary.txt)
  ↓
调用 DeepSeek API
  ↓
生成文章摘要 (100-200字)
  ↓
提取关键词
  ↓
保存到 summaries 表:
  - article_id
  - summary (摘要)
  - keywords (关键词)
  - created_at
  ↓
所有文章处理完成
```

#### 3.4 数据库存储

**articles 表**:
- id, title, url, content
- published_at, created_at
- source_id, category

**summaries 表**:
- id, article_id
- summary, keywords
- created_at


---

### 4. 报告生成模块 (Report Service Module)

#### 4.1 报告生成器 (`app/services/report/`)

**模块组成**:
- `generator.py`: 主生成器
- `aggregator.py`: 数据聚合
- `formatter.py`: 格式化输出
- `pdf_generator.py`: PDF 转换

#### 4.2 报告生成流程

```
开始生成报告
  ↓
1. 数据聚合 (aggregator.py)
   - 按层面分组文章
   - 按信息源分类
   - 统计数据
  ↓
2. AI 二次总结
   - 读取 daily_report.txt 提示词
   - 对每个层面的摘要进行总结
   - 生成整体趋势分析
  ↓
3. 格式化输出 (formatter.py)
   - 生成 HTML 格式
   - 生成 Markdown 格式
  ↓
4. PDF 转换 (pdf_generator.py)
   - 使用 WeasyPrint
   - 应用样式模板
   - 生成 PDF 文件
  ↓
5. 保存报告
   - HTML: data/reports/{date}.html
   - PDF: data/reports/{date}.pdf
   - 数据库: daily_reports 表
  ↓
结束
```

#### 4.3 报告结构

**HTML 报告** (`templates/report.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <title>金融日报 - {日期}</title>
    <style>/* 样式 */</style>
</head>
<body>
    <h1>金融日报</h1>
    <div class="date">{日期}</div>
    
    <!-- 政治层面 -->
    <section class="category">
        <h2>政治层面</h2>
        <div class="summary">{AI总结}</div>
        <div class="articles">
            <!-- 文章列表 -->
        </div>
    </section>
    
    <!-- 经济层面 -->
    <!-- 技术层面 -->
    <!-- 金融科技层面 -->
    
    <footer>
        <p>生成时间: {时间}</p>
    </footer>
</body>
</html>
```

**PDF 报告**:
- 基于 HTML 模板
- 优化打印样式
- 支持分页
- 包含目录


---

### 5. 邮件发送模块 (Email Service Module)

#### 5.1 邮件服务配置 (`app/services/email_service.py`)

**SMTP 配置**:
```python
EMAIL_CONFIG = {
    "smtp_server": "smtp.163.com",
    "smtp_port": 465,
    "use_ssl": True,
    "sender_email": "从环境变量读取",
    "sender_password": "从环境变量读取"
}
```

**支持功能**:
- 发送给多个收件人
- HTML 格式邮件
- 附件支持 (PDF 报告)
- 发送状态跟踪

#### 5.2 邮件发送流程

```
触发发送 (手动/定时)
  ↓
读取收件人列表 (settings 表)
  ↓
加载报告内容
  - HTML 正文
  - PDF 附件
  ↓
构建邮件
  - 主题: "金融日报 - {日期}"
  - 正文: HTML 格式
  - 附件: PDF 文件
  ↓
遍历收件人发送
  ↓
记录发送状态
  - 成功/失败
  - 发送时间
  - 错误信息
  ↓
返回发送结果
```

#### 5.3 邮件模板 (`templates/email_template.html`)

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        /* 邮件专用样式 */
        /* 兼容各邮件客户端 */
    </style>
</head>
<body>
    <div class="email-container">
        <h1>📊 金融日报</h1>
        <p class="date">{日期}</p>
        
        <div class="summary">
            <h2>今日要点</h2>
            {核心摘要}
        </div>
        
        <div class="categories">
            <!-- 各层面简要信息 -->
        </div>
        
        <p class="footer">
            详细内容请查看附件 PDF 报告
        </p>
    </div>
</body>
</html>
```


---

### 6. 定时任务模块 (Scheduler Module)

#### 6.1 任务调度器 (`app/scheduler/tasks.py`)

**使用 APScheduler**:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# 每日定时任务
@scheduler.scheduled_job('cron', hour=6, minute=0)
async def daily_report_task():
    # 1. 爬取昨天的文章
    # 2. 清洗数据
    # 3. AI 总结
    # 4. 生成报告
    # 5. 发送邮件
```

#### 6.2 任务配置

**默认时间**: 每天 06:00
**可配置**: 通过前端设置页面修改

**任务类型**:
- 每日报告生成 (定时)
- 手动触发报告生成
- 手动发送邮件
- 数据清理任务

#### 6.3 任务执行流程

```
定时触发 (06:00)
  ↓
1. 爬取文章
   - 遍历所有启用的信息源
   - 采集昨天的文章
  ↓
2. 数据清洗
   - 时间过滤
   - 内容验证
   - 去重
  ↓
3. AI 总结
   - 单篇文章摘要
   - 提取关键词
  ↓
4. 生成报告
   - 数据聚合
   - AI 二次总结
   - 生成 HTML/PDF
  ↓
5. 发送邮件
   - 读取收件人列表
   - 发送报告
  ↓
6. 记录日志
   - 执行状态
   - 错误信息
  ↓
结束
```


---

## 🎨 前端功能模块

### 1. 主页面 (`templates/index.html`)

#### 1.1 页面布局

```
┌─────────────────────────────────────┐
│  金融日报系统                        │
│  [设置] [自定义报告] [添加信息源]    │
├─────────────────────────────────────┤
│                                     │
│  📅 日期选择器: [2025-10-17] ▼     │
│                                     │
│  📊 每日报告列表                    │
│  ┌─────────────────────────────┐   │
│  │ 2025-10-17 金融日报         │   │
│  │ [查看详情] [下载PDF] [发送] │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ 2025-10-16 金融日报         │   │
│  │ [查看详情] [下载PDF] [发送] │   │
│  └─────────────────────────────┘   │
│                                     │
│  📰 文章浏览                        │
│  ├─ 政治层面 ▼                     │
│  │  ├─ 新华社 (5篇)               │
│  │  ├─ 人民日报 (3篇)             │
│  │  └─ 工信部 (2篇)               │
│  ├─ 经济层面 ▼                     │
│  ├─ 技术层面 ▼                     │
│  └─ 金融科技层面 ▼                 │
│                                     │
└─────────────────────────────────────┘
```

#### 1.2 核心功能

**日期选择**:
- 日历控件选择日期
- 显示该日期的所有文章
- 按层面和信息源分组展示

**报告列表**:
- 显示历史报告
- 查看详情按钮
- 下载 PDF 按钮
- 发送邮件按钮

**文章浏览**:
- 树形结构展示
- 点击展开/收起
- 显示文章标题、摘要、关键词
- 点击标题打开原文链接

**操作按钮**:
- 生成今日报告
- 刷新数据
- 导出数据


---

### 2. 报告详情页面 (`templates/report-detail.html`)

#### 2.1 页面功能

**显示内容**:
- 报告标题和日期
- 各层面的 AI 总结
- 文章列表（按层面分组）
- 每篇文章的摘要和关键词

**操作功能**:
- 返回按钮
- 刷新报告按钮（带缓存清理）
- 发送报告按钮
- 下载 PDF 按钮
- 词云图展示

**缓存管理**:
- 使用 `cache-manager.js`
- 智能刷新（清除缓存）
- 加载状态提示
- 操作结果通知

#### 2.2 刷新功能

```javascript
async function refreshReport() {
    // 1. 显示加载状态
    // 2. 清除相关缓存
    CacheManager.clearUrlCache(`/reports/${date}`);
    // 3. 重新加载数据
    await loadReportDetail(date);
    // 4. 显示成功通知
    showNotification('报告已刷新', 'success');
}
```

**刷新按钮特性**:
- 旋转动画效果
- 禁用状态防止重复点击
- 成功/失败通知
- 自动恢复状态

---

### 3. 设置页面 (`templates/settings.html`)

#### 3.1 邮件设置

**收件人管理**:
```
┌─────────────────────────────────┐
│ 📧 邮件设置                     │
├─────────────────────────────────┤
│ 收件人列表:                     │
│ ┌─────────────────────────────┐ │
│ │ user1@example.com  [删除]   │ │
│ │ user2@example.com  [删除]   │ │
│ └─────────────────────────────┘ │
│                                 │
│ 添加收件人:                     │
│ [输入邮箱地址]  [添加]          │
│                                 │
│ [测试发送]  [保存设置]          │
└─────────────────────────────────┘
```

**功能**:
- 添加/删除收件人
- 邮箱格式验证
- 测试发送功能
- 批量导入/导出

#### 3.2 定时任务设置

```
┌─────────────────────────────────┐
│ ⏰ 定时任务设置                 │
├─────────────────────────────────┤
│ 每日报告生成时间:               │
│ [06] : [00]  (默认 06:00)       │
│                                 │
│ 任务状态: ● 已启用              │
│ [启用] [禁用]                   │
│                                 │
│ 下次执行时间:                   │
│ 2025-10-18 06:00:00            │
│                                 │
│ [立即执行] [保存设置]           │
└─────────────────────────────────┘
```

**功能**:
- 设置执行时间（小时:分钟）
- 启用/禁用定时任务
- 显示下次执行时间
- 立即执行按钮
- 执行历史记录

#### 3.3 信息源管理

```
┌─────────────────────────────────┐
│ 📰 信息源管理                   │
├─────────────────────────────────┤
│ 政治层面:                       │
│ ☑ 新华社        [启用/禁用]    │
│ ☑ 人民日报      [启用/禁用]    │
│ ☑ 工信部        [启用/禁用]    │
│                                 │
│ 经济层面:                       │
│ ☑ 36氪          [启用/禁用]    │
│ ☑ 艾瑞咨询      [启用/禁用]    │
│                                 │
│ [全部启用] [全部禁用] [保存]    │
└─────────────────────────────────┘
```

**功能**:
- 按层面分组显示
- 单个启用/禁用开关
- 批量操作
- 显示信息源状态
- 最后更新时间


---

### 4. 自定义报告页面 (`templates/custom-report.html`)

#### 4.1 页面布局

```
┌─────────────────────────────────────┐
│  📝 自定义报告生成                  │
├─────────────────────────────────────┤
│  1️⃣ 选择信息源                     │
│  ┌─────────────────────────────┐   │
│  │ 政治层面:                   │   │
│  │ ☑ 新华社  ☑ 人民日报        │   │
│  │                             │   │
│  │ 经济层面:                   │   │
│  │ ☑ 36氪  ☐ 艾瑞咨询          │   │
│  └─────────────────────────────┘   │
│                                     │
│  2️⃣ 选择日期范围                   │
│  从: [2025-10-15] 到: [2025-10-17] │
│                                     │
│  3️⃣ 自定义提示词 (可选)            │
│  ┌─────────────────────────────┐   │
│  │ 单篇文章总结提示词:         │   │
│  │ [使用默认模板] ☑            │   │
│  │ ┌─────────────────────────┐ │   │
│  │ │ 请总结以下文章...       │ │   │
│  │ │ (可编辑文本框)          │ │   │
│  │ └─────────────────────────┘ │   │
│  │                             │   │
│  │ 每日报告总结提示词:         │   │
│  │ [使用默认模板] ☑            │   │
│  │ ┌─────────────────────────┐ │   │
│  │ │ 请整合以下信息...       │ │   │
│  │ │ (可编辑文本框)          │ │   │
│  │ └─────────────────────────┘ │   │
│  └─────────────────────────────┘   │
│                                     │
│  4️⃣ 报告选项                       │
│  ☑ 包含原文链接                    │
│  ☑ 生成词云图                      │
│  ☑ 包含关键词统计                  │
│                                     │
│  [生成报告] [重置] [保存为模板]    │
└─────────────────────────────────────┘
```

#### 4.2 核心功能

**信息源选择**:
- 多选框选择信息源
- 按层面分组
- 全选/取消全选
- 显示每个源的文章数量

**日期范围**:
- 日期选择器
- 支持单日或多日
- 显示可用日期范围

**提示词自定义**:
- 默认模板选项
- 自定义编辑框
- 模板变量提示
- 实时预览

**报告选项**:
- 包含/排除原文链接
- 生成词云图
- 关键词统计
- 导出格式选择

**操作按钮**:
- 生成报告（异步处理）
- 重置表单
- 保存为模板（供下次使用）
- 下载生成的报告

#### 4.3 生成流程

```
用户配置选项
  ↓
前端验证
  ↓
发送 POST 请求到 /api/custom-reports
  ↓
后端处理:
  1. 根据选择的信息源和日期查询文章
  2. 使用自定义提示词调用 AI
  3. 生成自定义报告
  4. 返回报告 ID
  ↓
前端轮询检查生成状态
  ↓
生成完成后显示结果
  ↓
提供下载/查看选项
```


---

### 5. 添加信息源页面 (`templates/add-source.html`)

#### 5.1 页面布局

```
┌─────────────────────────────────────┐
│  ➕ 添加新信息源                    │
├─────────────────────────────────────┤
│  基本信息:                          │
│  ┌─────────────────────────────┐   │
│  │ 信息源名称: *               │   │
│  │ [输入名称]                  │   │
│  │                             │   │
│  │ 所属层面: *                 │   │
│  │ [政治▼] [经济] [技术] [金融]│   │
│  │                             │   │
│  │ 描述:                       │   │
│  │ [输入描述信息]              │   │
│  └─────────────────────────────┘   │
│                                     │
│  采集配置:                          │
│  ┌─────────────────────────────┐   │
│  │ 采集方式:                   │   │
│  │ ○ RSS 订阅源                │   │
│  │   URL: [输入RSS地址]        │   │
│  │   [测试连接]                │   │
│  │                             │   │
│  │ ○ RSSHub                    │   │
│  │   路径: [输入RSSHub路径]    │   │
│  │   [测试连接]                │   │
│  │                             │   │
│  │ ○ 自定义爬虫                │   │
│  │   ⚠️ 需要手动编写爬虫代码   │   │
│  │   [查看示例代码]            │   │
│  └─────────────────────────────┘   │
│                                     │
│  测试结果:                          │
│  ┌─────────────────────────────┐   │
│  │ 状态: ⏳ 等待测试           │   │
│  │                             │   │
│  │ (测试后显示结果)            │   │
│  │ ✅ 连接成功                 │   │
│  │ 📄 获取到 5 篇文章          │   │
│  │ 示例标题: ...               │   │
│  └─────────────────────────────┘   │
│                                     │
│  [测试全部] [保存] [取消]          │
└─────────────────────────────────────┘
```

#### 5.2 核心功能

**信息源配置**:
- 名称、层面、描述
- 必填项验证
- 重复检查

**采集方式选择**:
1. **RSS 订阅源**:
   - 输入 RSS URL
   - 自动测试连接
   - 解析 RSS 格式
   - 显示示例文章

2. **RSSHub**:
   - 输入 RSSHub 路径
   - 自动拼接完整 URL
   - 测试可用性
   - 显示获取结果

3. **自定义爬虫**:
   - 提示需要编写代码
   - 提供示例代码模板
   - 引导创建爬虫文件
   - 测试爬虫功能

**自动测试流程**:
```
用户输入配置
  ↓
点击"测试连接"
  ↓
前端发送测试请求
  ↓
后端尝试采集:
  - RSS: 解析 feed
  - RSSHub: 请求 RSSHub API
  - 自定义: 运行爬虫代码
  ↓
返回测试结果:
  - 成功: 显示文章数量和示例
  - 失败: 显示错误信息
  ↓
用户决定是否保存
```

**自动集成**:
- 测试成功后自动添加到 config.yaml
- 更新数据库 sources 表
- 立即可用于采集
- 无需重启服务

#### 5.3 示例代码模板

当选择"自定义爬虫"时，显示示例代码：

```python
# app/crawlers/custom/your_source_crawler.py

from app.crawlers.base import BaseCrawler
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

class YourSourceCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(
            source_name="你的信息源名称",
            source_url="https://example.com"
        )
    
    async def fetch_articles(self) -> List[Dict]:
        articles = []
        
        # 1. 发送请求
        response = requests.get(self.source_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. 解析内容
        for item in soup.select('.article-item'):
            article = {
                'title': item.select_one('.title').text,
                'url': item.select_one('a')['href'],
                'content': item.select_one('.content').text,
                'published_at': item.select_one('.date').text
            }
            articles.append(article)
        
        return articles
```


---

### 6. 文章浏览页面 (`templates/articles.html`)

#### 6.1 页面功能

**筛选功能**:
```
┌─────────────────────────────────────┐
│  📰 文章浏览                        │
├─────────────────────────────────────┤
│  筛选条件:                          │
│  日期: [2025-10-17▼]               │
│  层面: [全部▼] [政治] [经济]...    │
│  信息源: [全部▼]                   │
│  关键词: [搜索...]                  │
│  [应用筛选] [重置]                  │
├─────────────────────────────────────┤
│  文章列表 (共 50 篇):              │
│  ┌─────────────────────────────┐   │
│  │ 📄 文章标题                 │   │
│  │ 🏷️ 新华社 | 政治层面        │   │
│  │ 🕐 2025-10-17 08:30        │   │
│  │ 📝 摘要: ...               │   │
│  │ 🔑 关键词: AI, 金融, 监管   │   │
│  │ [查看详情] [查看原文]       │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ 📄 另一篇文章标题           │   │
│  │ ...                         │   │
│  └─────────────────────────────┘   │
│                                     │
│  [上一页] 1 2 3 4 5 [下一页]       │
└─────────────────────────────────────┘
```

**功能特性**:
- 多维度筛选
- 关键词搜索
- 分页显示
- 排序功能（时间、相关性）
- 批量操作（导出、删除）

**文章详情弹窗**:
- 完整内容显示
- AI 摘要
- 关键词标签
- 相关文章推荐
- 分享功能

---

### 7. 词云图功能 (`app/api/wordcloud.py`)

#### 7.1 词云生成

**API 端点**: `/api/wordcloud`

**功能**:
- 提取报告中的关键词
- 统计词频
- 生成词云图片
- 支持自定义样式

**生成流程**:
```
接收报告日期
  ↓
查询该日期的所有关键词
  ↓
统计词频
  ↓
使用 wordcloud 库生成图片
  ↓
保存到 static/images/wordcloud/
  ↓
返回图片 URL
```

**显示位置**:
- 报告详情页面
- 主页面统计区域
- 自定义报告页面

#### 7.2 词云配置

```python
WORDCLOUD_CONFIG = {
    "width": 800,
    "height": 400,
    "background_color": "white",
    "max_words": 100,
    "font_path": "fonts/SimHei.ttf",  # 中文字体
    "colormap": "viridis"
}
```


---

## 🔌 API 接口文档

### 1. 报告相关 API

#### GET `/api/reports`
获取报告列表
```json
Response:
{
  "reports": [
    {
      "id": 1,
      "date": "2025-10-17",
      "title": "金融日报",
      "created_at": "2025-10-17 06:00:00",
      "status": "completed"
    }
  ]
}
```

#### GET `/api/reports/{date}`
获取指定日期的报告详情
```json
Response:
{
  "date": "2025-10-17",
  "categories": {
    "政治层面": {
      "summary": "AI总结内容",
      "articles": [...]
    },
    "经济层面": {...},
    "技术层面": {...},
    "金融科技层面": {...}
  }
}
```

#### POST `/api/reports/generate`
手动生成报告
```json
Request:
{
  "date": "2025-10-17",
  "force": false  // 是否强制重新生成
}

Response:
{
  "status": "success",
  "report_id": 123,
  "message": "报告生成成功"
}
```

#### GET `/api/reports/{date}/pdf`
下载 PDF 报告

#### POST `/api/reports/{date}/send`
发送报告邮件
```json
Request:
{
  "recipients": ["user@example.com"],
  "include_pdf": true
}

Response:
{
  "status": "success",
  "sent_count": 1,
  "failed": []
}
```

---

### 2. 文章相关 API

#### GET `/api/articles`
获取文章列表
```json
Query Parameters:
- date: 日期 (YYYY-MM-DD)
- category: 层面
- source_id: 信息源 ID
- keyword: 关键词
- page: 页码
- per_page: 每页数量

Response:
{
  "articles": [...],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

#### GET `/api/articles/{id}`
获取文章详情

#### POST `/api/articles/crawl`
手动触发爬取
```json
Request:
{
  "source_ids": [1, 2, 3],  // 可选，不传则爬取所有
  "date": "2025-10-17"      // 可选，默认昨天
}
```

---

### 3. 信息源相关 API

#### GET `/api/sources`
获取所有信息源
```json
Response:
{
  "sources": [
    {
      "id": 1,
      "name": "新华社",
      "category": "政治层面",
      "type": "rss",
      "url": "https://...",
      "enabled": true,
      "last_crawl": "2025-10-17 05:00:00"
    }
  ]
}
```

#### POST `/api/sources`
添加新信息源
```json
Request:
{
  "name": "信息源名称",
  "category": "政治层面",
  "type": "rss",  // rss, rsshub, custom
  "url": "https://...",
  "config": {}  // 额外配置
}
```

#### PUT `/api/sources/{id}`
更新信息源

#### DELETE `/api/sources/{id}`
删除信息源

#### POST `/api/sources/{id}/toggle`
启用/禁用信息源

#### POST `/api/sources/test`
测试信息源
```json
Request:
{
  "type": "rss",
  "url": "https://..."
}

Response:
{
  "status": "success",
  "article_count": 5,
  "sample_articles": [...]
}
```

---

### 4. 设置相关 API

#### GET `/api/settings`
获取系统设置
```json
Response:
{
  "email": {
    "recipients": ["user@example.com"],
    "sender": "sender@163.com"
  },
  "scheduler": {
    "enabled": true,
    "time": "06:00"
  },
  "ai": {
    "provider": "deepseek",
    "model": "deepseek-chat"
  }
}
```

#### PUT `/api/settings`
更新系统设置

#### POST `/api/settings/email/test`
测试邮件发送

---

### 5. 自定义报告 API

#### POST `/api/custom-reports`
生成自定义报告
```json
Request:
{
  "source_ids": [1, 2, 3],
  "date_from": "2025-10-15",
  "date_to": "2025-10-17",
  "article_prompt": "自定义提示词",
  "report_prompt": "自定义提示词",
  "options": {
    "include_links": true,
    "generate_wordcloud": true
  }
}

Response:
{
  "task_id": "abc123",
  "status": "processing"
}
```

#### GET `/api/custom-reports/{task_id}`
查询自定义报告生成状态

---

### 6. 词云图 API

#### GET `/api/wordcloud/{date}`
获取指定日期的词云图
```json
Response:
{
  "image_url": "/static/images/wordcloud/2025-10-17.png",
  "keywords": [
    {"word": "AI", "count": 15},
    {"word": "金融", "count": 12}
  ]
}
```

---

### 7. 统计 API

#### GET `/api/stats/overview`
获取系统概览统计
```json
Response:
{
  "total_articles": 1000,
  "total_reports": 30,
  "sources_count": 15,
  "enabled_sources": 12,
  "last_crawl": "2025-10-17 05:00:00"
}
```

#### GET `/api/stats/daily`
获取每日统计数据


---

## 🗄️ 数据库设计

### 数据表结构

#### 1. sources (信息源表)
```sql
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,              -- 信息源名称
    category TEXT NOT NULL,          -- 所属层面
    type TEXT NOT NULL,              -- 类型: rss, rsshub, custom
    url TEXT,                        -- RSS/网站 URL
    config TEXT,                     -- JSON 配置
    enabled BOOLEAN DEFAULT 1,       -- 是否启用
    last_crawl TIMESTAMP,            -- 最后爬取时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. articles (文章表)
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,      -- 信息源 ID
    title TEXT NOT NULL,             -- 标题
    url TEXT NOT NULL UNIQUE,        -- 链接
    content TEXT,                    -- 内容
    published_at TIMESTAMP,          -- 发布时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 保存时间
    FOREIGN KEY (source_id) REFERENCES sources(id)
);
```

#### 3. summaries (摘要表)
```sql
CREATE TABLE summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,     -- 文章 ID
    summary TEXT NOT NULL,           -- AI 摘要 (100-200字)
    keywords TEXT,                   -- 关键词 (JSON 数组)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);
```

#### 4. daily_reports (每日报告表)
```sql
CREATE TABLE daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,       -- 报告日期
    content TEXT,                    -- HTML 内容
    pdf_path TEXT,                   -- PDF 文件路径
    status TEXT DEFAULT 'pending',   -- 状态: pending, completed, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. settings (设置表)
```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,        -- 设置键
    value TEXT,                      -- 设置值 (JSON)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. email_logs (邮件日志表)
```sql
CREATE TABLE email_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER,               -- 报告 ID
    recipient TEXT NOT NULL,         -- 收件人
    status TEXT NOT NULL,            -- 状态: success, failed
    error_message TEXT,              -- 错误信息
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES daily_reports(id)
);
```

#### 7. crawl_logs (爬取日志表)
```sql
CREATE TABLE crawl_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,      -- 信息源 ID
    status TEXT NOT NULL,            -- 状态: success, failed
    article_count INTEGER DEFAULT 0, -- 爬取文章数
    error_message TEXT,              -- 错误信息
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES sources(id)
);
```

---

## 📝 配置文件说明

### config.yaml

```yaml
# 信息源配置
sources:
  # RSS 订阅源
  rss:
    - name: "新华社"
      category: "政治层面"
      url: "http://www.news.cn/rss/..."
      enabled: true
    
    - name: "36氪"
      category: "经济层面"
      url: "https://36kr.com/feed"
      enabled: true
  
  # RSSHub 订阅源
  rsshub:
    - name: "机器之心"
      category: "技术层面"
      path: "/jiqizhixin/posts"
      base_url: "http://101.42.187.241:1200"
      enabled: true
  
  # 自定义爬虫
  custom:
    - name: "工信部"
      category: "政治层面"
      crawler_class: "MIITCrawler"
      enabled: true
    
    - name: "证监会"
      category: "政治层面"
      crawler_class: "CSRCCrawler"
      enabled: true

# AI 配置
ai:
  provider: "deepseek"
  api_key: "${DEEPSEEK_API_KEY}"  # 从环境变量读取
  model: "deepseek-chat"
  temperature: 0.7
  max_tokens: 2000

# 邮件配置
email:
  smtp_server: "smtp.163.com"
  smtp_port: 465
  use_ssl: true
  sender_email: "${EMAIL_SENDER}"
  sender_password: "${EMAIL_PASSWORD}"
  recipients: []  # 从数据库读取

# 定时任务配置
scheduler:
  enabled: true
  daily_report_time: "06:00"  # 每天 06:00 执行
  timezone: "Asia/Shanghai"

# 数据清洗配置
cleaner:
  min_content_length: 100  # 最小内容长度
  date_filter: "yesterday"  # 默认过滤昨天的文章
  financial_keywords:  # 金融相关关键词
    - "金融"
    - "经济"
    - "投资"
    - "市场"
    - "监管"
    # ... 更多关键词

# 报告配置
report:
  formats: ["html", "pdf"]
  output_dir: "data/reports"
  template: "templates/report.html"
  pdf_template: "templates/report_pdf.html"

# 系统配置
system:
  debug: false
  log_level: "INFO"
  database: "data/financial_report.db"
  static_dir: "static"
  templates_dir: "templates"
```

---

## 🔐 环境变量配置

### .env 文件

```bash
# AI API 配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 邮件配置
EMAIL_SENDER=your_email@163.com
EMAIL_PASSWORD=your_email_password_or_app_key

# 数据库配置
DATABASE_URL=sqlite:///data/financial_report.db

# 系统配置
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_here

# RSSHub 配置
RSSHUB_BASE_URL=http://101.42.187.241:1200

# 可选: Firecrawl API (如果使用)
FIRECRAWL_API_KEY=your_firecrawl_api_key
```


---

## 🚀 系统启动流程

### 1. 启动脚本

#### Windows (`start.bat`)
```batch
@echo off
echo 启动金融日报系统...

REM 激活虚拟环境
call venv\Scripts\activate

REM 检查数据库
python db_status.py

REM 启动服务
python start_server.py

pause
```

#### Linux/Mac (`start.sh`)
```bash
#!/bin/bash
echo "启动金融日报系统..."

# 激活虚拟环境
source venv/bin/activate

# 检查数据库
python db_status.py

# 启动服务
python start_server.py
```

### 2. 启动流程

```
执行启动脚本
  ↓
1. 加载环境变量 (.env)
  ↓
2. 初始化数据库
   - 检查数据库文件
   - 创建表结构
   - 加载初始数据
  ↓
3. 加载配置 (config.yaml)
   - 信息源配置
   - AI 配置
   - 邮件配置
  ↓
4. 初始化爬虫工厂
   - 注册所有爬虫类
   - 验证配置
  ↓
5. 启动定时任务调度器
   - 加载定时任务
   - 设置执行时间
  ↓
6. 启动 FastAPI 服务
   - 注册路由
   - 启动 HTTP 服务器
   - 监听端口 (默认 8000)
  ↓
7. 系统就绪
   - 显示访问地址
   - 等待请求
```

### 3. 访问地址

- **主页**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **设置页面**: http://localhost:8000/settings
- **自定义报告**: http://localhost:8000/custom-report

---

## 🔄 完整工作流程

### 每日自动流程

```
06:00 定时任务触发
  ↓
1. 数据采集阶段 (5-10分钟)
   ├─ 遍历所有启用的信息源
   ├─ 并发执行爬虫
   ├─ 采集昨天的文章
   └─ 保存到 articles 表
  ↓
2. 数据清洗阶段 (1-2分钟)
   ├─ 时间过滤
   ├─ 内容验证
   ├─ 去重处理
   └─ 金融相关性过滤
  ↓
3. AI 总结阶段 (10-20分钟)
   ├─ 遍历所有文章
   ├─ 调用 DeepSeek API
   ├─ 生成摘要和关键词
   └─ 保存到 summaries 表
  ↓
4. 报告生成阶段 (2-5分钟)
   ├─ 按层面聚合数据
   ├─ AI 二次总结
   ├─ 生成 HTML 报告
   ├─ 转换为 PDF
   └─ 保存到 daily_reports 表
  ↓
5. 邮件发送阶段 (1-2分钟)
   ├─ 读取收件人列表
   ├─ 构建邮件内容
   ├─ 附加 PDF 文件
   ├─ 发送邮件
   └─ 记录发送日志
  ↓
6. 完成
   └─ 记录执行日志
```

**总耗时**: 约 20-40 分钟

---

## 🎯 前端交互流程

### 1. 查看报告流程

```
用户访问主页
  ↓
前端加载报告列表
  ↓
用户选择日期
  ↓
前端请求 /api/reports/{date}
  ↓
后端返回报告数据
  ↓
前端渲染报告内容
  ↓
用户可以:
  - 查看详情
  - 下载 PDF
  - 发送邮件
  - 查看词云图
```

### 2. 生成自定义报告流程

```
用户访问自定义报告页面
  ↓
选择信息源和日期范围
  ↓
(可选) 自定义提示词
  ↓
点击"生成报告"
  ↓
前端发送 POST /api/custom-reports
  ↓
后端返回 task_id
  ↓
前端轮询 GET /api/custom-reports/{task_id}
  ↓
显示生成进度
  ↓
生成完成后显示结果
  ↓
用户可以下载或查看
```

### 3. 添加信息源流程

```
用户访问添加信息源页面
  ↓
填写基本信息
  ↓
选择采集方式 (RSS/RSSHub/自定义)
  ↓
输入配置信息
  ↓
点击"测试连接"
  ↓
前端发送 POST /api/sources/test
  ↓
后端测试采集
  ↓
返回测试结果:
  - 成功: 显示示例文章
  - 失败: 显示错误信息
  ↓
用户确认后点击"保存"
  ↓
前端发送 POST /api/sources
  ↓
后端保存配置
  ↓
自动集成到系统
  ↓
立即可用
```

### 4. 设置邮件流程

```
用户访问设置页面
  ↓
添加收件人邮箱
  ↓
点击"测试发送"
  ↓
前端发送 POST /api/settings/email/test
  ↓
后端发送测试邮件
  ↓
返回发送结果
  ↓
用户确认后点击"保存"
  ↓
前端发送 PUT /api/settings
  ↓
后端更新配置
  ↓
保存成功
```


---

## 🛠️ 技术实现细节

### 1. 爬虫工厂模式

**目的**: 动态加载和管理不同类型的爬虫

**实现** (`app/crawlers/factory.py`):
```python
class CrawlerFactory:
    _crawlers = {}
    
    @classmethod
    def register(cls, name: str, crawler_class):
        """注册爬虫类"""
        cls._crawlers[name] = crawler_class
    
    @classmethod
    def create(cls, source_config: dict):
        """根据配置创建爬虫实例"""
        source_type = source_config['type']
        
        if source_type == 'rss':
            return RSSCrawler(source_config)
        elif source_type == 'rsshub':
            return RSSHubCrawler(source_config)
        elif source_type == 'custom':
            crawler_class = cls._crawlers.get(
                source_config['crawler_class']
            )
            return crawler_class(source_config)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    @classmethod
    def get_all_crawlers(cls, config):
        """获取所有启用的爬虫"""
        crawlers = []
        for source in config['sources']:
            if source.get('enabled', True):
                crawler = cls.create(source)
                crawlers.append(crawler)
        return crawlers
```

**使用示例**:
```python
# 注册自定义爬虫
CrawlerFactory.register('MIITCrawler', MIITCrawler)
CrawlerFactory.register('CSRCCrawler', CSRCCrawler)

# 创建爬虫实例
crawler = CrawlerFactory.create({
    'type': 'custom',
    'crawler_class': 'MIITCrawler',
    'name': '工信部'
})

# 执行爬取
articles = await crawler.fetch_articles()
```

---

### 2. 缓存管理系统

**目的**: 避免浏览器缓存导致数据不更新

**实现** (`static/js/cache-manager.js`):
```javascript
class CacheManager {
    // 添加时间戳参数
    static addCacheBuster(url) {
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}_t=${Date.now()}`;
    }
    
    // 无缓存请求
    static async fetchNoCache(url, options = {}) {
        const headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            ...options.headers
        };
        
        const urlWithTimestamp = this.addCacheBuster(url);
        return fetch(urlWithTimestamp, { ...options, headers });
    }
    
    // 清除指定 URL 缓存
    static async clearUrlCache(url) {
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            for (const cacheName of cacheNames) {
                const cache = await caches.open(cacheName);
                await cache.delete(url);
            }
        }
    }
    
    // 清除所有缓存
    static async clearAllCache() {
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            await Promise.all(
                cacheNames.map(name => caches.delete(name))
            );
        }
        localStorage.clear();
        sessionStorage.clear();
    }
}
```

**使用场景**:
- 报告详情页面刷新
- 文章列表更新
- 设置保存后刷新

---

### 3. 异步任务处理

**目的**: 处理耗时操作，避免阻塞

**实现方式**:
1. **后台任务队列**
2. **任务状态跟踪**
3. **前端轮询**

**示例** (自定义报告生成):
```python
# 后端
import uuid
from typing import Dict

# 任务状态存储
tasks: Dict[str, dict] = {}

@app.post("/api/custom-reports")
async def create_custom_report(request: CustomReportRequest):
    # 生成任务 ID
    task_id = str(uuid.uuid4())
    
    # 初始化任务状态
    tasks[task_id] = {
        'status': 'processing',
        'progress': 0,
        'result': None
    }
    
    # 异步执行任务
    asyncio.create_task(
        generate_custom_report_task(task_id, request)
    )
    
    return {'task_id': task_id, 'status': 'processing'}

async def generate_custom_report_task(task_id: str, request):
    try:
        # 更新进度
        tasks[task_id]['progress'] = 10
        
        # 执行生成逻辑
        report = await generate_report(request)
        
        tasks[task_id]['progress'] = 100
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['result'] = report
    except Exception as e:
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['error'] = str(e)

@app.get("/api/custom-reports/{task_id}")
async def get_task_status(task_id: str):
    return tasks.get(task_id, {'status': 'not_found'})
```

```javascript
// 前端轮询
async function generateCustomReport(config) {
    // 1. 创建任务
    const response = await fetch('/api/custom-reports', {
        method: 'POST',
        body: JSON.stringify(config)
    });
    const { task_id } = await response.json();
    
    // 2. 轮询状态
    return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
            const statusResponse = await fetch(
                `/api/custom-reports/${task_id}`
            );
            const status = await statusResponse.json();
            
            // 更新进度条
            updateProgress(status.progress);
            
            if (status.status === 'completed') {
                clearInterval(interval);
                resolve(status.result);
            } else if (status.status === 'failed') {
                clearInterval(interval);
                reject(new Error(status.error));
            }
        }, 2000);  // 每 2 秒检查一次
    });
}
```

---

### 4. 错误处理和日志

**统一错误处理**:
```python
from fastapi import HTTPException
from app.utils.logger import logger

class AppException(Exception):
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=exc.code,
        content={'error': exc.message}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={'error': '服务器内部错误'}
    )
```

**日志配置**:
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger('financial_report')
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

---

### 5. 数据库连接管理

**使用 SQLAlchemy**:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# 创建引擎
engine = create_engine(
    'sqlite:///data/financial_report.db',
    echo=False,
    pool_pre_ping=True
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 使用示例
@app.get("/api/articles")
async def get_articles(db: Session = Depends(get_db)):
    articles = db.query(Article).all()
    return articles
```


---

## 📊 性能优化策略

### 1. 爬虫并发优化

**使用异步并发**:
```python
import asyncio
from typing import List

async def crawl_all_sources(sources: List[dict]) -> List[dict]:
    """并发爬取所有信息源"""
    tasks = []
    for source in sources:
        crawler = CrawlerFactory.create(source)
        task = asyncio.create_task(crawler.fetch_articles())
        tasks.append(task)
    
    # 并发执行，设置超时
    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )
    
    # 处理结果
    all_articles = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Source {sources[i]['name']} failed: {result}")
        else:
            all_articles.extend(result)
    
    return all_articles
```

**限制并发数**:
```python
from asyncio import Semaphore

async def crawl_with_limit(sources: List[dict], max_concurrent: int = 5):
    """限制并发数的爬取"""
    semaphore = Semaphore(max_concurrent)
    
    async def crawl_one(source):
        async with semaphore:
            crawler = CrawlerFactory.create(source)
            return await crawler.fetch_articles()
    
    tasks = [crawl_one(source) for source in sources]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

---

### 2. 数据库查询优化

**使用索引**:
```sql
-- 为常用查询字段添加索引
CREATE INDEX idx_articles_date ON articles(published_at);
CREATE INDEX idx_articles_source ON articles(source_id);
CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_summaries_article ON summaries(article_id);
```

**批量插入**:
```python
def batch_insert_articles(articles: List[dict], batch_size: int = 100):
    """批量插入文章"""
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        db.bulk_insert_mappings(Article, batch)
        db.commit()
```

**查询优化**:
```python
# 使用 join 减少查询次数
articles_with_summaries = db.query(Article, Summary)\
    .join(Summary, Article.id == Summary.article_id)\
    .filter(Article.published_at >= yesterday)\
    .all()

# 使用 select_related 预加载关联数据
articles = db.query(Article)\
    .options(joinedload(Article.summary))\
    .filter(Article.published_at >= yesterday)\
    .all()
```

---

### 3. AI API 调用优化

**批量处理**:
```python
async def summarize_articles_batch(
    articles: List[Article],
    batch_size: int = 10
):
    """批量调用 AI API"""
    summaries = []
    
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        
        # 并发调用 API
        tasks = [
            ai_service.summarize(article.content)
            for article in batch
        ]
        batch_summaries = await asyncio.gather(*tasks)
        summaries.extend(batch_summaries)
        
        # 避免 API 限流
        await asyncio.sleep(1)
    
    return summaries
```

**缓存 AI 结果**:
```python
from functools import lru_cache
import hashlib

def get_content_hash(content: str) -> str:
    """计算内容哈希"""
    return hashlib.md5(content.encode()).hexdigest()

async def summarize_with_cache(content: str) -> str:
    """带缓存的摘要生成"""
    content_hash = get_content_hash(content)
    
    # 检查缓存
    cached = db.query(Summary)\
        .filter(Summary.content_hash == content_hash)\
        .first()
    
    if cached:
        return cached.summary
    
    # 调用 AI API
    summary = await ai_service.summarize(content)
    
    # 保存缓存
    db.add(Summary(
        content_hash=content_hash,
        summary=summary
    ))
    db.commit()
    
    return summary
```

---

### 4. 前端性能优化

**懒加载**:
```javascript
// 图片懒加载
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            observer.unobserve(img);
        }
    });
});

document.querySelectorAll('img[data-src]').forEach(img => {
    observer.observe(img);
});
```

**虚拟滚动**:
```javascript
// 大列表虚拟滚动
class VirtualScroll {
    constructor(container, items, itemHeight) {
        this.container = container;
        this.items = items;
        this.itemHeight = itemHeight;
        this.visibleCount = Math.ceil(
            container.clientHeight / itemHeight
        );
        this.render();
    }
    
    render() {
        const scrollTop = this.container.scrollTop;
        const startIndex = Math.floor(scrollTop / this.itemHeight);
        const endIndex = startIndex + this.visibleCount;
        
        const visibleItems = this.items.slice(startIndex, endIndex);
        // 渲染可见项...
    }
}
```

**防抖和节流**:
```javascript
// 防抖
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// 节流
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 使用
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', debounce(handleSearch, 300));

const scrollContainer = document.getElementById('articles');
scrollContainer.addEventListener('scroll', throttle(handleScroll, 100));
```

---

## 🔒 安全性考虑

### 1. API 安全

**API 密钥保护**:
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/api/protected", dependencies=[Depends(verify_api_key)])
async def protected_route():
    return {"message": "Protected data"}
```

**CORS 配置**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # 生产环境限制域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

### 2. 输入验证

**使用 Pydantic**:
```python
from pydantic import BaseModel, EmailStr, validator

class EmailRecipient(BaseModel):
    email: EmailStr
    name: str = None
    
    @validator('name')
    def validate_name(cls, v):
        if v and len(v) > 100:
            raise ValueError('Name too long')
        return v

class CustomReportRequest(BaseModel):
    source_ids: List[int]
    date_from: date
    date_to: date
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if 'date_from' in values and v < values['date_from']:
            raise ValueError('date_to must be after date_from')
        return v
```

---

### 3. SQL 注入防护

**使用 ORM**:
```python
# ✅ 安全 - 使用 ORM
articles = db.query(Article)\
    .filter(Article.title.like(f"%{keyword}%"))\
    .all()

# ❌ 不安全 - 直接拼接 SQL
query = f"SELECT * FROM articles WHERE title LIKE '%{keyword}%'"
```

---

### 4. XSS 防护

**HTML 转义**:
```python
import html

def sanitize_html(content: str) -> str:
    """清理 HTML 内容"""
    return html.escape(content)

# 在模板中使用
@app.get("/api/articles/{id}")
async def get_article(id: int):
    article = db.query(Article).get(id)
    article.content = sanitize_html(article.content)
    return article
```

**前端转义**:
```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 使用
element.innerHTML = escapeHtml(userInput);
```

---

## 🧪 测试策略

### 1. 单元测试

**测试爬虫**:
```python
import pytest
from app.crawlers.custom.miit_crawler import MIITCrawler

@pytest.mark.asyncio
async def test_miit_crawler():
    crawler = MIITCrawler()
    articles = await crawler.fetch_articles()
    
    assert len(articles) > 0
    assert all('title' in article for article in articles)
    assert all('url' in article for article in articles)
    assert all('content' in article for article in articles)
```

**测试 AI 服务**:
```python
@pytest.mark.asyncio
async def test_ai_summarize():
    content = "这是一篇测试文章..." * 100
    summary = await ai_service.summarize(content)
    
    assert len(summary) >= 100
    assert len(summary) <= 200
    assert isinstance(summary, str)
```

---

### 2. 集成测试

**测试完整流程**:
```python
@pytest.mark.asyncio
async def test_daily_report_generation():
    # 1. 爬取文章
    articles = await crawl_all_sources()
    assert len(articles) > 0
    
    # 2. 清洗数据
    cleaned = cleaner_service.clean(articles)
    assert len(cleaned) <= len(articles)
    
    # 3. AI 总结
    summaries = await ai_service.summarize_batch(cleaned)
    assert len(summaries) == len(cleaned)
    
    # 4. 生成报告
    report = await report_service.generate(summaries)
    assert report is not None
    assert 'html' in report
    assert 'pdf' in report
```

---

### 3. API 测试

**使用 TestClient**:
```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_reports():
    response = client.get("/api/reports")
    assert response.status_code == 200
    assert 'reports' in response.json()

def test_create_custom_report():
    data = {
        'source_ids': [1, 2, 3],
        'date_from': '2025-10-15',
        'date_to': '2025-10-17'
    }
    response = client.post("/api/custom-reports", json=data)
    assert response.status_code == 200
    assert 'task_id' in response.json()
```


---

## 📦 部署指南

### 1. 本地开发环境

**安装依赖**:
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**配置环境变量**:
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
# 填入 API 密钥和邮箱配置
```

**初始化数据库**:
```bash
python db_status.py
```

**启动服务**:
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

---

### 2. 生产环境部署

#### 使用 Docker

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "start_server.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    env_file:
      - .env
    restart: unless-stopped
    
  # 可选: 使用 PostgreSQL 替代 SQLite
  # db:
  #   image: postgres:13
  #   environment:
  #     POSTGRES_DB: financial_report
  #     POSTGRES_USER: user
  #     POSTGRES_PASSWORD: password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**部署命令**:
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

#### 使用 Systemd (Linux)

**创建服务文件** (`/etc/systemd/system/financial-report.service`):
```ini
[Unit]
Description=Financial Daily Report System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/financial-report
Environment="PATH=/opt/financial-report/venv/bin"
ExecStart=/opt/financial-report/venv/bin/python start_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**启动服务**:
```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start financial-report

# 设置开机自启
sudo systemctl enable financial-report

# 查看状态
sudo systemctl status financial-report

# 查看日志
sudo journalctl -u financial-report -f
```

---

#### 使用 Nginx 反向代理

**Nginx 配置** (`/etc/nginx/sites-available/financial-report`):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # 静态文件
    location /static {
        alias /opt/financial-report/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # API 请求
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 文件上传大小限制
    client_max_body_size 10M;
}
```

**启用配置**:
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/financial-report \
           /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

---

### 3. 监控和维护

**日志管理**:
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log

# 日志轮转配置 (/etc/logrotate.d/financial-report)
/opt/financial-report/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

**数据库备份**:
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/financial-report"
DB_FILE="/opt/financial-report/data/financial_report.db"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp $DB_FILE $BACKUP_DIR/db_backup_$DATE.db

# 压缩备份
gzip $BACKUP_DIR/db_backup_$DATE.db

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: db_backup_$DATE.db.gz"
```

**定时备份** (crontab):
```bash
# 每天凌晨 3 点备份
0 3 * * * /opt/financial-report/backup.sh
```

**健康检查**:
```python
# app/api/health.py

@app.get("/health")
async def health_check():
    """健康检查端点"""
    checks = {
        'database': check_database(),
        'ai_service': check_ai_service(),
        'email_service': check_email_service(),
        'disk_space': check_disk_space()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            'status': 'healthy' if all_healthy else 'unhealthy',
            'checks': checks,
            'timestamp': datetime.now().isoformat()
        }
    )
```

---

## 🔮 未来扩展功能

### 1. 已实现功能 ✅

- ✅ 多信息源采集 (RSS/RSSHub/自定义爬虫)
- ✅ AI 智能摘要和关键词提取
- ✅ 每日报告自动生成 (HTML/PDF)
- ✅ 邮件自动发送
- ✅ 定时任务调度
- ✅ 前端管理界面
- ✅ 信息源管理 (启用/禁用)
- ✅ 自定义报告生成
- ✅ 词云图展示
- ✅ 缓存管理系统
- ✅ 报告刷新功能

### 2. 计划中功能 🚧

**短期计划** (1-2 个月):
- 🔲 用户认证和权限管理
- 🔲 多用户支持
- 🔲 报告模板自定义
- 🔲 数据导出功能 (Excel/CSV)
- 🔲 移动端适配
- 🔲 微信/钉钉推送
- 🔲 报告评论和标注功能

**中期计划** (3-6 个月):
- 🔲 智能推荐系统
- 🔲 趋势分析和预测
- 🔲 多语言支持
- 🔲 API 开放平台
- 🔲 插件系统
- 🔲 实时数据流处理
- 🔲 知识图谱构建

**长期计划** (6-12 个月):
- 🔲 AI 对话式查询
- 🔲 自动化交易信号
- 🔲 风险预警系统
- 🔲 社区分享平台
- 🔲 企业级功能
- 🔲 大数据分析平台

### 3. 扩展接口预留

**插件系统接口**:
```python
class PluginInterface:
    """插件接口"""
    
    def on_article_crawled(self, article: Article):
        """文章爬取后触发"""
        pass
    
    def on_summary_generated(self, summary: Summary):
        """摘要生成后触发"""
        pass
    
    def on_report_generated(self, report: DailyReport):
        """报告生成后触发"""
        pass
    
    def process_article(self, article: Article) -> Article:
        """处理文章"""
        return article
```

**自定义数据源接口**:
```python
class DataSourceInterface:
    """数据源接口"""
    
    async def fetch_data(self) -> List[dict]:
        """获取数据"""
        raise NotImplementedError
    
    def validate_data(self, data: dict) -> bool:
        """验证数据"""
        raise NotImplementedError
    
    def transform_data(self, data: dict) -> Article:
        """转换数据"""
        raise NotImplementedError
```

---

## 📚 参考资源

### 官方文档
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [APScheduler 文档](https://apscheduler.readthedocs.io/)
- [DeepSeek API 文档](https://platform.deepseek.com/docs)

### 相关技术
- [RSSHub 文档](https://docs.rsshub.app/)
- [BeautifulSoup 文档](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [WeasyPrint 文档](https://doc.courtbouillon.org/weasyprint/)

### 最佳实践
- [Python 异步编程](https://docs.python.org/3/library/asyncio.html)
- [RESTful API 设计](https://restfulapi.net/)
- [Web 安全最佳实践](https://owasp.org/)

---

## 📞 支持和反馈

### 问题反馈
- 提交 Issue
- 发送邮件
- 在线文档

### 贡献指南
- Fork 项目
- 创建分支
- 提交 Pull Request
- 代码审查

---

## 📄 许可证

本项目采用 MIT 许可证。

---

## 🎉 总结

这个金融日报系统是一个完整的自动化信息聚合和分析平台，具有以下特点:

1. **模块化设计**: 各模块职责清晰，易于维护和扩展
2. **灵活的采集策略**: 支持 RSS、RSSHub 和自定义爬虫
3. **智能 AI 总结**: 使用 DeepSeek 进行智能摘要和关键词提取
4. **自动化流程**: 定时任务自动执行完整流程
5. **友好的前端界面**: 提供完整的管理和查看功能
6. **可扩展架构**: 预留多个扩展接口，便于未来功能添加

系统已经实现了所有核心功能，可以稳定运行并生成高质量的金融日报！🚀
