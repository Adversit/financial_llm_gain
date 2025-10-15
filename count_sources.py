import yaml

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

rss_count = len(config['sources']['rss'])
rsshub_count = len(config['sources']['rsshub'])
custom_count = len(config['sources']['custom'])
total = rss_count + rsshub_count + custom_count

rss_enabled = len([s for s in config['sources']['rss'] if s.get('enabled', False)])
rsshub_enabled = len([s for s in config['sources']['rsshub'] if s.get('enabled', False)])
custom_enabled = len([s for s in config['sources']['custom'] if s.get('enabled', False)])
total_enabled = rss_enabled + rsshub_enabled + custom_enabled

print("="*60)
print("信息源统计")
print("="*60)
print(f"\nRSS源:      {rss_count} 个 (启用: {rss_enabled})")
print(f"RSSHub源:   {rsshub_count} 个 (启用: {rsshub_enabled})")
print(f"自定义爬虫: {custom_count} 个 (启用: {custom_enabled})")
print(f"\n总计:       {total} 个 (启用: {total_enabled})")
print(f"启用率:     {total_enabled/total*100:.1f}%")
