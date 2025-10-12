# 数据库操作常用命令

## 数据库信息

- **类型**: SQLite
- **位置**: `data/financial_daily.db`
- **ORM**: SQLAlchemy

---

## 1. 查看数据库内容

### 使用 Python 脚本查询

```python
from app.database import SessionLocal
from app.models.article import Article
from app.models.summary import Summary
from app.models.daily_report import DailyReport
from app.models.source import Source

db = SessionLocal()

# 查询文章数量
article_count = db.query(Article).count()
print(f"文章数: {article_count}")

# 查询报告数量
report_count = db.query(DailyReport).count()
print(f"报告数: {report_count}")

# 查询信息源
sources = db.query(Source).all()
for source in sources:
    print(f"{source.name} - {source.category}")

db.close()
```

### 使用 SQLite 命令行

```bash
# 打开数据库
sqlite3 data/financial_daily.db

# 查看所有表
.tables

# 查看表结构
.schema articles
.schema daily_reports

# 查询数据
SELECT COUNT(*) FROM articles;
SELECT * FROM daily_reports;

# 退出
.quit
```

---

## 2. 常用查询命令

### 查询文章

```python
from app.database import SessionLocal
from app.models.article import Article
from sqlalchemy.orm import joinedload

db = SessionLocal()

# 查询所有文章
articles = db.query(Article).all()

# 查询特定日期的文章
from datetime import date
target_date = date(2025, 10, 11)
articles = db.query(Article).filter(
    Article.publish_time >= target_date,
    Article.publish_time < target_date + timedelta(days=1)
).all()

# 查询并加载关联数据
articles = db.query(Article).options(
    joinedload(Article.source),
    joinedload(Article.summaries)
).all()

# 按信息源查询
articles = db.query(Article).join(Article.source).filter(
    Source.name == '新华社'
).all()

db.close()
```

### 查询报告

```python
from app.database import SessionLocal
from app.models.daily_report import DailyReport

db = SessionLocal()

# 查询所有报告
reports = db.query(DailyReport).all()

# 查询特定日期的报告
report = db.query(DailyReport).filter(
    DailyReport.report_date == date(2025, 10, 11)
).first()

# 按日期排序
reports = db.query(DailyReport).order_by(
    DailyReport.report_date.desc()
).all()

db.close()
```

---

## 3. 插入数据

### 插入文章

```python
from app.database import SessionLocal
from app.models.article import Article
from datetime import datetime

db = SessionLocal()

article = Article(
    source_id=1,
    title="测试文章",
    link="https://example.com/article",
    content="文章内容",
    publish_time=datetime.now()
)

db.add(article)
db.commit()
db.refresh(article)

print(f"插入成功，ID: {article.id}")

db.close()
```

### 插入报告

```python
from app.database import SessionLocal
from app.models.daily_report import DailyReport
from datetime import date

db = SessionLocal()

report = DailyReport(
    report_date=date(2025, 10, 11),
    political_summary="政治层面总结",
    economic_summary="经济层面总结",
    overall_summary="总体总结",
    html_content="<html>...</html>"
)

db.add(report)
db.commit()

db.close()
```

---

## 4. 更新数据

```python
from app.database import SessionLocal
from app.models.article import Article

db = SessionLocal()

# 查询要更新的记录
article = db.query(Article).filter(Article.id == 1).first()

if article:
    # 更新字段
    article.title = "新标题"
    article.content = "新内容"
    
    # 提交更改
    db.commit()
    print("更新成功")

db.close()
```

---

## 5. 删除数据

### 删除单条记录

```python
from app.database import SessionLocal
from app.models.article import Article

db = SessionLocal()

article = db.query(Article).filter(Article.id == 1).first()

if article:
    db.delete(article)
    db.commit()
    print("删除成功")

db.close()
```

### 批量删除

```python
from app.database import SessionLocal
from app.models.article import Article

db = SessionLocal()

# 删除所有文章
deleted_count = db.query(Article).delete()
db.commit()

print(f"删除了 {deleted_count} 条记录")

db.close()
```

### 清空所有数据

```python
from app.database import SessionLocal
from app.models.article import Article
from app.models.summary import Summary
from app.models.daily_report import DailyReport

db = SessionLocal()

try:
    # 按顺序删除（考虑外键约束）
    db.query(DailyReport).delete()
    db.query(Summary).delete()
    db.query(Article).delete()
    
    db.commit()
    print("所有数据已清空")
except Exception as e:
    db.rollback()
    print(f"删除失败: {e}")
finally:
    db.close()
```

---

## 6. 统计和聚合

```python
from app.database import SessionLocal
from app.models.article import Article
from sqlalchemy import func

db = SessionLocal()

# 统计文章数量
count = db.query(Article).count()

# 按信息源统计
stats = db.query(
    Source.name,
    func.count(Article.id).label('count')
).join(Article.source).group_by(Source.name).all()

for name, count in stats:
    print(f"{name}: {count} 篇")

# 按日期统计
from sqlalchemy import cast, Date
stats = db.query(
    cast(Article.publish_time, Date).label('date'),
    func.count(Article.id).label('count')
).group_by('date').all()

db.close()
```

