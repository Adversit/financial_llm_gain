# 数据清洗逻辑说明

## 概述

数据清洗服务 (`app/services/cleaner_service.py`) 负责过滤和清洗爬取的文章数据，确保只保留相关且有效的内容。

## 清洗流程

### 完整流程 (`clean_all` 方法)

```
原始文章 (370篇)
    ↓
[步骤1] 去重 → 367篇 (-3篇)
    ↓
[步骤2] 日期过滤 → 20篇 (-347篇)
    ↓
[步骤3] 相关性过滤 → 17篇 (-3篇)
    ↓
最终文章 (17篇)
```

---

## 步骤详解

### 步骤 1: 去重 (`remove_duplicates`)

**目的**: 移除重复的文章

**判断标准**:
- 链接 (URL) 完全相同
- 或标题完全相同

**处理逻辑**:
```python
# 标准化处理
link = article.link.strip().lower()
title = article.title.strip().lower()

# 检查是否已存在
if link in seen_links or title in seen_titles:
    移除文章
```

**示例**:
- 原始: 370 篇
- 去重后: 367 篇
- 移除: 3 篇重复文章

---

### 步骤 2: 日期过滤 (`filter_by_date`)

**目的**: 只保留指定日期（默认昨天）的文章

**判断标准**:
```python
if article.publish_time is None:
    保留文章  # 假设是最新的
elif article.publish_time.date() == target_date:
    保留文章
else:
    移除文章
```

**特殊处理**:
- 如果文章**没有发布时间**，会保留该文章（假设是最新的）
- 这是为了避免因爬虫问题导致文章被错误过滤

**示例**:
- 输入: 367 篇
- 目标日期: 2025-10-11
- 输出: 20 篇
- 移除: 347 篇（不是昨天的文章）

**为什么移除这么多？**
- RSS 源通常包含最近几天甚至几周的文章
- 新华社的 RSS 包含 300 条记录，但大部分是 2022 年的旧文章
- 只有少数文章的发布日期是昨天

---

### 步骤 3: 相关性过滤 (`filter_by_relevance`)

**目的**: 过滤与金融无关的内容

**判断标准**:
文章必须包含**至少 2 个**金融关键词

**金融关键词列表** (共 48 个):
```python
FINANCE_KEYWORDS = [
    # 金融核心词
    '金融', '经济', '投资', '股票', '证券', '基金', '银行', '保险',
    '财经', '市场', '交易', '资本', '融资', '上市', '债券', '期货',
    
    # 宏观经济
    '货币', '汇率', '利率', '通货', '财政', '税收', '贸易', '产业',
    
    # 企业商业
    '企业', '公司', '商业', '消费', '价格', '成本', '利润', '营收',
    
    # 科技金融
    '科技', '技术', '创新', '数字', '互联网', '人工智能', 'AI',
    '区块链', '大数据', '云计算', '金融科技', 'fintech', '支付',
    
    # 政策监管
    '监管', '政策', '法规', '改革', '发展', '增长', '指数', 'GDP'
]
```

**检查逻辑**:
```python
text = f"{article.title} {article.content}".lower()

keyword_count = sum(
    1 for keyword in FINANCE_KEYWORDS
    if keyword.lower() in text
)

if keyword_count >= 2:
    保留文章
else:
    移除文章
```

**示例**:
- 输入: 20 篇
- 输出: 17 篇
- 移除: 3 篇（关键词不足 2 个）

**被过滤的文章示例**:
- 只包含 1 个关键词的文章
- 完全不相关的新闻（娱乐、体育等）

---

## 配置选项

### 1. 关闭相关性过滤

如果觉得相关性过滤太严格，可以关闭：

```python
# 在 crawler_service.py 中
grouped_articles = crawler_service.fetch_all_sources(
    target_date=target_date,
    filter_relevance=False  # 关闭相关性过滤
)
```

### 2. 调整关键词数量要求

修改 `cleaner_service.py` 中的判断条件：

