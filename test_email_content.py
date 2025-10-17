from app.database import SessionLocal
from app.models.daily_report import DailyReport
from datetime import datetime
import re

db = SessionLocal()
report = db.query(DailyReport).filter(
    DailyReport.report_date == datetime.strptime('2025-10-16', '%Y-%m-%d').date()
).first()

if report and report.html_content:
    # 提取 body 内容
    body_match = re.search(r'<body[^>]*>(.*?)</body>', report.html_content, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_content = body_match.group(1)
        print("Body内容前1000字符:")
        print(body_content[:1000])
        print("\n" + "="*50)
        print("是否包含 <p> 标签:", '<p>' in body_content)
        print("是否包含 <h3> 标签:", '<h3>' in body_content)
        print("是否包含 <div> 标签:", '<div>' in body_content)
    else:
        print("未找到 body 标签")
        print("HTML内容前1000字符:")
        print(report.html_content[:1000])
else:
    print("未找到报告")

db.close()
