from app.database import SessionLocal
from app.models.daily_report import DailyReport
from datetime import datetime
import re

db = SessionLocal()
report = db.query(DailyReport).filter(
    DailyReport.report_date == datetime.strptime('2025-10-16', '%Y-%m-%d').date()
).first()

if report:
    # 提取 body 内容
    body_match = re.search(r'<body[^>]*>(.*?)</body>', report.html_content, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_content = body_match.group(1)
        print("Body 内容结构 (前2000字符):")
        print("="*80)
        print(body_content[:2000])
        
        print("\n" + "="*80)
        print("检查关键元素:")
        print("="*80)
        print("是否包含 summary-section:", 'summary-section' in body_content)
        print("是否包含 每日综述:", '每日综述' in body_content)
        print("是否包含 container:", 'container' in body_content)

db.close()
