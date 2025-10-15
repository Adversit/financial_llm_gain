"""
启用所有测试通过的可用源
"""
import yaml

# 根据测试结果，这些源是可用的但未启用的
sources_to_enable = [
    ("rsshub", "arXiv 计算金融"),
    ("rsshub", "TechCrunch"),
]

# 读取配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

enabled_count = 0

# 启用源
for source_type, source_name in sources_to_enable:
    sources_list = config['sources'][source_type]
    for source in sources_list:
        if source['name'] == source_name:
            if not source.get('enabled', False):
                source['enabled'] = True
                enabled_count += 1
                print(f"✓ 已启用: {source_name} ({source_type})")
            else:
                print(f"  已经启用: {source_name}")

# 保存配置
with open('config.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print(f"\n总计启用了 {enabled_count} 个新源")

# 统计
rss_enabled = len([s for s in config['sources']['rss'] if s.get('enabled', False)])
rsshub_enabled = len([s for s in config['sources']['rsshub'] if s.get('enabled', False)])
custom_enabled = len([s for s in config['sources']['custom'] if s.get('enabled', False)])
total_enabled = rss_enabled + rsshub_enabled + custom_enabled

print(f"\n当前启用的源:")
print(f"  RSS源: {rss_enabled}")
print(f"  RSSHub源: {rsshub_enabled}")
print(f"  自定义爬虫: {custom_enabled}")
print(f"  总计: {total_enabled}")
