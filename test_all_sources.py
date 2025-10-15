"""
测试所有信息源的可用性
"""
import yaml
from app.crawlers.factory import CrawlerFactory
from app.utils.logger import setup_logger
from datetime import datetime

logger = setup_logger('test_all_sources')


def load_config():
    """加载配置文件"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def test_source(source_type, source_config, rsshub_base=None):
    """测试单个信息源"""
    source_name = source_config.get('name', 'Unknown')
    category = source_config.get('category', 'Unknown')
    enabled = source_config.get('enabled', False)
    
    result = {
        'name': source_name,
        'category': category,
        'type': source_type,
        'enabled': enabled,
        'status': 'SKIP',
        'method': '',
        'articles': 0,
        'error': ''
    }
    
    # 如果未启用，跳过测试
    if not enabled:
        result['status'] = 'DISABLED'
        result['method'] = get_method_name(source_type, source_config)
        return result
    
    try:
        # 创建爬虫
        if source_type == 'rss':
            url = source_config.get('url')
            crawler = CrawlerFactory.create_crawler(
                source_type='rss',
                source_name=source_name,
                url=url
            )
            result['method'] = 'RSSStrategy'
            
        elif source_type == 'rsshub':
            route = source_config.get('route')
            crawler = CrawlerFactory.create_crawler(
                source_type='rsshub',
                source_name=source_name,
                rsshub_base=rsshub_base,
                rsshub_route=route
            )
            result['method'] = 'RSSHubStrategy'
            
        elif source_type == 'custom':
            crawler_class = source_config.get('crawler_class')
            url = source_config.get('url')
            crawler = CrawlerFactory.create_crawler(
                source_type='custom',
                source_name=source_name,
                url=url,
                crawler_class=crawler_class
            )
            result['method'] = crawler_class
        
        # 执行爬取
        articles = crawler.fetch()
        
        if articles and len(articles) > 0:
            result['status'] = 'OK'
            result['articles'] = len(articles)
        else:
            result['status'] = 'EMPTY'
            
    except Exception as e:
        result['status'] = 'ERROR'
        result['error'] = str(e)[:100]
    
    return result


def get_method_name(source_type, source_config):
    """获取爬取方法名称"""
    if source_type == 'rss':
        return 'RSSStrategy'
    elif source_type == 'rsshub':
        return 'RSSHubStrategy'
    elif source_type == 'custom':
        return source_config.get('crawler_class', 'CustomCrawler')
    return 'Unknown'


def print_results(results):
    """打印测试结果"""
    print("\n" + "="*100)
    print("所有信息源测试结果")
    print("="*100)
    
    # 按类型分组
    rss_results = [r for r in results if r['type'] == 'rss']
    rsshub_results = [r for r in results if r['type'] == 'rsshub']
    custom_results = [r for r in results if r['type'] == 'custom']
    
    # 打印RSS源
    print("\n【RSS源】")
    print("-"*100)
    print(f"{'状态':<8} {'名称':<30} {'类别':<10} {'方法':<20} {'文章数':<8}")
    print("-"*100)
    for r in rss_results:
        status_icon = get_status_icon(r['status'])
        print(f"{status_icon:<8} {r['name']:<30} {r['category']:<10} {r['method']:<20} {r['articles']:<8}")
    
    # 打印RSSHub源
    print("\n【RSSHub源】")
    print("-"*100)
    print(f"{'状态':<8} {'名称':<30} {'类别':<10} {'方法':<20} {'文章数':<8}")
    print("-"*100)
    for r in rsshub_results:
        status_icon = get_status_icon(r['status'])
        print(f"{status_icon:<8} {r['name']:<30} {r['category']:<10} {r['method']:<20} {r['articles']:<8}")
    
    # 打印自定义爬虫源
    print("\n【自定义爬虫源】")
    print("-"*100)
    print(f"{'状态':<8} {'名称':<30} {'类别':<10} {'方法':<20} {'文章数':<8}")
    print("-"*100)
    for r in custom_results:
        status_icon = get_status_icon(r['status'])
        print(f"{status_icon:<8} {r['name']:<30} {r['category']:<10} {r['method']:<20} {r['articles']:<8}")
    
    # 统计
    print("\n" + "="*100)
    print("统计信息")
    print("="*100)
    
    total = len(results)
    ok = len([r for r in results if r['status'] == 'OK'])
    empty = len([r for r in results if r['status'] == 'EMPTY'])
    error = len([r for r in results if r['status'] == 'ERROR'])
    disabled = len([r for r in results if r['status'] == 'DISABLED'])
    
    print(f"\n总计: {total} 个信息源")
    print(f"  - OK (可用):      {ok} 个")
    print(f"  - EMPTY (无数据): {empty} 个")
    print(f"  - ERROR (错误):   {error} 个")
    print(f"  - DISABLED (禁用): {disabled} 个")
    print(f"\n可用率: {ok}/{total-disabled} = {ok/(total-disabled)*100:.1f}%")
    
    # 按类型统计
    print("\n按类型统计:")
    for source_type in ['rss', 'rsshub', 'custom']:
        type_results = [r for r in results if r['type'] == source_type]
        type_ok = len([r for r in type_results if r['status'] == 'OK'])
        type_total = len([r for r in type_results if r['status'] != 'DISABLED'])
        if type_total > 0:
            print(f"  - {source_type.upper()}: {type_ok}/{type_total} = {type_ok/type_total*100:.1f}%")


def get_status_icon(status):
    """获取状态图标"""
    icons = {
        'OK': 'OK',
        'EMPTY': 'EMPTY',
        'ERROR': 'ERROR',
        'DISABLED': 'SKIP',
        'SKIP': 'SKIP'
    }
    return icons.get(status, '?')


def main():
    """主函数"""
    print("="*100)
    print(f"开始测试所有信息源 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    # 加载配置
    config = load_config()
    rsshub_base = config.get('rsshub', {}).get('base_url')
    
    results = []
    
    # 测试RSS源
    print("\n正在测试RSS源...")
    for source in config['sources']['rss']:
        print(f"  测试: {source['name']}")
        result = test_source('rss', source)
        results.append(result)
    
    # 测试RSSHub源
    print("\n正在测试RSSHub源...")
    for source in config['sources']['rsshub']:
        print(f"  测试: {source['name']}")
        result = test_source('rsshub', source, rsshub_base)
        results.append(result)
    
    # 测试自定义爬虫源
    print("\n正在测试自定义爬虫源...")
    for source in config['sources']['custom']:
        print(f"  测试: {source['name']}")
        result = test_source('custom', source)
        results.append(result)
    
    # 打印结果
    print_results(results)
    
    # 保存结果到文件
    save_results_to_file(results)


def save_results_to_file(results):
    """保存结果到文件"""
    filename = f"source_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*100 + "\n")
        f.write("所有信息源测试结果\n")
        f.write("="*100 + "\n\n")
        
        # 可用源
        f.write("【可用的信息源】\n")
        f.write("-"*100 + "\n")
        ok_results = [r for r in results if r['status'] == 'OK']
        for r in ok_results:
            f.write(f"OK  {r['name']:<35} -> {r['method']:<25} ({r['articles']} 篇文章)\n")
        
        # 不可用源
        f.write("\n【不可用的信息源】\n")
        f.write("-"*100 + "\n")
        not_ok_results = [r for r in results if r['status'] in ['ERROR', 'EMPTY'] and r['enabled']]
        for r in not_ok_results:
            f.write(f"{r['status']:<6} {r['name']:<35} -> {r['method']:<25}\n")
            if r['error']:
                f.write(f"       错误: {r['error']}\n")
        
        # 禁用源
        f.write("\n【已禁用的信息源】\n")
        f.write("-"*100 + "\n")
        disabled_results = [r for r in results if r['status'] == 'DISABLED']
        for r in disabled_results:
            f.write(f"SKIP {r['name']:<35} -> {r['method']:<25}\n")
        
        # 统计
        total = len(results)
        ok = len([r for r in results if r['status'] == 'OK'])
        disabled = len([r for r in results if r['status'] == 'DISABLED'])
        
        f.write("\n" + "="*100 + "\n")
        f.write("统计信息\n")
        f.write("="*100 + "\n")
        f.write(f"总计: {total} 个信息源\n")
        f.write(f"可用: {ok} 个\n")
        f.write(f"禁用: {disabled} 个\n")
        f.write(f"可用率: {ok}/{total-disabled} = {ok/(total-disabled)*100:.1f}%\n")
    
    print(f"\n结果已保存到: {filename}")


if __name__ == "__main__":
    main()
