"""检查关键词类型分布"""
from app.database import SessionLocal
from app.models.summary import Summary
from app.models.article import Article
from datetime import datetime
import json
from collections import Counter

db = SessionLocal()

# 查询 2025-10-14 的摘要
summaries = db.query(Summary).join(Article).filter(
    Article.publish_time >= datetime(2025, 10, 14),
    Article.publish_time < datetime(2025, 10, 15)
).all()

print(f'找到 {len(summaries)} 条摘要\n')

# 统计关键词类型
type_counter = Counter()
keyword_examples = {}

for s in summaries:
    if s.keywords:
        try:
            keywords = json.loads(s.keywords)
            for kw in keywords:
                kw_type = kw.get('type', '')
                word = kw.get('word', '')
                if kw_type:
                    type_counter[kw_type] += 1
                    if kw_type not in keyword_examples:
                        keyword_examples[kw_type] = []
                    if len(keyword_examples[kw_type]) < 3:
                        keyword_examples[kw_type].append(word)
        except:
            pass

print('关键词类型统计：')
print('-' * 60)
for kw_type, count in type_counter.most_common():
    examples = ', '.join(keyword_examples.get(kw_type, []))
    print(f'{kw_type}: {count} 个')
    print(f'  示例: {examples}')
    print()

db.close()