---

## 7. 实用脚本

### 快速查看数据库状态

创建文件 `db_status.py`:

```python
"""查看数据库状态"""
from app.database import SessionLocal
from app.models.article import Article
from app.models.summary import Summary
from app.models.daily_report import DailyReport
from app.models.source import Source
from app.models.email_subscription import EmailSubscription

db = SessionLocal()

print("=" * 50)
print("数据库状态")
print("=" * 50)

tables = [
    ('信息源', Source),
    ('文章', Article),
    ('摘要', Summary),
    ('报告', DailyReport),
    ('邮件订阅', EmailSubscription),
]

for name, model in tables:
    count = db.query(model).count()
    print(f"{name:12} {count:6} 条")

db.close()
```

运行: `python db_status.py`

### 导出数据到 CSV

```python
"""导出文章到 CSV"""
import csv
from app.database import SessionLocal
from app.models.article import Article
from sqlalchemy.orm import joinedload

db = SessionLocal()

articles = db.query(Article).options(
    joinedload(Article.source)
).all()

with open('articles_export.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    
    # 写入表头
    writer.writerow(['ID', '标题', '链接', '信息源', '发布时间'])
    
    # 写入数据
    for article in articles:
        writer.writerow([
            article.id,
            article.title,
            article.link,
            article.source.name,
            article.publish_time.strftime('%Y-%m-%d %H:%M:%S') if article.publish_time else ''
        ])

print(f"导出完成: {len(articles)} 条记录")

db.close()
```

---

## 8. 数据库备份和恢复

### 备份数据库

```bash
# Windows
copy data\financial_daily.db data\financial_daily_backup.db

# Linux/Mac
cp data/financial_daily.db data/financial_daily_backup.db
```

### 恢复数据库

```bash
# Windows
copy data\financial_daily_backup.db data\financial_daily.db

# Linux/Mac
cp data/financial_daily_backup.db data/financial_daily.db
```

### 使用 Python 备份

```python
import shutil
from datetime import datetime

# 创建带时间戳的备份
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = f'data/financial_daily_backup_{timestamp}.db'

shutil.copy('data/financial_daily.db', backup_path)
print(f"备份完成: {backup_path}")
```

---

## 9. 数据库维护

### 重建数据库

```python
"""重建数据库（删除并重新创建所有表）"""
from app.database import engine, Base
from app.models import *  # 导入所有模型

# 删除所有表
Base.metadata.drop_all(bind=engine)
print("已删除所有表")

# 重新创建所有表
Base.metadata.create_all(bind=engine)
print("已重新创建所有表")
```

### 数据库迁移（使用 Alembic）

如果需要修改表结构，建议使用 Alembic：

```bash
# 安装 Alembic
pip install alembic

# 初始化
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

---

## 10. 常见问题

### Q: 数据库被锁定

```python
# 确保关闭所有数据库连接
db.close()

# 或使用上下文管理器
from app.database import SessionLocal

with SessionLocal() as db:
    # 执行操作
    articles = db.query(Article).all()
    # 自动关闭
```

### Q: 外键约束错误

删除数据时注意顺序：
1. 先删除 DailyReport
2. 再删除 Summary
3. 最后删除 Article
4. Source 最后删除

### Q: 查询性能优化

```python
# 使用 joinedload 预加载关联数据
from sqlalchemy.orm import joinedload

articles = db.query(Article).options(
    joinedload(Article.source),
    joinedload(Article.summaries)
).all()

# 使用索引
# 已在模型中定义索引，无需额外操作
```

---

## 11. 项目提供的工具脚本

```bash
# 查看数据库状态
python diagnose_frontend.py

# 查看报告内容
python show_report_in_db.py

# 清理并重新爬取
python reset_and_recrawl.py

# 生成报告
python generate_report.py

# 分析数据清洗
python analyze_cleaning.py
```

---

## 12. SQLite 浏览器工具

推荐使用图形化工具：

1. **DB Browser for SQLite** (免费)
   - 下载: https://sqlitebrowser.org/
   - 功能: 可视化查看、编辑数据库

2. **DBeaver** (免费)
   - 下载: https://dbeaver.io/
   - 功能: 通用数据库管理工具

3. **VS Code 插件**
   - SQLite Viewer
   - SQLite

---

## 总结

最常用的命令：

```python
# 1. 查看数据
from app.database import SessionLocal
from app.models.article import Article

db = SessionLocal()
articles = db.query(Article).all()
db.close()

# 2. 统计数量
count = db.query(Article).count()

# 3. 删除数据
db.query(Article).delete()
db.commit()

# 4. 备份数据库
import shutil
shutil.copy('data/financial_daily.db', 'backup.db')
```
