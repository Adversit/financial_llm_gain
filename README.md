# 金融科技日报系统 V6

一个自动化的金融科技信息聚合与报告生成系统。

## 📊 系统状态

✅ **运行状态**: 正常  
✅ **成功率**: 68.8% (11/16个信息源)  
✅ **每日文章数**: 510篇  
✅ **数据完整率**: 90.6%

详细状态请查看: [FINAL_STATUS_REPORT.md](FINAL_STATUS_REPORT.md)

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

必须配置：
- `AI_API_KEY` - AI服务API密钥
- `SMTP_*` - 邮件服务器配置

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 启动系统

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

### 5. 访问系统

- 🏠 主页: http://localhost:9998/
- 📚 API文档: http://localhost:9998/docs
- 📰 信息源管理: http://localhost:9998/sources.html
- 📧 邮件管理: http://localhost:9998/emails.html

## 📋 功能特点

- ✅ 自动采集16个信息源的最新资讯
- ✅ AI智能生成每日摘要
- ✅ 自动发送邮件报告
- ✅ Web管理界面
- ✅ 支持HTML和PDF格式报告
- ✅ 智能去重和内容清洗

## 📰 信息源列表

### ✅ 正常运行 (11个)

| 信息源 | 类型 | 每日文章数 |
|--------|------|-----------|
| 人民日报 | RSS | 100篇 |
| 新华社 | RSS | 259篇 |
| 第一财经 | 自定义 | 19篇 |
| 36氪 | RSSHub | 29篇 |
| 虎嗅 | RSSHub | 20篇 |
| 量子位 | 自定义 | 19篇 |
| 财新网 | 自定义 | 20篇 |
| 证监会 | 自定义 | 9篇 |
| 未央网 | 自定义 | 3篇 |
| 工信部-政策解读 | RSSHub | 24篇 |
| 工信部-文件公示 | RSSHub | 8篇 |

### ⚠️ 待优化 (5个)

- 机器之心 - 需要API或Selenium
- 艾瑞咨询 - 网站结构复杂
- 头豹研究院 - 网站结构复杂
- AI前线 - 网站结构复杂
- 工信部-政策文件 - RSSHub暂时不可用

## 🛠️ 常用命令

### 快速测试所有信息源
```bash
python quick_test.py
```

### 验证数据完整性
```bash
python validate_crawlers.py
```

### 初始化/重置数据库
```bash
python scripts/init_db.py
```

## 📁 项目结构

```
.
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   ├── crawlers/          # 爬虫模块
│   │   ├── custom/       # 自定义爬虫
│   │   ├── base.py       # 爬虫基类
│   │   ├── rss_crawler.py
│   │   └── rsshub_crawler.py
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── templates/             # HTML模板
├── static/                # 静态文件
├── scripts/               # 脚本工具
├── config.yaml           # 配置文件
├── quick_test.py         # 快速测试脚本
├── validate_crawlers.py  # 验证脚本
└── requirements.txt      # 依赖列表
```

## 🔧 开发指南

### 添加新的自定义爬虫

1. 在 `app/crawlers/custom/` 创建新文件，例如 `example_crawler.py`
2. 继承 `BaseCrawler` 类并实现 `fetch()` 方法：

```python
from app.crawlers.base import BaseCrawler, Article
from datetime import datetime

class ExampleCrawler(BaseCrawler):
    def fetch(self):
        articles = []
        # 爬取逻辑
        return articles
```

3. 在Web界面或数据库中添加信息源配置

### 测试爬虫

```bash
python -c "from app.crawlers.custom.example_crawler import ExampleCrawler; c = ExampleCrawler('测试源'); print(len(c.fetch()))"
```

## 📖 文档

- [最终状态报告](FINAL_STATUS_REPORT.md) - 系统优化详情
- [部署指南](DEPLOY.md) - 生产环境部署
- [使用说明](USAGE.md) - 详细使用文档
- [项目总结](PROJECT_SUMMARY.md) - 项目概述

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
