from app.database import SessionLocal
from app.services.report.generator import ReportGenerator
from app.services.ai_service import AIService
from app.config import get_config
from datetime import datetime

# 初始化
db = SessionLocal()
config = get_config()

# 初始化 AI 服务
ai_config = config.get('ai', {})
ai_service = AIService(
    provider=ai_config.get('provider', 'openai'),
    api_key=ai_config.get('api_key'),
    base_url=ai_config.get('base_url'),
    model=ai_config.get('model')
)

# 创建报告生成器
generator = ReportGenerator(db, ai_service)

# 生成报告
report_date = datetime.strptime('2025-10-16', '%Y-%m-%d').date()
print(f"重新生成 {report_date} 的报告...")

report = generator.generate_daily_report(
    report_date,
    generate_category_summaries=False,  # 不重新生成层面总结
    generate_pdf=False  # 不生成 PDF
)

print("\n报告生成完成！")
print("\nHTML内容前800字符:")
print(report.html_content[:800])

print("\n" + "="*50)
print("检查 HTML 标签:")
print("是否包含 <p> (未转义):", '<p>' in report.html_content)
print("是否包含 &lt;p&gt; (已转义):", '&lt;p&gt;' in report.html_content)

db.close()
