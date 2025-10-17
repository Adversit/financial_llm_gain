"""爬取数据并生成 2025-10-17 的报告"""
from app.services.crawler_service import CrawlerService
from app.services.report_service import ReportGenerator
from app.services.ai_service import AIService
from app.config import load_config
from app.database import SessionLocal
from datetime import date

print("=" * 80)
print("步骤 1: 爬取 2025-10-17 的数据")
print("=" * 80)

# 加载配置
config = load_config()
ai_config = config['ai']

# 初始化服务
db = SessionLocal()

# 步骤 1: 爬取数据
print("\n开始爬取数据...\n")
crawler_service = CrawlerService(db)

try:
    # 爬取所有信息源
    articles = crawler_service.crawl_all_sources()
    print(f"\n✅ 爬取完成，共获取 {len(articles)} 篇文章")
    
    # 数据清洗
    target_date = date(2025, 10, 17)
    print(f"\n开始数据清洗，目标日期: {target_date}")
    
    cleaned_articles = crawler_service.clean_articles(articles, target_date)
    print(f"✅ 清洗完成，保留 {len(cleaned_articles)} 篇文章")
    
    # 保存到数据库
    print("\n保存文章到数据库...")
    saved_count = crawler_service.save_articles(cleaned_articles)
    print(f"✅ 成功保存 {saved_count} 篇文章")
    
    # 生成摘要
    print("\n生成文章摘要...")
    ai_service = AIService(
        provider=ai_config['provider'],
        api_key=ai_config['api_key'],
        base_url=ai_config['base_url'],
        model=ai_config['model'],
        prompt_dir='prompts',
        timeout=ai_config.get('timeout', 180)
    )
    
    crawler_service.ai_service = ai_service
    crawler_service.generate_summaries(cleaned_articles)
    print("✅ 摘要生成完成")
    
    # 步骤 2: 生成报告
    print("\n" + "=" * 80)
    print("步骤 2: 生成报告")
    print("=" * 80)
    
    report_service = ReportGenerator(db, ai_service)
    
    print(f'\n正在生成 {target_date} 的报告...\n')
    
    report = report_service.generate_daily_report(
        report_date=target_date,
        generate_category_summaries=True,
        generate_pdf=False
    )
    
    print('\n' + '=' * 80)
    print('✅ 报告生成成功！')
    print('=' * 80)
    print(f'\n报告ID: {report.id}')
    print(f'报告日期: {report.report_date}')
    print(f'文章数量: {saved_count} 篇')
    print(f'HTML内容长度: {len(report.html_content)} 字符')
    print(f'总体总结长度: {len(report.overall_summary)} 字符')
    
    print(f'\n✅ 报告已保存')
    print(f'\n可以访问以下地址查看报告:')
    print(f'  http://localhost:9998/report-detail.html?date={target_date}')
    print('\n' + '=' * 80)
    
except Exception as e:
    print(f'\n❌ 处理失败: {e}')
    import traceback
    traceback.print_exc()

db.close()