```python
# 原来: 至少 2 个关键词
return keyword_count >= 2

# 改为: 至少 1 个关键词（更宽松）
return keyword_count >= 1

# 改为: 至少 3 个关键词（更严格）
return keyword_count >= 3
```

### 3. 扩展关键词列表

在 `FINANCE_KEYWORDS` 中添加更多关键词：

```python
FINANCE_KEYWORDS = [
    # ... 现有关键词 ...
    
    # 添加新关键词
    '风投', 'VC', 'PE', '并购', 'IPO',
    '估值', '融资', '创业', '独角兽',
    # ...
]
```

### 4. 使用日期范围

如果想保留多天的文章：

```python
# 使用日期范围过滤
articles = cleaner.filter_by_date_range(
    articles,
    start_date=date(2025, 10, 10),  # 开始日期
    end_date=date(2025, 10, 11)     # 结束日期
)
```

---

## 实际案例分析

### 案例: 2025-10-11 的爬取

```
原始数据:
- 人民日报: 91 篇
- 新华社: 127 篇
- 36氪: 29 篇
- 虎嗅: 20 篇
- 其他: 103 篇
总计: 370 篇

清洗过程:
1. 去重: 370 → 367 篇
   - 移除 3 篇重复文章

2. 日期过滤: 367 → 20 篇
   - 只保留 2025-10-11 的文章
   - 大部分 RSS 文章是旧文章（2022年）
   
3. 相关性过滤: 20 → 17 篇
   - 移除 3 篇关键词不足的文章

最终结果:
- 政治: 1 篇
- 经济: 9 篇
- 技术: 0 篇
- 金融科技: 7 篇
总计: 17 篇
```

---

## 常见问题

### Q1: 为什么文章数量这么少？

**A**: 主要原因是日期过滤：
- RSS 源包含历史文章，但我们只要昨天的
- 新华社的 300 条记录大部分是 2022 年的旧文章
- 只有少数信息源每天更新

**解决方案**:
1. 添加更多每日更新的信息源
2. 扩展日期范围（保留最近 3 天）
3. 关闭日期过滤（保留所有文章）

### Q2: 相关性过滤是否太严格？

**A**: 当前要求至少 2 个关键词，这是一个平衡：
- 太宽松（1个）: 会包含很多不相关文章
- 太严格（3个）: 会过滤掉一些相关文章
- 当前（2个）: 适中

**调整建议**:
- 如果文章太少，改为 1 个关键词
- 如果不相关文章太多，改为 3 个关键词

### Q3: 如何保留没有日期的文章？

**A**: 当前逻辑已经保留了没有日期的文章：

```python
if article.publish_time is None:
    filtered.append(article)  # 保留
```

但在报告生成时，查询使用了严格的日期范围，所以这些文章不会出现在报告中。

**解决方案**: 修改报告生成的查询逻辑，包含最近保存的无日期文章。

---

## 优化建议

### 1. 智能日期处理

对于没有发布时间的文章，使用保存时间作为发布时间：

```python
if article.publish_time is None:
    article.publish_time = article.saved_at
```

### 2. 使用 AI 判断相关性

替代关键词匹配，使用 AI 判断文章是否与金融相关：

```python
def _is_finance_related_ai(self, article: Article) -> bool:
    prompt = f"判断以下文章是否与金融相关：{article.title}"
    result = ai_service.classify(prompt)
    return result == "相关"
```

### 3. 可配置的过滤规则

将过滤规则放到配置文件中：

```yaml
# config.yaml
data_cleaning:
  enable_deduplication: true
  enable_date_filter: true
  enable_relevance_filter: true
  min_keywords: 2
  date_range_days: 1
```

---

## 总结

数据清洗的核心目标是：
1. ✅ 去除重复内容
2. ✅ 只保留最新（昨天）的文章
3. ✅ 过滤不相关的内容

当前配置适合每日报告的需求，如果需要更多文章，可以：
- 添加更多信息源
- 放宽相关性要求
- 扩展日期范围
