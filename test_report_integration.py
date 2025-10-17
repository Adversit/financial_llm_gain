"""测试报告生成和模板集成"""
from app.services.report_service import ReportGenerator
from app.services.ai_service import AIService
from app.config import load_config
from app.database import SessionLocal
from datetime import date

# 加载配置
config = load_config()
ai_config = config['ai']

# 初始化服务
db = SessionLocal()
ai_service = AIService(
    provider=ai_config['provider'],
    api_key=ai_config['api_key'],
    base_url=ai_config['base_url'],
    model=ai_config['model'],
    prompt_dir='prompts',
    timeout=ai_config.get('timeout', 180)
)

report_service = ReportGenerator(db, ai_service)

# 生成报告
target_date = date(2025, 10, 14)
print(f'正在生成 {target_date} 的报告...\n')

try:
    report = report_service.generate_daily_report(
        report_date=target_date,
        generate_category_summaries=True,
        generate_pdf=False
    )
    
    print('✅ 报告生成成功！')
    print(f'\n报告ID: {report.id}')
    print(f'报告日期: {report.report_date}')
    print(f'HTML内容长度: {len(report.html_content)} 字符')
    print(f'总体总结长度: {len(report.overall_summary)} 字符')
    
    # 保存 HTML 到文件以便查看
    html_file = f'data/reports/test_report_{target_date}.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(report.html_content)
    
    print(f'\n✅ HTML 报告已保存到: {html_file}')
    print('\n可以在浏览器中打开查看效果！')
    
except Exception as e:
    print(f'❌ 报告生成失败: {e}')
    import traceback
    traceback.print_exc()

db.close()
