"""
快速测试所有信息源（包括禁用的）
"""
import yaml
from app.crawlers.factory import CrawlerFactory
from datetime import datetime
import sys

def test_source(source_type, source_config, rsshub_base=None):
    """测试单个信息源"""
    source_name = source_config.get('name', 'Unknown')
    enabled = source_config.get('enabled', False)
    
    result = {
        'name': source_name,
        'type': source_type,
        'enabled': enabled,
        'status': 'SKIP',
        'articles': 0,
        'error': ''
    }
    
    # 如果禁用，也尝试测试
    try:
        if source_type == 'rss':
            url = source_config.get('url')
            if not url:
                result['status'] = 'CONFIG_ERROR'
                result['error'] = 'Missing URL'
                return result
            crawler = CrawlerFactory.create_crawler(
                source_type='rss',
                source_name=source_name,
                url=url
            )
        elif source_type == 'rsshub':
            route = source_config.get('route')
            if not route or not rsshub_base:
                result['status'] = 'CONFIG_ERROR'
                result['error'] = 'Missing route or base'
                return result
            crawler = CrawlerFactory.create_crawler(
                source_type='rsshub',
                source_name=source_name,
                rsshub_base=rsshub_base,
                rsshub_route=route
            )
        elif source_type == 'custom':
            crawler_class = source_config.get('crawler_class')
            url = source_config.get('url')
            if not crawler_class:
                result['status'] = 'CONFIG_ERROR'
                result['error'] = 'Missing crawler_class'
                return result
            crawler = CrawlerFactory.create_crawler(
                source_type='custom',
                source_name=source_name,
                url=url,
                crawler_class=crawler_class
            )
        
        articles = crawler.fetch()
        
        if articles and len(articles) > 0:
            result['status'] = 'OK'
            result['articles'] = len(articles)
        else:
            result['status'] = 'EMPTY'
            
    except Exception as e:
        result['status'] = 'ERROR'
        result['error'] = str(e)[:80]
    
    return result


