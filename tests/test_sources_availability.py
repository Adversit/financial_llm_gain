# -*- coding: utf-8 -*-
"""测试所有信息源的可用性和爬取方式"""
import sys
from pathlib import Path
import requests
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_config
from app.crawlers.factory import CrawlerFactory

print("=" * 80)
print("信息源可用性测试")
print("=" * 80)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# 加载配置
config = get_config()
sources_config = config.get('sources', {})

# 统计变量
total_sources = 0
available_sources = 0
unavailable_sources = 0
results = []

def test_rss_source(name, url):
    """测试RSS源"""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            return True, "RSS可用", response.status_code
        else:
            return False, f"HTTP {response.status_code}", response.status_code
    except requests.Timeout:
        return False, "超时", None
    except requests.ConnectionError:
        return False, "连接失败", None
    except Exception as e:
        return False, str(e)[:50], None

def test_rsshub_source(name, route, base_url):
    """测试RSSHub源"""
    try:
        url = f"{base_url}/{route}"
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            return True, "RSSHub可用", response.status_code
        else:
            return False, f"HTTP {response.status_code}", response.status_code
    except requests.Timeout:
        return False, "超时", None
    except requests.ConnectionError:
        return False, "连接失败", None
    except Exception as e:
        return False, str(e)[:50], None

def test_custom_source(name, url):
    """测试自定义源"""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            return True, "网站可访问", response.status_code
        else:
            return False, f"HTTP {response.status_code}", response.status_code
    except requests.Timeout:
        return False, "超时", None
    except requests.ConnectionError:
        return False, "连接失败", None
    except Exception as e:
        return False, str(e)[:50], None

# 测试RSS源
print("\n" + "=" * 80)
print("1. RSS源测试（公众号）")
print("=" * 80)

rss_sources = sources_config.get('rss', [])
print(f"共 {len(rss_sources)} 个RSS源\n")

for i, source in enumerate(rss_sources, 1):
    name = source.get('name', '未知')
    url = source.get('url', '')
    category = source.get('category', '未分类')
    enabled = source.get('enabled', True)
    
    total_sources += 1
    
    if not enabled:
        print(f"[{i:2d}] ⊘ {name:20s} - 已禁用")
        results.append({
            'type': 'RSS',
            'name': name,
            'category': category,
            'status': '已禁用',
            'method': 'RSS',
            'available': False
        })
        unavailable_sources += 1
        continue
    
    print(f"[{i:2d}] 测试 {name:20s} ... ", end='', flush=True)
    
    available, message, status_code = test_rss_source(name, url)
    
    if available:
        print(f"✓ {message}")
        available_sources += 1
        results.append({
            'type': 'RSS',
            'name': name,
            'category': category,
            'status': message,
            'method': 'RSSStrategy',
            'available': True,
            'url': url
        })
    else:
        print(f"✗ {message}")
        unavailable_sources += 1
        results.append({
            'type': 'RSS',
            'name': name,
            'category': category,
            'status': message,
            'method': 'RSSStrategy',
            'available': False,
            'url': url
        })

# 测试RSSHub源
print("\n" + "=" * 80)
print("2. RSSHub源测试")
print("=" * 80)

rsshub_sources = sources_config.get('rsshub', [])
rsshub_base = config.get('rsshub', {}).get('base_url', '')
print(f"共 {len(rsshub_sources)} 个RSSHub源")
print(f"RSSHub服务器: {rsshub_base}\n")

for i, source in enumerate(rsshub_sources, 1):
    name = source.get('name', '未知')
    route = source.get('route', '')
    category = source.get('category', '未分类')
    enabled = source.get('enabled', True)
    
    total_sources += 1
    
    if not enabled:
        print(f"[{i:2d}] ⊘ {name:30s} - 已禁用")
        results.append({
            'type': 'RSSHub',
            'name': name,
            'category': category,
            'status': '已禁用',
            'method': 'RSSHub',
            'available': False
        })
        unavailable_sources += 1
        continue
    
    print(f"[{i:2d}] 测试 {name:30s} ... ", end='', flush=True)
    
    available, message, status_code = test_rsshub_source(name, route, rsshub_base)
    
    if available:
        print(f"✓ {message}")
        available_sources += 1
        results.append({
            'type': 'RSSHub',
            'name': name,
            'category': category,
            'status': message,
            'method': 'RSSHubStrategy',
            'available': True,
            'route': route
        })
    else:
        print(f"✗ {message}")
        unavailable_sources += 1
        results.append({
            'type': 'RSSHub',
            'name': name,
            'category': category,
            'status': message,
            'method': 'RSSHubStrategy',
            'available': False,
            'route': route
        })

# 测试自定义源
print("\n" + "=" * 80)
print("3. 自定义爬虫源测试")
print("=" * 80)

