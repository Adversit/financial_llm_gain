"""
验证爬虫数据完整性
检查每个爬虫返回的数据是否包含：标题、链接、内容、发布时间
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models.source import Source
from app.crawlers.factory import CrawlerFactory
from app.config import get_config


def validate_article(article, source_name):
    """
    验证单篇文章数据完整性
    
    Args:
        article: Article对象
        source_name: 信息源名称
    
    Returns:
        dict: 验证结果
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # 检查标题
    if not hasattr(article, 'title') or not article.title:
        result['valid'] = False
        result['errors'].append('❌ 缺少标题')
    elif len(article.title.strip()) < 5:
        result['warnings'].append(f'⚠️ 标题过短: "{article.title}"')
    
    # 检查链接
    if not hasattr(article, 'link') or not article.link:
        result['valid'] = False
        result['errors'].append('❌ 缺少链接')
    elif not article.link.startswith('http'):
        result['warnings'].append(f'⚠️ 链接格式可能有误: {article.link}')
    
    # 检查内容
    if not hasattr(article, 'content') or not article.content:
        result['valid'] = False
        result['errors'].append('❌ 缺少内容')
    elif len(article.content.strip()) < 10:
        result['warnings'].append(f'⚠️ 内容过短 ({len(article.content)} 字符)')
    
    # 检查发布时间
    if not hasattr(article, 'publish_time') or not article.publish_time:
        result['valid'] = False
        result['errors'].append('❌ 缺少发布时间')
    elif not isinstance(article.publish_time, datetime):
        result['warnings'].append(f'⚠️ 发布时间类型错误: {type(article.publish_time)}')
    
    return result


def validate_source(source, config):
    """
    验证单个信息源
    
    Args:
        source: Source对象
        config: 配置字典
    
    Returns:
        dict: 验证结果
    """
    result = {
        'name': source.name,
        'type': source.type,
        'success': False,
        'article_count': 0,
        'valid_articles': 0,
        'invalid_articles': 0,
        'errors': [],
        'warnings': [],
        'sample_articles': []
    }
    
    try:
        print(f"\n{'='*80}")
        print(f"验证: {source.name} ({source.type})")
        print(f"{'='*80}")
        
        # 创建爬虫
        crawler = CrawlerFactory.create_crawler(
            source_type=source.type,
            source_name=source.name,
            url=source.url,
            rsshub_base=config['rsshub']['base_url'] if source.type == 'rsshub' else None,
            rsshub_route=source.rsshub_route,
            crawler_class=source.crawler_class
        )
        
        # 执行爬取
        articles = crawler.fetch()
        result['article_count'] = len(articles)
        
        if not articles:
            result['warnings'].append('⚠️ 未获取到任何文章')
            print(f"⚠️ 未获取到文章")
            return result
        
        print(f"✅ 获取 {len(articles)} 篇文章")
        print(f"\n开始验证数据完整性...")
        
        # 验证每篇文章
        for i, article in enumerate(articles[:5], 1):  # 只验证前5篇
            validation = validate_article(article, source.name)
            
            if validation['valid']:
                result['valid_articles'] += 1
            else:
                result['invalid_articles'] += 1
            
            # 收集样本
            sample = {
                'index': i,
                'title': article.title if hasattr(article, 'title') else 'N/A',
                'link': article.link if hasattr(article, 'link') else 'N/A',
                'content_length': len(article.content) if hasattr(article, 'content') else 0,
                'publish_time': str(article.publish_time) if hasattr(article, 'publish_time') else 'N/A',
                'valid': validation['valid'],
                'errors': validation['errors'],
                'warnings': validation['warnings']
            }
            result['sample_articles'].append(sample)
            
            # 打印验证结果
            status = "✅" if validation['valid'] else "❌"
            print(f"\n{status} 文章 {i}:")
            print(f"   标题: {sample['title'][:60]}...")
            print(f"   链接: {sample['link'][:60]}...")
            print(f"   内容长度: {sample['content_length']} 字符")
            print(f"   发布时间: {sample['publish_time']}")
            
            if validation['errors']:
                for error in validation['errors']:
                    print(f"   {error}")
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    print(f"   {warning}")
        
        # 计算有效率
        total_validated = len(result['sample_articles'])
        if total_validated > 0:
            valid_rate = (result['valid_articles'] / total_validated) * 100
            print(f"\n数据完整性: {result['valid_articles']}/{total_validated} ({valid_rate:.1f}%)")
            
            if valid_rate == 100:
                print("🎉 所有文章数据完整！")
                result['success'] = True
            elif valid_rate >= 80:
                print("✅ 大部分文章数据完整")
                result['success'] = True
            else:
                print("⚠️ 数据完整性较低，需要优化")
        
    except Exception as e:
        result['errors'].append(f"爬取失败: {str(e)}")
        print(f"❌ 错误: {e}")
    
    return result


