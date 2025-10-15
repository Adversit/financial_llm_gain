# -*- coding: utf-8 -*-
"""详细的信息源测试 - 使用GET请求"""
import sys
import io
from pathlib import Path
import requests
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_config

print("=" * 80)
print("信息源详细测试（使用GET请求）")
print("=" * 80)

config = get_config()
sources_config = config.get('sources', {})

results = {
    'rss': {'total': 0, 'ok': 0, 'fail': 0, 'details': []},
    'rsshub': {'total': 0, 'ok': 0, 'fail': 0, 'details': []},
    'custom': {'total': 0, 'ok': 0, 'fail': 0, 'details': []}
}

def test_url(url, timeout=10):
    """测试URL可用性"""
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        return response.status_code, len(response.content), None
    except requests.Timeout:
        return None, 0, "超时"
    except requests.ConnectionError as e:
        return None, 0, f"连接失败: {str(e)[:50]}"
    except Exception as e:
        return None, 0, str(e)[:50]

# 测试RSS源
print("\n1. RSS源测试（使用GET请求）")
print("-" * 80)

rss_sources = sources_config.get('rss', [])
print(f"共 {len(rss_sources)} 个RSS源\n")

for i, source in enumerate(rss_sources, 1):  # 测试所有RSS源
    name = source.get('name', '未知')
    url = source.get('url', '')
    category = source.get('category', '')
    
    results['rss']['total'] += 1
    print(f"[{i:2d}] {name:20s} [{category:8s}] ... ", end='', flush=True)
    
    status, size, error = test_url(url)
    
    if status == 200 and size > 0:
        print(f"OK (HTTP {status}, {size} bytes)")
        results['rss']['ok'] += 1
        results['rss']['details'].append({
            'name': name,
            'status': 'OK',
            'method': 'RSSStrategy',
            'url': url
        })
    else:
        msg = error if error else f"HTTP {status}"
        print(f"FAIL ({msg})")
        results['rss']['fail'] += 1
        results['rss']['details'].append({
            'name': name,
            'status': 'FAIL',
            'error': msg
        })

# 测试RSSHub源
print("\n2. RSSHub源测试")
print("-" * 80)

rsshub_sources = sources_config.get('rsshub', [])
rsshub_base = config.get('rsshub', {}).get('base_url', '')
print(f"共 {len(rsshub_sources)} 个RSSHub源")
print(f"服务器: {rsshub_base}\n")

# 先测试RSSHub服务器
print("测试RSSHub服务器 ... ", end='', flush=True)
status, size, error = test_url(rsshub_base)
if status == 200:
    print(f"OK (HTTP {status})")
    rsshub_available = True
else:
    msg = error if error else f"HTTP {status}"
    print(f"FAIL ({msg})")
    print("警告: RSSHub服务器不可用，跳过RSSHub源测试\n")
    rsshub_available = False

if rsshub_available:
    for i, source in enumerate(rsshub_sources, 1):  # 测试所有RSSHub源
        name = source.get('name', '未知')
        route = source.get('route', '')
        category = source.get('category', '')
        url = f"{rsshub_base}/{route}"
        
        results['rsshub']['total'] += 1
        print(f"[{i:2d}] {name:30s} [{category:8s}] ... ", end='', flush=True)
        
        status, size, error = test_url(url)
        
        if status == 200 and size > 0:
            print(f"OK (HTTP {status}, {size} bytes)")
            results['rsshub']['ok'] += 1
            results['rsshub']['details'].append({
                'name': name,
                'status': 'OK',
                'method': 'RSSHubStrategy',
                'route': route
            })
        else:
            msg = error if error else f"HTTP {status}"
            print(f"FAIL ({msg})")
            results['rsshub']['fail'] += 1
            results['rsshub']['details'].append({
                'name': name,
                'status': 'FAIL',
                'error': msg
            })

# 测试自定义源
print("\n3. 自定义爬虫源测试")
print("-" * 80)

custom_sources = sources_config.get('custom', [])
print(f"共 {len(custom_sources)} 个自定义源\n")

for i, source in enumerate(custom_sources, 1):
    name = source.get('name', '未知')
    url = source.get('url', '')
    category = source.get('category', '')
    crawler = source.get('crawler_class', '')
    
    results['custom']['total'] += 1
    print(f"[{i:2d}] {name:30s} [{category:8s}] ... ", end='', flush=True)
    
    status, size, error = test_url(url)
    
    if status and status < 400:  # 2xx或3xx都算成功
        print(f"OK (HTTP {status}, 使用 {crawler})")
        results['custom']['ok'] += 1
        results['custom']['details'].append({
            'name': name,
            'status': 'OK',
            'method': crawler,
            'url': url
        })
    else:
        msg = error if error else f"HTTP {status}"
        print(f"FAIL ({msg})")
        results['custom']['fail'] += 1
        results['custom']['details'].append({
            'name': name,
            'status': 'FAIL',
            'error': msg
        })

# 汇总统计
print("\n" + "=" * 80)
print("测试结果汇总")
print("=" * 80)

total_tested = sum(r['total'] for r in results.values())
total_ok = sum(r['ok'] for r in results.values())
total_fail = sum(r['fail'] for r in results.values())

print(f"\n总计测试: {total_tested} 个")
print(f"  OK: {total_ok} 个 ({total_ok/total_tested*100:.1f}%)")
print(f"  FAIL: {total_fail} 个 ({total_fail/total_tested*100:.1f}%)")

print("\n按类型统计:")
for source_type, stats in results.items():
    if stats['total'] > 0:
        print(f"  {source_type:10s}: {stats['ok']}/{stats['total']} OK ({stats['ok']/stats['total']*100:.1f}%)")

# 可用的信息源
print("\n" + "=" * 80)
print("可用的信息源及推荐爬取方式")
print("=" * 80)

for source_type, stats in results.items():
    for detail in stats['details']:
        if detail['status'] == 'OK':
            method = detail.get('method', 'Unknown')
            print(f"OK {detail['name']:30s} -> {method}")

# 建议
print("\n" + "=" * 80)
print("建议")
print("=" * 80)

if not rsshub_available:
    print("\n1. RSSHub服务器不可用")
    print("   - 检查RSSHub服务是否启动")
    print("   - 检查配置中的RSSHub地址是否正确")
    print("   - 当前配置: " + rsshub_base)

if results['rss']['ok'] == 0 and results['rss']['total'] > 0:
    print("\n2. RSS源全部不可用")
    print("   - 检查RSS服务器是否启动")
    print("   - 检查网络连接")
    print("   - RSS服务器: http://101.42.187.241:8001")

if total_ok > 0:
    print(f"\n3. 有 {total_ok} 个信息源可用")
    print("   - 可以使用这些信息源进行测试")
    print("   - 建议先修复不可用的服务")

print("\n" + "=" * 80)
