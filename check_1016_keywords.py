"""检查 10月16日文章的关键词"""
from app.database import SessionLocal
from app.models.article import Article
from app.models.summary import Summary
from datetime import datetime
import json

db = SessionLocal()

# 查询 10月16日的文章
articles = db.query(Article).join(Summary).filter(
    Article.publish_time >= datetime(2025, 10, 16),
    Article.publish_time < datetime(2025, 10, 17)
).limit(5).all()

print(f'找到 {len(articles)} 篇文章（显示前5篇）\n')

domestic_count = 0
foreign_count = 0

for i, article in enumerate(articles, 1):
    summary = article.summaries[0] if article.summaries else None
    if summary and summary.keywords:
        try:
            keywords = json.loads(summary.keywords)
            print(f'{i}. {article.title[:50]}...')
            print(f'   关键词数量: {len(keywords)}')
            
            has_location = False
            for kw in keywords:
                if isinstance(kw, dict):
                    if kw.get('type') == '国内外信息':
                        has_location = True
                        word = kw.get('word')
                        print(f'   ✓ 国内外信息: {word}')
                        if word == '国内':
                            domestic_count += 1
                        elif word == '国外':
                            foreign_count += 1
            
            if not has_location:
                print(f'   ✗ 没有国内外信息关键词')
                print(f'   关键词示例: {keywords[:2]}')
            
            print()
        except Exception as e:
            print(f'   解析失败: {e}\n')

print(f'统计: 国内 {domestic_count} 篇, 国外 {foreign_count} 篇')

db.close()
