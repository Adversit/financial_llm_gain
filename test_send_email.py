from app.database import SessionLocal
from app.models.daily_report import DailyReport
from app.services.email_service import EmailSender
from app.config import get_config
from datetime import datetime

db = SessionLocal()
report = db.query(DailyReport).filter(
    DailyReport.report_date == datetime.strptime('2025-10-16', '%Y-%m-%d').date()
).first()

config = get_config()
email_config = config.get('email', {})

sender = EmailSender(
    smtp_server=email_config.get('smtp_server'),
    smtp_port=email_config.get('smtp_port'),
    username=email_config.get('username'),
    password=email_config.get('password'),
    use_ssl=email_config.get('use_ssl', True)
)

print('发送美化后的邮件...')
print(f'HTML 内容长度: {len(report.html_content)}')

result = sender.send_report(
    recipients=['18348801013@163.com'],
    report_date=report.report_date,
    html_content=report.html_content,
    attach_pdf=False
)

print(f'发送结果: {result}')
db.close()
