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
        summary_obj = article.summaries[0] if article.summaries else None
        summary_text = summary_obj.summary if summary_obj else ''
        
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

# 准备报告数据
report_data = {
    'overall_summary': report.overall_summary,
    'categories': categories
}

# 生成 HTML
config = get_config()
email_config = config.get('email', {})

sender = EmailSender(
    smtp_server=email_config.get('smtp_server'),
    smtp_port=email_config.get('smtp_port'),
    username=email_config.get('username'),
    password=email_config.get('password'),
    use_ssl=email_config.get('use_ssl', True)
)

# 使用内部方法生成 HTML
html_content = sender._render_full_email_template(report_data, report_date_obj)

# 保存到文件
with open('debug_email.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n✅ HTML 已保存到 debug_email.html")
print(f"HTML 长度: {len(html_content)} 字符")

# 检查是否有内容
if '政治' in html_content:
    print("✅ 包含政治层面")
if '经济' in html_content:
    print("✅ 包含经济层面")
if '技术' in html_content:
    print("✅ 包含技术层面")
if '金融科技' in html_content:
    print("✅ 包含金融科技层面")

# 检查文章数量
for cat_name, cat_data in categories.items():
    if cat_data['articles']:
        print(f"✅ {cat_name}: {len(cat_data['articles'])} 篇文章")

db.close()
