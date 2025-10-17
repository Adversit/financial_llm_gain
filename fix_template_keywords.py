"""修复模板中的关键词显示"""

# 读取文件
with open('templates/report.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换关键词显示
old_pattern = '<span class="keyword">{{ keyword }}</span>'
new_pattern = '<span class="keyword">{{ keyword.word if keyword is mapping else keyword }}</span>'

content = content.replace(old_pattern, new_pattern)

# 写回文件
with open('templates/report.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 模板已修复")
print(f"替换次数: {content.count(new_pattern)}")
