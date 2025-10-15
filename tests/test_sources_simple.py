# -*- coding: utf-8 -*-
"""简化版信息源测试"""
import sys
import io
from pathlib import Path
import requests
from datetime import datetime

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_config

print("=" * 80)
print("信息源可用性测试")
print("=" * 80)

config = get_config()
sources_config = config.get('sources', {})

total = 0
available = 0

# 测试RSS源
print("\n1. RSS源测试")
print("-" * 80)

rss_sources = sources_config.get('rss', [])
print(f"共 {len(rss_sources)} 个RSS源\n")

for i, source in enumerate(rss_sources, 1):
    name = source.get('name', '未知')
    url = source.get('url', '')
    
    total += 1
    print(f"[{i:2d}] {name:20s} ... ", end='', flush=True)
    
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            print("OK")
            available += 1
        else:
            print(f"FAIL (HTTP {response.status_code})")
    except Exception as e:
        print(f"FAIL ({str(e)[:30]})")

# 测试RSSHub源
print("\n2. RSSHub源测试")
print("-" * 80)

rsshub_sources = sources_config.get('rsshub', [])
rsshub_base = config.get('rsshub', {}).get('base_url', '')
print(f"共 {len(rsshub_sources)} 个RSSHub源")
print(f"服务器: {rsshub_base}\n")

for i, source in enumerate(rsshub_sources, 1):
    name = source.get('name', '未知')
    route = source.get('route', '')
    url = f"{rsshub_base}/{route}"
    
    total += 1
    print(f"[{i:2d}] {name:30s} ... ", end='', flush=True)
    
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            print("OK")
            available += 1
        else:
            print(f"FAIL (HTTP {response.status_code})")
    except Exception as e:
        print(f"FAIL ({str(e)[:30]})")

# 测试自定义源
print("\n3. 自定义爬虫源测试")
print("-" * 80)

custom_sources = sources_config.get('custom', [])
print(f"共 {len(custom_sources)} 个自定义源\n")

for i, source in enumerate(custom_sources, 1):
    name = source.get('name', '未知')
    url = source.get('url', '')
    crawler = source.get('crawler_class', '')
    
    total += 1
    print(f"[{i:2d}] {name:30s} ... ", end='', flush=True)
    
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            print(f"OK (使用 {crawler})")
            available += 1
        else:
            print(f"FAIL (HTTP {response.status_code})")
    except Exception as e:
        print(f"FAIL ({str(e)[:30]})")

# 汇总
print("\n" + "=" * 80)
print("测试结果")
print("=" * 80)
print(f"总计: {total} 个")
print(f"可用: {available} 个 ({available/total*100:.1f}%)")
print(f"不可用: {total-available} 个 ({(total-available)/total*100:.1f}%)")

if available >= total * 0.7:
    print("\n状态: 良好")
elif available >= total * 0.5:
    print("\n状态: 一般")
else:
    print("\n状态: 需要检查")
