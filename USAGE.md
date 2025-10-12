# 金融日报系统 - 使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要配置：

```env
# AI模型配置（必填）
AI_API_KEY=your-deepseek-api-key
AI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat

# 邮件配置（必填）
SMTP_USERNAME=your-email@163.com
SMTP_PASSWORD=your-email-password
```

### 3. 初始化数据库

```bash
# 创建数据库表
python scripts/init_db.py

# 填充初始信息源数据
python scripts/seed_data.py
```

### 4. 启动应用

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5. 访问系统

打开浏览器访问：http://localhost:8000

- API文档：http://localhost:8000/docs
- 主页：http://localhost:8000/
- 信息源管理：http://localhost:8000/sources.html
- 邮件管理：http://localhost:8000/emails.html

## 功能使用

### 信息源管理

1. **查看信息源**
   - 访问"信息源管理"页面
   - 可按层面和状态筛选

2. **添加信息源**
   - 点击"添加信息源"按钮
   - 选择类型（RSS/RSSHub/自定义爬虫）
   - 填写相应信息
   - 点击"测试"验证可用性
   - 点击"添加"保存

3. **启用/停用信息源**
   - 在信息源卡片中点击"启用"或"停用"按钮

4. **删除信息源**
   - 在信息源卡片中点击"删除"按钮

### 邮件订阅管理

1. **添加订阅邮箱**
   - 访问"邮件管理"页面
   - 点击"添加订阅"
   - 输入邮箱地址

2. **测试邮件**
   - 点击"测试邮件"按钮
   - 输入测试邮箱
   - 检查是否收到测试邮件

3. **管理订阅**
   - 启用/停用订阅
   - 删除订阅

### 报告生成

#### 自动生成（推荐）

系统会在每天早上8点自动执行：
1. 爬取昨天的所有文章
2. 使用AI生成摘要
3. 生成HTML和PDF报告
4. 发送邮件给所有订阅者

#### 手动生成

1. 访问首页
2. 选择日期
3. 点击"生成今日报告"
4. 等待生成完成

### 查看报告

1. 在首页查看报告列表
2. 点击"查看报告"查看完整报告
3. 点击"查看文章"查看文章列表

## 配置说明

### config.yaml

主要配置项：

```yaml
# AI配置
ai:
  provider: deepseek  # 可选：deepseek, openai, azure, custom
  api_key: "${AI_API_KEY}"
  base_url: "${AI_BASE_URL}"
  model: "${AI_MODEL}"

# 邮件配置
email:
  smtp_server: "smtp.163.com"
  smtp_port: 465
  username: "${SMTP_USERNAME}"
  password: "${SMTP_PASSWORD}"

# 调度配置
scheduler:
  daily_report_time: "08:00"  # 每日执行时间
  timezone: "Asia/Shanghai"
```

### 提示词自定义

提示词文件位于 `prompts/` 目录：

- `article_summary.txt` - 文章摘要提示词
- `daily_report.txt` - 每日报告提示词

可以直接编辑这些文件来自定义AI生成的内容。

## 添加自定义爬虫

### 1. 创建爬虫文件

在 `app/crawlers/custom/` 目录创建新文件，例如 `example_crawler.py`：

```python
from app.crawlers.base import BaseCrawler, Article
from typing import List
import requests
from bs4 import BeautifulSoup

class ExampleCrawler(BaseCrawler):
    def fetch(self) -> List[Article]:
        articles = []
        
        # 实现你的爬取逻辑
        response = requests.get(self.source_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 解析页面，提取文章
        for item in soup.select('.article'):
            article = Article(
                title=item.select_one('.title').text,
                link=item.select_one('a')['href'],
                content=item.select_one('.content').text,
                publish_time=None,  # 解析发布时间
                source_name=self.source_name
            )
            articles.append(article)
        
        return articles
```

### 2. 在系统中添加

1. 访问"信息源管理"
2. 点击"添加信息源"
3. 选择类型为"自定义爬虫"
4. 填写爬虫类名：`ExampleCrawler`
5. 填写网站URL
6. 点击"测试"验证
7. 点击"添加"保存

## 常见问题

### 1. 邮件发送失败

**问题**：测试邮件发送失败

**解决方案**：
- 检查SMTP配置是否正确
- 确认使用的是授权码而不是登录密码（网易邮箱需要）
- 检查防火墙是否阻止了SMTP端口

### 2. AI摘要生成失败

**问题**：文章摘要为空或生成失败

**解决方案**：
- 检查AI API密钥是否正确
- 确认API额度是否充足
- 检查网络连接

### 3. 爬虫无法获取文章

**问题**：某个信息源无法获取文章

**解决方案**：
- 使用"测试"功能验证信息源
- 检查RSS地址是否有效
- 对于自定义爬虫，检查网站结构是否变化

### 4. 数据库错误

**问题**：数据库相关错误

**解决方案**：
```bash
# 重新初始化数据库
python scripts/init_db.py
```

## 系统维护

### 数据库备份

```bash
# 备份数据库
cp data/financial_daily.db data/financial_daily_backup_$(date +%Y%m%d).db
```

### 日志查看

日志文件位于 `logs/app.log`

```bash
# 查看最新日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

### 清理旧数据

```python
# 可以编写脚本清理30天前的数据
from app.database import SessionLocal
from app.models.article import Article
from datetime import datetime, timedelta

db = SessionLocal()
cutoff_date = datetime.now() - timedelta(days=30)
db.query(Article).filter(Article.created_at < cutoff_date).delete()
db.commit()
```

## 性能优化建议

1. **限制并发爬虫数**：在 `CrawlerService` 中调整 `max_workers` 参数

2. **定期清理数据**：删除旧的文章和报告

3. **使用缓存**：对于频繁访问的报告，可以添加缓存层

4. **数据库索引**：已在关键字段添加索引，无需额外配置

## 技术支持

如有问题，请查看：
- 项目文档：README.md
- API文档：http://localhost:8000/docs
- 日志文件：logs/app.log
