from app.database import SessionLocal
from app.models.daily_report import DailyReport
from app.services.email_service import EmailSender
from app.config import get_config
from datetime import datetime, date as date_type

db = SessionLocal()

# 获取报告
report_date = '2025-10-16'
report = db.query(DailyReport).filter(
    DailyReport.report_date == report_date
).first()

if not report:
    print("报告不存在")
    exit(1)

if not report.html_content:
    print("报告内容不存在")
    exit(1)

print(f"HTML 内容长度: {len(report.html_content)}")

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

print('\n发送静态 HTML 内容邮件...')
result = sender.send_report(
    recipients=['18348801013@163.com'],
    report_date=date_type.fromisoformat(report_date),
    html_content=report.html_content,
    attach_pdf=False
)

print(f'发送结果: {result}')
db.close()