def main():
    print("="*100)
    print(f"测试所有信息源 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    rsshub_base = config.get('rsshub', {}).get('base_url')
    results = []
    
    total_sources = len(config['sources']['rss']) + len(config['sources']['rsshub']) + len(config['sources']['custom'])
    current = 0
    
    # 测试RSS源
    print(f"\n[1/3] 测试RSS源 ({len(config['sources']['rss'])} 个)...")
    for source in config['sources']['rss']:
        current += 1
        name = source['name']
        enabled = "✓" if source.get('enabled', False) else "✗"
        print(f"  [{current}/{total_sources}] {enabled} {name:<40}", end=' ')
        sys.stdout.flush()
        
        result = test_source('rss', source)
        results.append(result)
        
        if result['status'] == 'OK':
            print(f"OK ({result['articles']} 篇)")
        elif result['status'] == 'EMPTY':
            print(f"EMPTY")
        elif result['status'] == 'CONFIG_ERROR':
            print(f"CONFIG_ERROR: {result['error']}")
        else:
            print(f"ERROR: {result['error'][:50]}")
    
    # 测试RSSHub源
    print(f"\n[2/3] 测试RSSHub源 ({len(config['sources']['rsshub'])} 个)...")
    for source in config['sources']['rsshub']:
        current += 1
        name = source['name']
        enabled = "✓" if source.get('enabled', False) else "✗"
        print(f"  [{current}/{total_sources}] {enabled} {name:<40}", end=' ')
        sys.stdout.flush()
        
        result = test_source('rsshub', source, rsshub_base)
        results.append(result)
        
        if result['status'] == 'OK':
            print(f"OK ({result['articles']} 篇)")
        elif result['status'] == 'EMPTY':
            print(f"EMPTY")
        elif result['status'] == 'CONFIG_ERROR':
            print(f"CONFIG_ERROR: {result['error']}")
        else:
            print(f"ERROR: {result['error'][:50]}")
    
    # 测试自定义爬虫
    print(f"\n[3/3] 测试自定义爬虫 ({len(config['sources']['custom'])} 个)...")
    for source in config['sources']['custom']:
        current += 1
        name = source['name']
        enabled = "✓" if source.get('enabled', False) else "✗"
        print(f"  [{current}/{total_sources}] {enabled} {name:<40}", end=' ')
        sys.stdout.flush()
        
        result = test_source('custom', source)
        results.append(result)
        
        if result['status'] == 'OK':
            print(f"OK ({result['articles']} 篇)")
        elif result['status'] == 'EMPTY':
            print(f"EMPTY")
        elif result['status'] == 'CONFIG_ERROR':
            print(f"CONFIG_ERROR: {result['error']}")
        else:
            print(f"ERROR: {result['error'][:50]}")
    
    # 统计
    print("\n" + "="*100)
    print("测试结果统计")
    print("="*100)
    
    ok = len([r for r in results if r['status'] == 'OK'])
    empty = len([r for r in results if r['status'] == 'EMPTY'])
    error = len([r for r in results if r['status'] == 'ERROR'])
    config_error = len([r for r in results if r['status'] == 'CONFIG_ERROR'])
    total = len(results)
    
    enabled_results = [r for r in results if r['enabled']]
    enabled_ok = len([r for r in enabled_results if r['status'] == 'OK'])
    
    print(f"\n总计: {total} 个信息源")
    print(f"  OK (可用):          {ok} 个 ({ok/total*100:.1f}%)")
    print(f"  EMPTY (无数据):     {empty} 个 ({empty/total*100:.1f}%)")
    print(f"  ERROR (错误):       {error} 个 ({error/total*100:.1f}%)")
    print(f"  CONFIG_ERROR (配置): {config_error} 个 ({config_error/total*100:.1f}%)")
    
    print(f"\n启用的源: {len(enabled_results)} 个")
    print(f"  可用: {enabled_ok} 个 ({enabled_ok/len(enabled_results)*100:.1f}%)")
    
    # 按类型统计
    print("\n按类型统计:")
    for stype in ['rss', 'rsshub', 'custom']:
        type_results = [r for r in results if r['type'] == stype]
        if type_results:
            type_ok = len([r for r in type_results if r['status'] == 'OK'])
            type_enabled = len([r for r in type_results if r['enabled']])
            print(f"  {stype.upper():<10} 总计: {len(type_results):<3} 可用: {type_ok:<3} 启用: {type_enabled:<3} 可用率: {type_ok/len(type_results)*100:.1f}%")
    
    # 显示可用的源
    print("\n" + "="*100)
    print("可用的信息源")
    print("="*100)
    ok_results = [r for r in results if r['status'] == 'OK']
    for r in ok_results:
        enabled_mark = "✓" if r['enabled'] else "✗"
        print(f"  {enabled_mark} {r['name']:<45} {r['type']:<10} {r['articles']:>3} 篇")
    
    # 显示失败的源
    failed = [r for r in results if r['status'] in ['ERROR', 'CONFIG_ERROR']]
    if failed:
        print("\n" + "="*100)
        print("失败的信息源")
        print("="*100)
        for r in failed:
            enabled_mark = "✓" if r['enabled'] else "✗"
            print(f"  {enabled_mark} {r['name']:<45} {r['status']:<15} {r['error'][:50]}")
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"all_sources_test_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*100 + "\n")
        f.write(f"所有信息源测试结果 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*100 + "\n\n")
        
        f.write(f"总计: {total} 个信息源\n")
        f.write(f"可用: {ok} 个 ({ok/total*100:.1f}%)\n")
        f.write(f"启用的源可用率: {enabled_ok}/{len(enabled_results)} ({enabled_ok/len(enabled_results)*100:.1f}%)\n\n")
        
        f.write("可用的信息源:\n")
        f.write("-"*100 + "\n")
        for r in ok_results:
            enabled_mark = "✓" if r['enabled'] else "✗"
            f.write(f"{enabled_mark} {r['name']:<45} {r['type']:<10} {r['articles']:>3} 篇\n")
        
        if failed:
            f.write("\n失败的信息源:\n")
            f.write("-"*100 + "\n")
            for r in failed:
                enabled_mark = "✓" if r['enabled'] else "✗"
                f.write(f"{enabled_mark} {r['name']:<45} {r['status']:<15} {r['error']}\n")
    
    print(f"\n结果已保存到: {filename}")


if __name__ == "__main__":
    main()
