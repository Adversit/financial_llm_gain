#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 读取文件
with open('app/services/email_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换颜色配置
old_config = """        category_config = {
            '政治': {'color': '#e91e63', 'icon': '🏛️', 'css_class': 'political'},  # 粉红色
            '经济': {'color': '#2196f3', 'icon': '💰',  'css_class': 'economic'},  # 蓝色
            '技术': {'color': '#4caf50', 'icon': '🔬', 'css_class': 'technical'},  # 绿色
            '金融科技': {'color': '#ff9800', 'icon': '💳', 'css_class': 'fintech'}  # 橙色
        }"""

new_config = """        category_config = {
            '政治': {'color': '#f5576c', 'icon': '🏛️', 'css_class': 'political'},
            '经济': {'color': '#4facfe', 'icon': '💰', 'css_class': 'economic'},
            '技术': {'color': '#43e97b', 'icon': '🔬', 'css_class': 'technical'},
            '金融科技': {'color': '#fec163', 'icon': '💳', 'css_class': 'fintech'}
        }"""

# 尝试多种匹配方式
if old_config in content:
    content = content.replace(old_config, new_config)
    print("方式1: 成功替换")
else:
    # 尝试只替换颜色值
    content = content.replace("'#e91e63'", "'#f5576c'")
    content = content.replace("'#2196f3'", "'#4facfe'")
    content = content.replace("'#4caf50'", "'#43e97b'")
    content = content.replace("'#ff9800'", "'#fec163'")
    print("方式2: 逐个替换颜色值")

# 写回文件
with open('app/services/email_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("颜色配置已更新！")
