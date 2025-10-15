"""
快速列出所有信息源及其状态
"""
import yaml


def main():
    """列出所有信息源"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("="*100)
    print("所有信息源列表")
    print("="*100)
    
    # RSS源
    print("\n【RSS源】")
    print("-"*100)
    print(f"{'状态':<8} {'名称':<35} {'类别':<12} {'爬取方式':<20}")
    print("-"*100)
    for source in config['sources']['rss']:
        status = "✓ 可用" if source.get('enabled', False) else "✗ 禁用"
        name = source['name']
        category = source.get('category', 'N/A')
        method = "RSSStrategy"
        print(f"{status:<8} {name:<35} {category:<12} {method:<20}")
    
    # RSSHub源
    print("\n【RSSHub源】")
    print("-"*100)
    print(f"{'状态':<8} {'名称':<35} {'类别':<12} {'爬取方式':<20}")
    print("-"*100)
    for source in config['sources']['rsshub']:
        status = "✓ 可用" if source.get('enabled', False) else "✗ 禁用"
        name = source['name']
        category = source.get('category', 'N/A')
        method = "RSSHubStrategy"
        print(f"{status:<8} {name:<35} {category:<12} {method:<20}")
    
    # 自定义爬虫
    print("\n【自定义爬虫】")
    print("-"*100)
    print(f"{'状态':<8} {'名称':<35} {'类别':<12} {'爬取方式':<20}")
    print("-"*100)
    for source in config['sources']['custom']:
        status = "✓ 可用" if source.get('enabled', False) else "✗ 禁用"
        name = source['name']
        category = source.get('category', 'N/A')
        method = source.get('crawler_class', 'N/A')
        print(f"{status:<8} {name:<35} {category:<12} {method:<20}")
    
    # 统计
    print("\n" + "="*100)
    print("统计信息")
    print("="*100)
    
    rss_enabled = len([s for s in config['sources']['rss'] if s.get('enabled', False)])
    rss_total = len(config['sources']['rss'])
    
    rsshub_enabled = len([s for s in config['sources']['rsshub'] if s.get('enabled', False)])
    rsshub_total = len(config['sources']['rsshub'])
    
    custom_enabled = len([s for s in config['sources']['custom'] if s.get('enabled', False)])
    custom_total = len(config['sources']['custom'])
    
    total_enabled = rss_enabled + rsshub_enabled + custom_enabled
    total = rss_total + rsshub_total + custom_total
    
    print(f"\nRSS源:      {rss_enabled}/{rss_total} 可用")
    print(f"RSSHub源:   {rsshub_enabled}/{rsshub_total} 可用")
    print(f"自定义爬虫: {custom_enabled}/{custom_total} 可用")
    print(f"\n总计:       {total_enabled}/{total} 可用 ({total_enabled/total*100:.1f}%)")


if __name__ == "__main__":
    main()
