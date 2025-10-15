# -*- coding: utf-8 -*-
"""测试新的配置文件"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("新配置文件测试")
print("=" * 60)

# 测试1: 加载配置
print("\n测试1: 加载配置文件")
print("-" * 60)

try:
    from app.config import get_config
    
    config = get_config()
    print("✓ 配置加载成功")
    print(f"  - 应用名称: {config['app']['name']}")
    print(f"  - 版本: {config['app']['version']}")
    
except Exception as e:
    print(f"✗ 配置加载失败: {e}")
    sys.exit(1)

# 测试2: 统计信息源
print("\n测试2: 统计信息源")
print("-" * 60)

try:
    sources = config.get('sources', {})
    
    rss_count = len(sources.get('rss', []))
    rsshub_count = len(sources.get('rsshub', []))
    custom_count = len(sources.get('custom', []))
    total_count = rss_count + rsshub_count + custom_count
    
    print(f"✓ 信息源统计:")
    print(f"  - RSS源: {rss_count} 个")
    print(f"  - RSSHub源: {rsshub_count} 个")
    print(f"  - 自定义爬虫: {custom_count} 个")
    print(f"  - 总计: {total_count} 个")
    
    if total_count < 50:
        print(f"\n⚠️  信息源数量较少，预期50+个")
    
except Exception as e:
    print(f"✗ 统计失败: {e}")

# 测试3: 检查分类
print("\n测试3: 检查信息源分类")
print("-" * 60)

try:
    categories = {}
    
    for source in sources.get('rss', []):
        cat = source.get('category', '未分类')
        categories[cat] = categories.get(cat, 0) + 1
    
    for source in sources.get('rsshub', []):
        cat = source.get('category', '未分类')
        categories[cat] = categories.get(cat, 0) + 1
    
    for source in sources.get('custom', []):
        cat = source.get('category', '未分类')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("✓ 分类统计:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat}: {count} 个")
    
except Exception as e:
    print(f"✗ 分类检查失败: {e}")

# 测试4: 检查启用状态
print("\n测试4: 检查信息源启用状态")
print("-" * 60)

try:
    enabled_count = 0
    disabled_count = 0
    
    for source in sources.get('rss', []):
        if source.get('enabled', True):
            enabled_count += 1
        else:
            disabled_count += 1
    
    for source in sources.get('rsshub', []):
        if source.get('enabled', True):
            enabled_count += 1
        else:
            disabled_count += 1
    
    for source in sources.get('custom', []):
        if source.get('enabled', True):
            enabled_count += 1
        else:
            disabled_count += 1
    
    print(f"✓ 启用状态:")
    print(f"  - 已启用: {enabled_count} 个")
    print(f"  - 已禁用: {disabled_count} 个")
    
except Exception as e:
    print(f"✗ 启用状态检查失败: {e}")

# 测试5: 检查重点信息源
print("\n测试5: 检查重点信息源")
print("-" * 60)

key_sources = [
    '移动支付网',
    '量子位',
    '机器之心',
    '工业和信息化部',
    '中国人民银行',
    '36氪',
    '财新网',
]

found_sources = []
missing_sources = []

for key_source in key_sources:
    found = False
    
    for source in sources.get('rss', []):
        if key_source in source.get('name', ''):
            found = True
            found_sources.append(key_source)
            break
    
    if not found:
        for source in sources.get('rsshub', []):
            if key_source in source.get('name', ''):
                found = True
                found_sources.append(key_source)
                break
    
    if not found:
        for source in sources.get('custom', []):
            if key_source in source.get('name', ''):
                found = True
                found_sources.append(key_source)
                break
    
    if not found:
        missing_sources.append(key_source)

print(f"✓ 重点信息源检查:")
print(f"  - 已找到: {len(found_sources)}/{len(key_sources)}")
for source in found_sources:
    print(f"    ✓ {source}")

if missing_sources:
    print(f"\n  - 缺失: {len(missing_sources)}")
    for source in missing_sources:
        print(f"    ✗ {source}")

# 测试6: 检查RSSHub配置
print("\n测试6: 检查RSSHub配置")
print("-" * 60)

try:
    rsshub_config = config.get('rsshub', {})
    base_url = rsshub_config.get('base_url', '')
    
    print(f"✓ RSSHub配置:")
    print(f"  - 基础URL: {base_url}")
    
    if '101.42.187.241' in base_url:
        print(f"  - 使用自建RSSHub服务器")
    
except Exception as e:
    print(f"✗ RSSHub配置检查失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

print("\n总结:")
print(f"✓ 配置文件加载正常")
print(f"✓ 信息源数量: {total_count} 个")
print(f"✓ 已启用: {enabled_count} 个")
print(f"✓ 分类完整: {len(categories)} 个分类")

if total_count >= 50:
    print("\n🎉 配置更新成功！信息源已大幅扩充！")
else:
    print(f"\n⚠️  信息源数量({total_count})少于预期(50+)")

print("\n下一步:")
print("1. 启动服务: python start_server.py")
print("2. 查看日志: tail -f logs/app.log")
print("3. 监控爬取: 观察各信息源的爬取情况")