custom_sources = sources_config.get('custom', [])
print(f"共 {len(custom_sources)} 个自定义源\n")

for i, source in enumerate(custom_sources, 1):
    name = source.get('name', '未知')
    url = source.get('url', '')
    category = source.get('category', '未分类')
    crawler_class = source.get('crawler_class', '')
    enabled = source.get('enabled', True)
    
    total_sources += 1
    
    if not enabled:
        print(f"[{i:2d}] ⊘ {name:30s} - 已禁用")
        results.append({
            'type': 'Custom',
            'name': name,
            'category': category,
            'status': '已禁用',
            'method': crawler_class,
            'available': False
        })
        unavailable_sources += 1
        continue
    
    print(f"[{i:2d}] 测试 {name:30s} ... ", end='', flush=True)
    
    available, message, status_code = test_custom_source(name, url)
    
    if available:
        print(f"✓ {message} (使用 {crawler_class})")
        available_sources += 1
        results.append({
            'type': 'Custom',
            'name': name,
            'category': category,
            'status': message,
            'method': crawler_class,
            'available': True,
            'url': url
        })
    else:
        print(f"✗ {message}")
        unavailable_sources += 1
        results.append({
            'type': 'Custom',
            'name': name,
            'category': category,
            'status': message,
            'method': crawler_class,
            'available': False,
            'url': url
        })

# 汇总统计
print("\n" + "=" * 80)
print("测试结果汇总")
print("=" * 80)

print(f"\n总计: {total_sources} 个信息源")
print(f"  ✓ 可用: {available_sources} 个 ({available_sources/total_sources*100:.1f}%)")
print(f"  ✗ 不可用: {unavailable_sources} 个 ({unavailable_sources/total_sources*100:.1f}%)")

# 按类型统计
print("\n按类型统计:")
type_stats = {}
for result in results:
    t = result['type']
    if t not in type_stats:
        type_stats[t] = {'total': 0, 'available': 0}
    type_stats[t]['total'] += 1
    if result['available']:
        type_stats[t]['available'] += 1

for t, stats in type_stats.items():
    total = stats['total']
    available = stats['available']
    print(f"  {t:10s}: {available}/{total} 可用 ({available/total*100:.1f}%)")

# 按分类统计
print("\n按分类统计:")
category_stats = {}
for result in results:
    cat = result['category']
    if cat not in category_stats:
        category_stats[cat] = {'total': 0, 'available': 0}
    category_stats[cat]['total'] += 1
    if result['available']:
        category_stats[cat]['available'] += 1

for cat, stats in sorted(category_stats.items()):
    total = stats['total']
    available = stats['available']
    print(f"  {cat:10s}: {available}/{total} 可用 ({available/total*100:.1f}%)")

# 推荐的爬取策略
print("\n" + "=" * 80)
print("推荐的爬取策略")
print("=" * 80)

print("\n可用的信息源及其爬取方式:")
print("-" * 80)

for result in results:
    if result['available']:
        print(f"✓ {result['name']:30s} [{result['category']:8s}] → {result['method']}")

print("\n不可用的信息源:")
print("-" * 80)

for result in results:
    if not result['available']:
        print(f"✗ {result['name']:30s} [{result['category']:8s}] - {result['status']}")

# 保存结果到文件
output_file = Path('logs') / f"source_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
output_file.parent.mkdir(exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("信息源可用性测试报告\n")
    f.write("=" * 80 + "\n")
    f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"总计: {total_sources} 个信息源\n")
    f.write(f"可用: {available_sources} 个 ({available_sources/total_sources*100:.1f}%)\n")
    f.write(f"不可用: {unavailable_sources} 个 ({unavailable_sources/total_sources*100:.1f}%)\n")
    f.write("\n" + "=" * 80 + "\n")
    f.write("详细结果\n")
    f.write("=" * 80 + "\n\n")
    
    for result in results:
        status_icon = "✓" if result['available'] else "✗"
        f.write(f"{status_icon} {result['name']:30s} [{result['type']:8s}] [{result['category']:8s}]\n")
        f.write(f"   状态: {result['status']}\n")
        f.write(f"   方法: {result['method']}\n")
        if 'url' in result:
            f.write(f"   URL: {result['url']}\n")
        if 'route' in result:
            f.write(f"   路由: {result['route']}\n")
        f.write("\n")

print(f"\n详细报告已保存到: {output_file}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)

# 返回状态码
if available_sources >= total_sources * 0.7:  # 70%以上可用
    print("\n✓ 大部分信息源可用，系统状态良好")
    sys.exit(0)
elif available_sources >= total_sources * 0.5:  # 50%以上可用
    print("\n⚠️  部分信息源不可用，建议检查")
    sys.exit(0)
else:
    print("\n✗ 大量信息源不可用，需要立即处理")
    sys.exit(1)
