"""
快速测试所有启用的信息源
"""
import yaml
from app.crawlers.factory import CrawlerFactory
from datetime import datetime

def test_source(source_type, source_config, rsshub_base=None):
    """测试单个信息源"""
    source_name = source_config.get('name', 'Unknown')
    enabled = source_config.get('enabled', False)
    
    if not enabled:
        return None
    
    result = {
        'name': source_name,
        'type': source_type,
        'status': 'ERROR',
        'articles': 0
    }
    
    try:
        if source_type == 'rss':
            crawler = CrawlerFactory.create_crawler(
                source_type='rss',
                source_name=source_name,
                url=source_config.get('url')
            )
        elif source_type == 'rsshub':
            crawler = CrawlerFactory.create_crawler(
                source_type='rsshub',
                source_name=source_name,
                rsshub_base=rsshub_base,
                rsshub_route=source_config.get('route')
            )
        elif source_type == 'custom':
            crawler = CrawlerFactory.create_crawler(
                source_type='custom',
                source_name=source_name,
                url=source_config.get('url'),
                crawler_class=source_config.get('crawler_class')
            )
        
        articles = crawler.fetch()
        
        if articles and len(articles) > 0:
            result['status'] = 'OK'
            result['articles'] = len(articles)
        else:
            result['status'] = 'EMPTY'
            
    except Exception as e:
        result['status'] = 'ERROR'
        result['error'] = str(e)[:50]
    
    return result


def main():
    print("="*80)
    print(f"测试启用的信息源 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    rsshub_base = config.get('rsshub', {}).get('base_url')
    results = []
    
    # 测试RSS源
    print("\n[1/3] 测试RSS源...")
    for i, source in enumerate(config['sources']['rss'], 1):
        if source.get('enabled', False):
            print(f"  [{i}] {source['name']}", end=' ... ')
            result = test_source('rss', source)
            if result:
                results.append(result)
                print(f"{result['status']} ({result['articles']} 篇)")
    
    # 测试RSSHub源
    print("\n[2/3] 测试RSSHub源...")
    for i, source in enumerate(config['sources']['rsshub'], 1):
        if source.get('enabled', False):
            print(f"  [{i}] {source['name']}", end=' ... ')
            result = test_source('rsshub', source, rsshub_base)
            if result:
                results.append(result)
                print(f"{result['status']} ({result['articles']} 篇)")
    
    # 测试自定义爬虫
    print("\n[3/3] 测试自定义爬虫...")
    for i, source in enumerate(config['sources']['custom'], 1):
        if source.get('enabled', False):
            print(f"  [{i}] {source['name']}", end=' ... ')
            result = test_source('custom', source)
            if result:
                results.append(result)
                print(f"{result['status']} ({result['articles']} 篇)")
    
    # 统计
    print("\n" + "="*80)
    print("测试结果统计")
    print("="*80)
    
    ok = len([r for r in results if r['status'] == 'OK'])
    empty = len([r for r in results if r['status'] == 'EMPTY'])
    error = len([r for r in results if r['status'] == 'ERROR'])
    total = len(results)
    
    print(f"\n总计测试: {total} 个启用的信息源")
    print(f"  OK (可用):      {ok} 个 ({ok/total*100:.1f}%)")
    print(f"  EMPTY (无数据): {empty} 个 ({empty/total*100:.1f}%)")
    print(f"  ERROR (错误):   {error} 个 ({error/total*100:.1f}%)")
    
    # 按类型统计
    print("\n按类型统计:")
    for stype in ['rss', 'rsshub', 'custom']:
        type_results = [r for r in results if r['type'] == stype]
        if type_results:
            type_ok = len([r for r in type_results if r['status'] == 'OK'])
            print(f"  {stype.upper()}: {type_ok}/{len(type_results)} 可用 ({type_ok/len(type_results)*100:.1f}%)")
    
    # 显示失败的源
    failed = [r for r in results if r['status'] in ['ERROR', 'EMPTY']]
    if failed:
        print("\n失败的信息源:")
        for r in failed:
            print(f"  - {r['name']} ({r['status']})")


if __name__ == "__main__":
    main()
