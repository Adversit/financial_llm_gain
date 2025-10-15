"""
添加新的信息源到配置文件
"""
import yaml

# 读取当前配置
with open('config.yaml.backup', 'r', encoding='utf-8') as f:
    content = f.read()
    # 移除最后添加的错误内容
    if '# 新增源 - 待测试和开发' in content:
        content = content.split('# 新增源 - 待测试和开发')[0]
    
# 重新解析
config = yaml.safe_load(content)

# 添加新的RSS源
new_rss_sources = [
    {
        "name": "新华社英文",
        "category": "经济",
        "url": "http://www.xinhuanet.com/english/rss/index.htm",
        "enabled": False,
        "note": "RSS源待测试"
    },
    {
        "name": "国家统计局RSS",
        "category": "政治",
        "url": "https://www.stats.gov.cn/wzgl/rss/202305/t20230519_1939842.html",
        "enabled": False,
        "note": "RSS源待测试"
    },
]

# 添加新的RSSHub源
new_rsshub_sources = [
    {
        "name": "麦肯锡中国",
        "category": "经济",
        "route": "mckinsey/cn/:category",
        "enabled": False,
        "note": "RSSHub路由待测试"
    },
    {
        "name": "联合资信",
        "category": "经济",
        "route": "lhratings/research/:type",
        "enabled": False,
        "note": "RSSHub路由待测试"
    },
    {
        "name": "arXiv 计算金融",
        "category": "技术",
        "route": "papers/category/arxiv/cs.AI",
        "enabled": False,
        "note": "RSSHub路由待测试"
    },
    {
        "name": "GitHub 金融 AI",
        "category": "技术",
        "route": "github/notifications",
        "enabled": False,
        "note": "RSSHub路由待测试"
    },
    {
        "name": "Hugging Face 金融大模型",
        "category": "技术",
        "route": "huggingface/daily-papers/:cycle",
        "enabled": False,
        "note": "RSSHub路由待测试"
    },
    {
        "name": "掘金",
        "category": "技术",
        "route": "juejin/trending/:category/:type",
        "enabled": False,
        "note": "RSSHub路由待测试"
    },
    {
        "name": "TechCrunch",
        "category": "技术",
        "route": "techcrunch/news",
        "enabled": False,
        "note": "RSSHub路由待测试"
    },
    {
        "name": "The Wall Street Journal",
        "category": "经济",
        "route": "wsj/:lang/:category",
        "enabled": False,
        "note": "RSSHub路由待测试"
    },
    {
        "name": "Bloomberg Technology",
        "category": "技术",
        "route": "bloomberg/:site",
        "enabled": False,
        "note": "RSSHub路由待测试"
    },
    {
        "name": "Financial Times",
        "category": "经济",
        "route": "ft/myft/:key",
        "enabled": False,
        "note": "RSSHub路由待测试"
    },
]

# 添加新的自定义爬虫源
new_custom_sources = [
    {
        "name": "科学技术部",
        "category": "政治",
        "crawler_class": "MOSTCrawler",
        "url": "http://www.most.gov.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "国家金融监督管理总局",
        "category": "政治",
        "crawler_class": "NFRACrawler",
        "url": "https://www.nfra.gov.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "零壹财经",
        "category": "经济",
        "crawler_class": "ZeroOneCrawler",
        "url": "https://www.01caijing.com/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "万得资讯",
        "category": "金融科技",
        "crawler_class": "WindCrawler",
        "url": "https://www.wind.com.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "同花顺 iFinD",
        "category": "金融科技",
        "crawler_class": "IFindCrawler",
        "url": "https://www.51ifind.com/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "中国社会科学院金融研究所",
        "category": "政治",
        "crawler_class": "CASSCrawler",
        "url": "http://ifb.cass.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "清华大学五道口金融学院",
        "category": "经济",
        "crawler_class": "TsinghuaPBCCrawler",
        "url": "https://www.pbcsf.tsinghua.edu.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "波士顿咨询（BCG）中国",
        "category": "经济",
        "crawler_class": "BCGCrawler",
        "url": "https://www.bcg.com/cn",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "中诚信国际",
        "category": "经济",
        "crawler_class": "CCXICrawler",
        "url": "https://www.ccxi.com.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "证券时报",
        "category": "经济",
        "crawler_class": "STCNCrawler",
        "url": "http://www.stcn.com/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "经济参考报",
        "category": "经济",
        "crawler_class": "JJCKBCrawler",
        "url": "http://www.jjckb.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "SSRN 金融经济学",
        "category": "经济",
        "crawler_class": "SSRNCrawler",
        "url": "https://www.ssrn.com/index.cfm/en/fen/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "中国互联网金融协会",
        "category": "政治",
        "crawler_class": "NIFACrawler",
        "url": "http://www.nifa.org.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "世界人工智能大会",
        "category": "技术",
        "crawler_class": "WorldAICCrawler",
        "url": "https://www.worldaic.com.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "中国银行业协会",
        "category": "政治",
        "crawler_class": "ChinaCBACrawler",
        "url": "https://www.china-cba.net/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "中国证券业协会",
        "category": "政治",
        "crawler_class": "SACCrawler",
        "url": "https://www.sac.net.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "北京大学数字金融研究中心",
        "category": "经济",
        "crawler_class": "PKUIDFCrawler",
        "url": "https://idf.pku.edu.cn/",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "清华大学五道口金融学院金融科技实验室",
        "category": "技术",
        "crawler_class": "TsinghuaFintechLabCrawler",
        "url": "https://fintechlab.pbcsf.tsinghua.edu.cn/yjfb/qb.htm",
        "enabled": False,
        "note": "待开发自定义爬虫"
    },
    {
        "name": "新华财经专业终端",
        "category": "金融科技",
        "crawler_class": "XinhuaFinanceCrawler",
        "url": "https://www.ceis.cn/download/",
        "enabled": False,
        "note": "需要专业终端访问"
    },
]

# 添加到配置
config['sources']['rss'].extend(new_rss_sources)
config['sources']['rsshub'].extend(new_rsshub_sources)
config['sources']['custom'].extend(new_custom_sources)

# 保存配置
with open('config.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("✅ 成功添加新信息源到配置文件！")
print(f"\n新增统计:")
print(f"  RSS源: +{len(new_rss_sources)} 个")
print(f"  RSSHub源: +{len(new_rsshub_sources)} 个")
print(f"  自定义爬虫: +{len(new_custom_sources)} 个")
print(f"\n总计新增: {len(new_rss_sources) + len(new_rsshub_sources) + len(new_custom_sources)} 个信息源")
