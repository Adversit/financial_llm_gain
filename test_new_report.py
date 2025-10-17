"""测试新的报告生成逻辑"""
from app.database import SessionLocal
from app.models.article import Article
from app.models.summary import Summary
from app.services.ai_service import AIService
from app.config import load_config
from datetime import datetime
import json

# 加载配置
config = load_config()
ai_config = config['ai']

# 初始化 AI 服务
ai_service = AIService(
    provider=ai_config['provider'],
    api_key=ai_config['api_key'],
    base_url=ai_config['base_url'],
    model=ai_config['model'],
    prompt_dir='prompts'
)

db = SessionLocal()

# 查询 2025-10-14 的文章
articles = db.query(Article).join(Summary).filter(
    Article.publish_time >= datetime(2025, 10, 14),
    Article.publish_time < datetime(2025, 10, 15)
).all()

print(f'找到 {len(articles)} 篇文章\n')

# 按类别分组
summaries_by_category = {'政治': [], '经济': [], '技术': [], '金融科技': []}
articles_data = []

for article in articles:
    category = article.source.category if article.source else '未分类'
    summary_obj = article.summaries[0] if article.summaries else None
    
    if summary_obj:
        # 解析关键词
        keywords = []
        if summary_obj.keywords:
            try:
                keywords = json.loads(summary_obj.keywords)
            except:
                pass
        
        # 添加到分类摘要
        if category in summaries_by_category:
            summaries_by_category[category].append(summary_obj.summary)
        
        # 添加到文章数据
        articles_data.append({
            'title': article.title,
            'summary': summary_obj.summary,
            'keywords': keywords
        })

# 统计国内外信息
domestic_count = 0
foreign_count = 0

for article in articles_data:
    for kw in article['keywords']:
        if isinstance(kw, dict) and kw.get('type') == '国内外信息':
            if kw.get('word') == '国内':
                domestic_count += 1
            elif kw.get('word') == '国外':
                foreign_count += 1

print(f'国内信息: {domestic_count} 条')
print(f'国外信息: {foreign_count} 条')
print()

# 生成报告
print('正在生成报告...\n')
report = ai_service.generate_daily_report(
    summaries_by_category,
    articles_data=articles_data
)

print('=' * 80)
print('生成的报告：')
print('=' * 80)
print(report)

db.close()
