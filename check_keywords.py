"""检查关键词数据"""
from app.database import SessionLocal
from app.models.summary import Summary
from app.models.article import Article
from datetime import datetime

db = SessionLocal()

# 查询 2025-10-14 的摘要
summaries = db.query(Summary).join(Article).filter(
    Article.publish_time >= datetime(2025, 10, 14),
    Article.publish_time < datetime(2025, 10, 15)
).limit(5).all()

print(f'找到 {len(summaries)} 条摘要\n')

for s in summaries:
    print(f'文章ID: {s.article_id}')
    print(f'摘要: {s.summary[:100]}...')
    if s.keywords:
        print(f'关键词: {s.keywords[:300]}')
    else:
        print('关键词: 无')
    print('-' * 80)

db.close()
