"""
检查缺失的信息源
"""
import yaml

# 你提供的信息源列表
provided_sources = [
    "工业和信息化部",
    "科学技术部",
    "新华社",
    "中国人民银行",
    "国家金融监督管理总局",
    "国家互联网信息办公室",
    "中央金融委员会办公室",
    "中国证券监督管理委员会",
    "国家发展和改革委员会",
    "外交部国际经济司",
    "全国人民代表大会财政经济委员会",
    "国家外汇管理局",
    "新华财经专业终端",
    "中国人民银行金融基础数据中心",
    "国际货币基金组织中国执董办公室",
    "艾瑞咨询",
    "头豹研究院",
    "36氪",
    "财新网",
    "零壹财经",
    "虎嗅",
    "第一财经",
    "国家统计局",
    "万得资讯",
    "同花顺 iFinD",
    "东方财富网",
    "彭博中国",
    "路透中文网",
    "中国社会科学院金融研究所",
    "清华大学五道口金融学院",
    "麦肯锡中国",
    "波士顿咨询（BCG）中国",
    "中诚信国际",
    "联合资信",
    "arXiv 计算金融",
    "GitHub 金融 AI",
    "Hugging Face 金融大模型",
    "掘金",
    "证券时报",
    "经济参考报",
    "SSRN 金融经济学",
    "TechCrunch",
    "The Wall Street Journal",
    "Bloomberg",
    "Financial Times",
    "中国互联网金融协会",
    "未央网",
    "世界人工智能大会",
    "中国银行业协会",
    "中国证券业协会",
    "北京大学数字金融研究中心",
    "清华大学五道口金融学院金融科技实验室",
]

# 读取当前配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 获取已配置的源
configured_sources = []
for source in config['sources']['rss']:
    configured_sources.append(source['name'])
for source in config['sources']['rsshub']:
    configured_sources.append(source['name'])
for source in config['sources']['custom']:
    configured_sources.append(source['name'])

# 去重
configured_sources = list(set(configured_sources))

# 找出缺失的源
missing_sources = []
for source in provided_sources:
    # 模糊匹配
    found = False
    for configured in configured_sources:
        if source in configured or configured in source:
            found = True
            break
    if not found:
        missing_sources.append(source)

print("="*80)
print("缺失的信息源")
print("="*80)
print(f"\n总计: {len(missing_sources)} 个\n")

for i, source in enumerate(missing_sources, 1):
    print(f"{i}. {source}")

print("\n" + "="*80)
print("已配置的信息源")
print("="*80)
print(f"\n总计: {len(configured_sources)} 个\n")

for source in sorted(configured_sources):
    print(f"  - {source}")
