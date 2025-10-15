# -*- coding: utf-8 -*-
"""解析datafrom文件并生成config.yaml配置"""
import re
from pathlib import Path

# 读取datafrom文件
with open('datafrom', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 分类映射
category_map = {
    '移动支付网': '金融科技',
    '金融监管研究': '政治',
    '消金界': '金融科技',
    'AIGC开放社区': '技术',
    '脑极体': '技术',
    '赛博禅心': '技术',
    'APPSO': '技术',
    '硅星人PRO': '技术',
    '光子星球': '技术',
    '智东西': '技术',
    'DeepTech深科技': '技术',
    '数据猿': '技术',
    '深度学习与NLP': '技术',
    'BigQuant': '金融科技',
    '新智元': '技术',
    '量子位': '技术',
    '中国人工智能学会': '技术',
    '甲子光年': '经济',
    'Z Finance': '金融科技',
    '人工智能量化实验室': '金融科技',
    '机器之心': '技术',
    'AI科技评论': '技术',
    'AI前线': '技术',
    '中国金融杂志': '经济',
    '国家金融与发展实验': '经济',
}

# 政府机构默认为政治类
gov_keywords = ['部', '委', '局', '办公室', '银行', '监督', '管理', '协会']

# 解析RSS源（公众号）
rss_sources = []
rsshub_sources = []
custom_sources = []

for line in lines:
    line = line.strip()
    if not line or line == '公众号：':
        continue
    
    # 解析公众号RSS
    if '101.42.187.241:8001/feed/' in line:
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0]
            url = 'http://' + parts[1]
            
            # 确定分类
            category = category_map.get(name, '技术')  # 默认技术类
            
            rss_sources.append({
                'name': name,
                'category': category,
                'url': url
            })
    
    # 解析RSSHub源
    elif 'rsshub.app' in line or 'https://rsshub.app' in line:
        # 提取名称和路由
        match = re.search(r'(.+?)\s+https?://[^\s]+\s+.*?(https://rsshub\.app/[^\s]+)', line)
        if match:
            name = match.group(1).strip()
            rsshub_route = match.group(2).replace('https://rsshub.app/', '')
            
            # 移除括号内的英文名
            name = re.sub(r'\s*\([^)]+\)', '', name)
            
            # 确定分类
            if any(kw in name for kw in gov_keywords):
                category = '政治'
            elif any(kw in name for kw in ['金融', '银行', '证券', '基金']):
                category = '经济'
            elif any(kw in name for kw in ['科技', '技术', 'AI', '人工智能', '数据']):
                category = '技术'
            elif any(kw in name for kw in ['财经', '咨询', '研究']):
                category = '经济'
            else:
                category = '经济'
            
            rsshub_sources.append({
                'name': name,
                'category': category,
                'route': rsshub_route
            })

print(f"解析完成:")
print(f"  RSS源: {len(rss_sources)} 个")
print(f"  RSSHub源: {len(rsshub_sources)} 个")

# 生成YAML配置
yaml_content = """# 金融日报系统配置文件 - 更新版本

# 应用配置
app:
  name: "金融日报系统"
  version: "2.0.0"
  debug: false

# 数据库配置
database:
  url: "sqlite:///./data/financial_daily.db"

# RSSHub配置
rsshub:
  base_url: "http://101.42.187.241:1200"

# AI模型配置
ai:
  provider: "deepseek"
  api_key: "${AI_API_KEY}"
  base_url: "${AI_BASE_URL}"
  model: "${AI_MODEL}"
  prompts:
    article_summary: "prompts/article_summary.txt"
    daily_report: "prompts/daily_report.txt"
  temperature: 0.7
  max_tokens: 2000
  timeout: 120
  max_retries: 3

# 邮件配置
email:
  smtp_server: "${SMTP_SERVER}"
  smtp_port: 465
  use_ssl: true
  username: "${SMTP_USERNAME}"
  password: "${SMTP_PASSWORD}"
  from_name: "金融日报系统"

# 任务调度配置
scheduler:
  daily_report_time: "08:00"
  timezone: "Asia/Shanghai"

# 报告配置
report:
  generate_pdf: true
  show_pdf_in_frontend: false
  attach_pdf_in_email: false

# 日志配置
logging:
  level: "INFO"
  file: "logs/app.log"
  max_bytes: 10485760
  backup_count: 5

# Firecrawl配置
firecrawl:
  api_key: "${FIRECRAWL_API_KEY}"
  api_url: "${FIRECRAWL_API_URL}"
  enabled: true
  timeout: 60

# 信息源配置
sources:
  # RSS源（公众号）
  rss:
"""

# 添加RSS源
for source in rss_sources[:30]:  # 限制数量避免过多
    yaml_content += f"""    - name: "{source['name']}"
      category: "{source['category']}"
      url: "{source['url']}"
      enabled: true
    
"""

yaml_content += """  # RSSHub源
  rsshub:
"""

# 添加RSSHub源
for source in rsshub_sources[:20]:  # 限制数量
    yaml_content += f"""    - name: "{source['name']}"
      category: "{source['category']}"
      route: "{source['route']}"
      enabled: true
    
"""

yaml_content += """  # 自定义爬虫源（保留现有的）
  custom:
    - name: "工业和信息化部"
      category: "政治"
      crawler_class: "MIITCrawler"
      url: "https://www.miit.gov.cn/"
      enabled: true
    
    - name: "中国证券监督管理委员会"
      category: "政治"
      crawler_class: "CSRCCrawler"
      url: "http://www.csrc.gov.cn/"
      enabled: true
    
    - name: "第一财经"
      category: "经济"
      crawler_class: "YicaiCrawler"
      url: "https://www.yicai.com/"
      enabled: true
"""

# 保存配置
with open('config_new.yaml', 'w', encoding='utf-8') as f:
    f.write(yaml_content)

print("\n新配置已生成: config_new.yaml")
print("\n请检查配置后，使用以下命令替换:")
print("  cp config_new.yaml config.yaml")
