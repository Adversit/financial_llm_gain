"""测试重新生成摘要"""
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

# 获取一篇 2025-10-14 的文章
article = db.query(Article).filter(
    Article.publish_time >= datetime(2025, 10, 14),
    Article.publish_time < datetime(2025, 10, 15)
).first()

if article:
    print(f'测试文章: {article.title[:50]}...\n')
    
    # 生成摘要
    result = ai_service.summarize_article(
        title=article.title,
        content=article.content or article.title
    )
    
    print(f'摘要: {result["summary"][:100]}...\n')
    print(f'关键词: {json.dumps(result["keywords"], ensure_ascii=False, indent=2)}\n')
    
    # 更新数据库
    summary = db.query(Summary).filter(Summary.article_id == article.id).first()
    if summary:
        summary.summary = result['summary']
        summary.keywords = json.dumps(result['keywords'], ensure_ascii=False)
        db.commit()
        print('✅ 摘要已更新到数据库')
    else:
        print('❌ 未找到对应的摘要记录')
else:
    print('❌ 未找到文章')

db.close()
