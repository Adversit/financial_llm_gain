"""
调试报告生成提示词
查看实际发送给 AI 的提示词内容
"""

import sys
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.article import Article
from app.models.summary import Summary
from app.services.report.aggregator import ReportAggregator
from pathlib import Path

def main():
    db = SessionLocal()
    
    # 使用昨天的日期
    test_date = (datetime.now() - timedelta(days=1)).date()
    print(f"📅 测试日期: {test_date}")
    print("="*80)
    
    # 聚合数据
    aggregator = ReportAggregator(db)
    report_data = aggregator.aggregate_report_data(test_date)
    
    # 统计信息
    print("\n📊 数据统计:")
    for category, data in report_data['categories'].items():
        article_count = len(data['articles'])
        print(f"  {category}: {article_count} 篇文章")
    
    # 读取提示词模板
    template_path = Path("prompts/daily_report.txt")
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    print(f"\n📝 提示词模板长度: {len(template)} 字符")
    
    # 构建各层面的摘要
    def format_summaries(summaries):
        if not summaries:
            return "（本层面暂无内容）"
        
        formatted = []
        for i, summary in enumerate(summaries, 1):
            max_length = 300
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            formatted.append(f"{i}. {summary}")
        
        return "\n".join(formatted)
    
    # 收集各层面摘要
    political_summaries = []
    economic_summaries = []
    technical_summaries = []
    fintech_summaries = []
    
    for category, data in report_data['categories'].items():
        summaries = [article['summary'] for article in data['articles'] if article['summary']]
        
        if category == '政治':
            political_summaries = summaries
        elif category == '经济':
            economic_summaries = summaries
        elif category == '技术':
            technical_summaries = summaries
        elif category == '金融科技':
            fintech_summaries = summaries
    
    # 格式化
    political = format_summaries(political_summaries)
    economic = format_summaries(economic_summaries)
    technical = format_summaries(technical_summaries)
    fintech = format_summaries(fintech_summaries)
    
    # 国内外信息（简化处理）
    domestic = "（暂无国内信息分类）"
    foreign = "（暂无国外信息分类）"
    
    # 构建完整提示词
    prompt = template.format(
        domestic_summaries=domestic,
        foreign_summaries=foreign,
        political_summaries=political,
        economic_summaries=economic,
        technical_summaries=technical,
        fintech_summaries=fintech
    )
    
    print(f"\n📏 完整提示词长度: {len(prompt)} 字符")
    print("\n" + "="*80)
    print("📄 完整提示词内容:")
    print("="*80)
    print(prompt)
    print("="*80)
    
    # 分析各部分长度
    print("\n📊 各部分长度分析:")
    print(f"  模板: {len(template)} 字符")
    print(f"  国内信息: {len(domestic)} 字符")
    print(f"  国外信息: {len(foreign)} 字符")
    print(f"  政治层面: {len(political)} 字符 ({len(political_summaries)} 条)")
    print(f"  经济层面: {len(economic)} 字符 ({len(economic_summaries)} 条)")
    print(f"  技术层面: {len(technical)} 字符 ({len(technical_summaries)} 条)")
    print(f"  金融科技层面: {len(fintech)} 字符 ({len(fintech_summaries)} 条)")
    
    # 建议
    print("\n💡 优化建议:")
    if len(prompt) > 8000:
        print("  ⚠️  提示词过长 (>8000字符)，可能导致超时")
        print("  建议:")
        print("    1. 减少每层面的摘要数量（当前最多15条）")
        print("    2. 缩短单条摘要长度（当前最多300字符）")
        print("    3. 简化提示词模板")
    elif len(prompt) > 6000:
        print("  ⚠️  提示词较长 (>6000字符)，可能响应较慢")
        print("  建议适当精简内容")
    else:
        print("  ✅ 提示词长度合理")
    
    db.close()

if __name__ == '__main__':
    main()
