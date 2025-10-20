from app.database import SessionLocal
from app.models.daily_report import DailyReport
from app.models.article import Article
from app.models.source import Source
from app.services.email_service import EmailSender
from app.config import get_config
from datetime import datetime, date as date_type
import json

db = SessionLocal()

# 获取报告
report_date = '2025-10-16'
report = db.query(DailyReport).filter(
    DailyReport.report_date == report_date
).first()

if not report:
    print("报告不存在")
    exit(1)

# 获取该日期的所有文章
report_date_obj = date_type.fromisoformat(report_date)
start_datetime = datetime.combine(report_date_obj, datetime.min.time())
end_datetime = datetime.combine(report_date_obj, datetime.max.time())

articles = db.query(Article).join(Source).filter(
    Article.publish_time >= start_datetime,
    Article.publish_time <= end_datetime
).all()

print(f"找到 {len(articles)} 篇文章")

# 按层面分组文章
categories = {
    '政治': {'articles': [], 'summary': report.political_summary},
    '经济': {'articles': [], 'summary': report.economic_summary},
    '技术': {'articles': [], 'summary': report.technical_summary},
    '金融科技': {'articles': [], 'summary': report.fintech_summary}
}

for article in articles:
    category = article.source.category if article.source else None
    if category in categories:
        # 获取摘要
        summary_obj = article.summaries[0] if article.summaries else None
        summary_text = summary_obj.summary if summary_obj else ''
        
        # 处理关键词
        keywords = []
        if summary_obj and hasattr(summary_obj, 'keywords') and summary_obj.keywords:
            try:
                kw_list = json.loads(summary_obj.keywords)
                keywords = [kw['word'] if isinstance(kw, dict) else str(kw) for kw in kw_list]
            except:
                pass
        
        categories[category]['articles'].append({
            'title': article.title,
            'link': article.link,
            'source': article.source.name if article.source else '未知',
            'publish_time': article.publish_time.strftime('%Y-%m-%d %H:%M') if article.publish_time else '未知',
            'summary': summary_text,
            'keywords': keywords
        })

# 打印统计
for cat_name, cat_data in categories.items():
    print(f"{cat_name}: {len(cat_data['articles'])} 篇")

# 准备报告数据
report_data = {
    'overall_summary': report.overall_summary,
    'categories': categories
}

# 发送邮件
config = get_config()
email_config = config.get('email', {})

sender = EmailSender(
    smtp_server=email_config.get('smtp_server'),
    smtp_port=email_config.get('smtp_port'),
    username=email_config.get('username'),
    password=email_config.get('password'),
    use_ssl=email_config.get('use_ssl', True)
)

print('\n发送完整报告邮件...')
result = sender.send_report(
    recipients=['18348801013@163.com'],
    report_date=report_date_obj,
    report_data=report_data,
    attach_pdf=False
)

print(f'发送结果: {result}')
db.close()
