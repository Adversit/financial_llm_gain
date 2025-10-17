"""调试报告生成"""
from app.database import SessionLocal
from app.models.daily_report import DailyReport
from datetime import date

db = SessionLocal()

# 查询 10月16日的报告
report = db.query(DailyReport).filter(
    DailyReport.report_date == date(2025, 10, 16)
).first()

if report:
    print("=" * 80)
    print("10月16日报告内容")
    print("=" * 80)
    
    print("\n【总体总结】")
    print("-" * 80)
    print(report.overall_summary[:1000])
    print("...")
    
    print("\n\n【经济层面总结】")
    print("-" * 80)
    print(report.economic_summary[:500] if report.economic_summary else "无")
    
    print("\n\n【金融科技层面总结】")
    print("-" * 80)
    print(report.fintech_summary[:500] if report.fintech_summary else "无")
    
else:
    print("未找到10月16日的报告")

db.close()
