"""重新生成 2025-10-16 的报告"""
from app.services.report_service import ReportGenerator
from app.services.ai_service import AIService
from app.config import load_config
from app.database import SessionLocal
from datetime import date

print("=" * 80)
print("重新生成 2025-10-16 的报告")
print("=" * 80)

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
target_date = date(2025, 10, 16)
print(f'\n正在重新生成 {target_date} 的报告...')
print('这将使用最新的提示词格式，包含国内外信息总结\n')

try:
    report = report_service.generate_daily_report(
        report_date=target_date,
        generate_category_summaries=True,
        generate_pdf=False
    )
    
    print('\n' + '=' * 80)
    print('✅ 报告重新生成成功！')
    print('=' * 80)
    print(f'\n报告ID: {report.id}')
    print(f'报告日期: {report.report_date}')
    print(f'HTML内容长度: {len(report.html_content)} 字符')
    print(f'总体总结长度: {len(report.overall_summary)} 字符')
    
    # 显示总体总结的前500字符
    print(f'\n总体总结预览:')
    print('-' * 80)
    print(report.overall_summary[:500])
    print('...')
    
    print(f'\n✅ HTML 报告已保存到: data/reports/report_{target_date}.html')
    print(f'\n可以访问以下地址查看报告:')
    print(f'  http://localhost:9998/report-detail.html?date={target_date}')
    print('\n' + '=' * 80)
    
except Exception as e:
    print(f'\n❌ 报告生成失败: {e}')
    import traceback
    traceback.print_exc()

db.close()
