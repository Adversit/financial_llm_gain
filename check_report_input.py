"""查看报告生成的输入内容"""
from app.database import SessionLocal
from app.models.article import Article
from app.models.summary import Summary
from datetime import datetime
from pathlib import Path

db = SessionLocal()

# 查询 2025-10-14 的文章和摘要
articles = db.query(Article).join(Summary).filter(
    Article.publish_time >= datetime(2025, 10, 14),
    Article.publish_time < datetime(2025, 10, 15)
).all()

print(f'找到 {len(articles)} 篇文章\n')
print('=' * 80)

# 按类别分组
categories = {'政治': [], '经济': [], '技术': [], '金融科技': []}

for article in articles:
    category = article.source.category if article.source else '未分类'
    summary_obj = article.summaries[0] if article.summaries else None
    
    if category in categories and summary_obj:
        categories[category].append({
            'title': article.title,
            'summary': summary_obj.summary
        })

# 显示各层面的输入
for category, items in categories.items():
    print(f'\n【{category}层面】- {len(items)} 篇文章')
    print('-' * 80)
    
    if items:
        for i, item in enumerate(items, 1):
            print(f'\n{i}. {item["title"][:60]}...')
            print(f'   摘要: {item["summary"][:150]}...')
    else:
        print('（本层面暂无内容）')

# 读取提示词模板
print('\n\n' + '=' * 80)
print('【提示词模板】')
print('=' * 80)

prompt_file = Path('prompts/daily_report.txt')
if prompt_file.exists():
    with open(prompt_file, 'r', encoding='utf-8') as f:
        template = f.read()
    print(template[:500] + '...\n')
else:
    print('提示词文件不存在')

db.close()
