# 金融日报系统

一个自动化的金融信息聚合和分析平台，用于从多个信息源收集金融相关资讯，通过AI进行智能总结，并生成每日报告发送给指定用户。

## 功能特性

- 📰 **多源信息获取**：支持RSS、RSSHub、自定义爬虫三种方式
- 🤖 **AI智能摘要**：使用DeepSeek API生成文章摘要和关键词
- 📊 **每日报告生成**：自动生成HTML和PDF格式的综合报告
- 📧 **邮件自动发送**：支持多收件人的邮件订阅
- 🌐 **Web管理界面**：基于FastAPI的现代化管理界面
- ⚙️ **灵活配置**：支持信息源管理和个性化报告定制
- 🔌 **可扩展架构**：插件化的爬虫系统，易于添加新信息源

## 信息源覆盖

### 政治层面
- 新闻联播
- 工业和信息化部 (MIIT)
- 人民日报
- 新华社
- 中国证券监督管理委员会 (CSRC)

### 经济层面
- 艾瑞咨询 (iResearch)
- 头豹研究院 (LeadLeo)
- 36氪 (36Kr)
- 财新网 (Caixin)
- 虎嗅 (Huxiu)

### 技术层面
- 量子位 (QbitAI)
- arXiv 计算金融（cs.FI）
- 机器之心
- AI 前线
- 第一财经

### 金融科技层面
- 未央网 (WeiyangX)

## 技术栈

- **Web框架**: FastAPI + Uvicorn
- **数据库**: SQLite + SQLAlchemy
- **RSS解析**: feedparser
- **网络爬虫**: requests + BeautifulSoup4
- **AI服务**: DeepSeek API
- **报告生成**: Jinja2 + weasyprint
- **邮件发送**: aiosmtplib
- **任务调度**: APScheduler

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的配置：
- DeepSeek API密钥
- 邮箱SMTP配置
- 其他可选配置

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 运行应用

开发模式：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

生产模式：
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5. 访问Web界面

打开浏览器访问：http://localhost:8000

## 项目结构

```
financial-daily-system/
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   ├── crawlers/          # 爬虫模块
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic模式
│   ├── services/          # 业务逻辑
│   ├── scheduler/         # 任务调度
│   └── utils/             # 工具函数
├── templates/             # HTML模板
├── static/                # 静态文件
├── data/                  # 数据目录
├── logs/                  # 日志目录
├── scripts/               # 脚本
├── tests/                 # 测试
├── config.yaml            # 配置文件
├── requirements.txt       # 依赖
└── README.md             # 项目说明
```

## 使用说明

### 添加新信息源

1. 通过Web界面添加：访问"信息源管理"页面
2. 输入信息源名称、RSS地址或RSSHub路径
3. 系统自动测试可用性
4. 如需自定义爬虫，在 `app/crawlers/custom/` 目录创建新爬虫类

### 个性化报告

1. 访问"个性化报告"页面
2. 选择要包含的信息源
3. 可选：自定义AI提示词
4. 生成并预览报告

### 邮件订阅

1. 访问"邮件管理"页面
2. 添加订阅邮箱地址
3. 系统将在每天指定时间自动发送报告

## 配置说明

主要配置文件：`config.yaml`

- **信息源配置**：在 `sources` 部分配置RSS、RSSHub和自定义爬虫
- **AI提示词**：在 `deepseek.prompts` 部分自定义提示词模板
- **调度时间**：在 `scheduler.daily_report_time` 设置报告生成时间
- **邮件配置**：在 `email` 部分配置SMTP服务器

## 开发指南

### 创建自定义爬虫

```python
# app/crawlers/custom/example_crawler.py
from app.crawlers.base import BaseCrawler, Article
from typing import List

class ExampleCrawler(BaseCrawler):
    def fetch(self) -> List[Article]:
        # 实现爬取逻辑
        articles = []
        # ... 爬取代码
        return articles
```

### 运行测试

```bash
pytest tests/
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
