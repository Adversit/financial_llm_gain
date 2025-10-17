from app.database import SessionLocal
from app.models.daily_report import DailyReport
from datetime import datetime
import html as html_module

db = SessionLocal()
report = db.query(DailyReport).filter(
    DailyReport.report_date == datetime.strptime('2025-10-16', '%Y-%m-%d').date()
).first()

if report:
    print("="*80)
    print("数据库中的 overall_summary (前1500字符):")
    print("="*80)
    print(report.overall_summary[:1500])
    
    print("\n" + "="*80)
    print("解码后的 overall_summary (前1500字符):")
    print("="*80)
    decoded = html_module.unescape(report.overall_summary)
    print(decoded[:1500])
    
    print("\n" + "="*80)
    print("检查:")
    print("="*80)
    print("原始是否包含 &lt;h3&gt;:", '&lt;h3&gt;' in report.overall_summary)
    print("原始是否包含 <h3>:", '<h3>' in report.overall_summary)
    print("解码后是否包含 <h3>:", '<h3>' in decoded)
    print("解码后是否包含 <ul>:", '<ul>' in decoded)
    print("解码后是否包含 <li>:", '<li>' in decoded)

db.close()
