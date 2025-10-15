# -*- coding: utf-8 -*-
"""示例测试文件"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("示例测试")
print("=" * 60)

# 测试1: 导入测试
print("\n测试1: 导入模块")
print("-" * 60)

try:
    from app.config import get_config
    print("✓ 配置模块导入成功")
    
    config = get_config()
    print(f"✓ 配置加载成功")
    print(f"  - 应用名称: {config['app']['name']}")
    
except Exception as e:
    print(f"✗ 导入失败: {e}")

# 测试2: 策略导入
print("\n测试2: 策略模块导入")
print("-" * 60)

try:
    from app.crawlers.strategies import (
        RSSStrategy,
        RSSHubStrategy,
        HTTPStrategy,
        SeleniumStrategy,
        CustomStrategy,
        FirecrawlStrategy
    )
    print("✓ 所有策略模块导入成功")
    print(f"  - RSS优先级: {RSSStrategy.PRIORITY_RSS}")
    print(f"  - Firecrawl优先级: {FirecrawlStrategy.PRIORITY_FIRECRAWL}")
    
except Exception as e:
    print(f"✗ 策略导入失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