def print_summary(results):
    """打印验证总结"""
    print("\n" + "="*80)
    print("验证总结")
    print("="*80)
    
    total = len(results)
    success = sum(1 for r in results if r['success'])
    total_articles = sum(r['article_count'] for r in results)
    total_valid = sum(r['valid_articles'] for r in results)
    total_invalid = sum(r['invalid_articles'] for r in results)
    
    print(f"\n📊 总体统计:")
    print(f"  - 测试信息源: {total}")
    print(f"  - 通过验证: {success} ({success/total*100:.1f}%)")
    print(f"  - 总文章数: {total_articles}")
    print(f"  - 有效文章: {total_valid}")
    print(f"  - 无效文章: {total_invalid}")
    
    if total_valid + total_invalid > 0:
        valid_rate = (total_valid / (total_valid + total_invalid)) * 100
        print(f"  - 数据完整率: {valid_rate:.1f}%")
    
    # 按类型分组
    by_type = {}
    for result in results:
        type_name = result['type']
        if type_name not in by_type:
            by_type[type_name] = []
        by_type[type_name].append(result)
    
    for type_name, type_results in by_type.items():
        print(f"\n{type_name.upper()} 源:")
        for result in type_results:
            status = "✅" if result['success'] else "❌"
            count = f"({result['article_count']}篇)" if result['article_count'] > 0 else ""
            valid_info = ""
            if result['valid_articles'] > 0 or result['invalid_articles'] > 0:
                valid_info = f" - 有效:{result['valid_articles']}/无效:{result['invalid_articles']}"
            print(f"  {status} {result['name']:30s} {count}{valid_info}")
    
    # 数据质量问题
    print(f"\n⚠️ 常见问题:")
    all_warnings = []
    for result in results:
        for sample in result.get('sample_articles', []):
            all_warnings.extend(sample.get('warnings', []))
    
    if all_warnings:
        warning_counts = {}
        for warning in all_warnings:
            warning_counts[warning] = warning_counts.get(warning, 0) + 1
        
        for warning, count in sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {warning} (出现{count}次)")
    else:
        print(f"  无")
    
    # 建议
    print(f"\n💡 建议:")
    if total_invalid > 0:
        print(f"  1. 修复无效文章的数据提取逻辑")
    
    failed_sources = [r for r in results if not r['success'] and r['article_count'] == 0]
    if failed_sources:
        print(f"  2. 检查以下源的爬取逻辑:")
        for r in failed_sources:
            print(f"     - {r['name']}")
    
    short_content = sum(1 for r in results for s in r.get('sample_articles', []) 
                       if any('内容过短' in w for w in s.get('warnings', [])))
    if short_content > 0:
        print(f"  3. 优化内容提取，避免内容过短")
    
    if valid_rate >= 90:
        print(f"\n🎉 数据质量优秀！系统可以正常使用。")
    elif valid_rate >= 70:
        print(f"\n✅ 数据质量良好，建议优化部分源。")
    else:
        print(f"\n⚠️ 数据质量需要改进。")


def main():
    """主函数"""
    print("="*80)
    print("爬虫数据完整性验证工具")
    print("="*80)
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n检查项目:")
    print(f"  ✓ 标题 (title)")
    print(f"  ✓ 链接 (link)")
    print(f"  ✓ 内容 (content)")
    print(f"  ✓ 发布时间 (publish_time)")
    
    try:
        # 加载配置
        config = get_config()
        
        # 获取所有启用的信息源
        db = SessionLocal()
        sources = db.query(Source).filter(Source.enabled == True).all()
        db.close()
        
        print(f"\n将验证 {len(sources)} 个启用的信息源")
        
        response = input("\n是否继续? (Y/n): ").strip().lower()
        if response and response != 'y':
            print("已取消")
            return
        
        # 验证所有信息源
        results = []
        for i, source in enumerate(sources, 1):
            print(f"\n[{i}/{len(sources)}]", end=" ")
            result = validate_source(source, config)
            results.append(result)
        
        # 打印总结
        print_summary(results)
        
        # 保存报告
        report_file = Path("logs") / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"爬虫数据完整性验证报告\n")
            f.write(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"="*80 + "\n\n")
            
            for result in results:
                f.write(f"信息源: {result['name']}\n")
                f.write(f"类型: {result['type']}\n")
                f.write(f"状态: {'通过' if result['success'] else '失败'}\n")
                f.write(f"文章数: {result['article_count']}\n")
                f.write(f"有效文章: {result['valid_articles']}\n")
                f.write(f"无效文章: {result['invalid_articles']}\n")
                
                if result['sample_articles']:
                    f.write(f"\n样本文章:\n")
                    for sample in result['sample_articles']:
                        f.write(f"\n  文章 {sample['index']}:\n")
                        f.write(f"    标题: {sample['title']}\n")
                        f.write(f"    链接: {sample['link']}\n")
                        f.write(f"    内容长度: {sample['content_length']}\n")
                        f.write(f"    发布时间: {sample['publish_time']}\n")
                        f.write(f"    有效: {'是' if sample['valid'] else '否'}\n")
                        
                        if sample['errors']:
                            f.write(f"    错误:\n")
                            for error in sample['errors']:
                                f.write(f"      {error}\n")
                        
                        if sample['warnings']:
                            f.write(f"    警告:\n")
                            for warning in sample['warnings']:
                                f.write(f"      {warning}\n")
                
                f.write("\n" + "-"*80 + "\n\n")
        
        print(f"\n验证报告已保存到: {report_file}")
        
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
