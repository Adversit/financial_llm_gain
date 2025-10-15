# Firecrawl集成完成

## 概述

已成功将Firecrawl添加为爬虫策略链的最后一个备选方案。

## 完整的策略优先级链

```
1. RSS          → 最快最稳定
2. RSSHub       → 统一格式
3. HTTP Request → 静态页面
4. Selenium     → 动态页面
5. Custom       → 特殊格式
6. Firecrawl    → 最后备选（新增）✨
```

## Firecrawl策略特点

### 优势
- ✅ 可以处理复杂的JavaScript渲染
- ✅ 绕过大部分反爬机制
- ✅ 自动提取主要内容
- ✅ 支持转换为Markdown格式
- ✅ 云端处理，无需本地资源
- ✅ 作为最后的备选方案，提高成功率

### 适用场景
- 其他策略都失败的网站
- 有强反爬机制的网站
- 复杂的JavaScript渲染页面
- 需要高成功率的场景

### 限制
- ⚠️ 需要API密钥（付费服务）
- ⚠️ 响应时间较长（10-30秒）
- ⚠️ 有API调用限制
- ⚠️ 优先级最低（仅在其他策略失败时使用）

## 新增文件

### 策略实现
- `app/crawlers/strategies/firecrawl_strategy.py` - Firecrawl策略实现
  - `FirecrawlStrategy` - 基础Firecrawl策略
  - `FirecrawlListStrategy` - 列表页策略

### 示例代码
- `app/crawlers/custom/example_firecrawl_crawler.py` - 使用示例
  - `ExampleFirecrawlParser` - 基础解析器
  - `ExampleFirecrawlCrawler` - 单一策略爬虫
  - `MultiStrategyWithFirecrawlCrawler` - 多策略爬虫

### 测试脚本
- `test_firecrawl_strategy.py` - 完整的测试脚本

### 文档更新
- `CRAWLER_ARCHITECTURE.md` - 添加Firecrawl策略说明
- `requirements.txt` - 添加Firecrawl说明
- `FIRECRAWL_INTEGRATION.md` - 本文档

## 使用方法

### 1. 获取API密钥

访问 https://firecrawl.dev 注册并获取API密钥。

### 2. 配置API密钥（推荐方式）

**在.env文件中配置（推荐）：**
```bash
# .env文件
FIRECRAWL_API_KEY=your_api_key_here
FIRECRAWL_API_URL=https://api.firecrawl.dev/v0
```

配置后，所有Firecrawl策略会自动读取，无需手动传入。

**其他方式：**

如果需要在代码中手动指定：
```python
strategy = FirecrawlStrategy(
    source_name="网站名称",
    source_url="https://example.com",
    api_key="your_api_key_here"  # 可选，不传则从配置读取
)
```

### 3. 使用Firecrawl策略

**单独使用（API密钥自动从配置读取）：**
```python
from app.crawlers.strategies import FirecrawlStrategy

# API密钥会自动从.env中的FIRECRAWL_API_KEY读取
strategy = FirecrawlStrategy(
    source_name="难爬的网站",
    source_url="https://example.com"
)

articles = strategy.fetch()
```

**作为备选方案（推荐）：**
```python
from app.crawlers.strategies import (
    StrategyManager,
    RSSStrategy,
    HTTPStrategy,
    FirecrawlStrategy
)

manager = StrategyManager()

# 添加多个策略
manager.add_strategy(RSSStrategy(...))      # 优先尝试
manager.add_strategy(HTTPStrategy(...))     # 次优先
manager.add_strategy(FirecrawlStrategy(     # 最后备选
    source_name="网站名称",
    source_url="https://example.com"
    # api_key自动从配置读取
))

# 自动选择最佳策略，失败则回退
articles = manager.fetch_with_fallback()
```

### 4. 自定义解析逻辑

```python
from app.crawlers.strategies import FirecrawlStrategy

class MyFirecrawlParser(FirecrawlStrategy):
    def parse_firecrawl_data(self, data: dict) -> List[Article]:
        """自定义解析逻辑"""
        articles = []
        
        # 获取Markdown内容
        content = data.get('markdown', '')
        title = data.get('metadata', {}).get('title', '')
        
        # 自定义处理...
        
        return articles
```

## 工作流程

### 自动回退机制

```
用户请求
    ↓
尝试 RSS策略
    ↓ (失败)
尝试 RSSHub策略
    ↓ (失败)
尝试 HTTP策略
    ↓ (失败)
尝试 Selenium策略
    ↓ (失败)
尝试 Custom策略
    ↓ (失败)
尝试 Firecrawl策略 ← 最后的备选
    ↓ (成功)
返回文章列表 ✓
```

### Firecrawl API调用流程

```
1. 发送爬取请求到Firecrawl API
2. Firecrawl云端处理：
   - 渲染JavaScript
   - 绕过反爬机制
   - 提取主要内容
   - 转换为Markdown
3. 返回结构化数据
4. 本地解析数据
5. 返回文章列表
```

## 配置示例

### config.yaml（可选）

```yaml
# Firecrawl配置（可选）
firecrawl:
  api_key: "${FIRECRAWL_API_KEY}"
  api_url: "https://api.firecrawl.dev/v0"
  timeout: 60
  enabled: true
```

### 在自定义爬虫中使用

```python
class MyCrawler(BaseCrawler):
    def fetch(self) -> List[Article]:
        from app.config import get_config
        
        config = get_config()
        firecrawl_key = config.get('firecrawl', {}).get('api_key')
        
        manager = StrategyManager()
        
        # 添加其他策略...
        
        # 如果配置了Firecrawl，添加为备选
        if firecrawl_key:
            manager.add_strategy(FirecrawlStrategy(
                source_name=self.source_name,
                source_url=self.source_url,
                api_key=firecrawl_key
            ))
        
        return manager.fetch_with_fallback()
```

## 测试

### 运行测试脚本

```bash
python test_firecrawl_strategy.py
```

### 测试结果

```
✓ Firecrawl策略已添加
✓ 优先级设置正确（6 - 最低）
✓ 策略管理器支持Firecrawl
✓ 示例代码已创建
✓ 文档已更新
```

## 成本考虑

### Firecrawl定价（参考）

- **免费层**：有限的API调用次数
- **付费层**：按调用次数计费

### 优化建议

1. **只在必要时使用**
   - 设置为最低优先级
   - 只在其他策略失败时调用

2. **缓存结果**
   - 避免重复爬取相同URL
   - 设置合理的缓存时间

3. **监控使用量**
   - 记录API调用次数
   - 设置使用限制
   - 定期检查账单

4. **批量处理**
   - 如果需要爬取多个页面，使用批量API
   - 减少单次调用成本

## 常见问题

### Q: 必须使用Firecrawl吗？
**A:** 不是。Firecrawl是可选的，只在其他策略都失败时使用。

### Q: 没有API密钥会怎样？
**A:** 系统会自动跳过Firecrawl策略，不影响其他策略的使用。

### Q: Firecrawl比Selenium好在哪里？
**A:** 
- Firecrawl是云端服务，无需本地资源
- 更好的反爬绕过能力
- 自动提取主要内容
- 但Selenium是免费的，Firecrawl需要付费

### Q: 什么时候应该使用Firecrawl？
**A:** 
- 网站有强反爬机制
- Selenium也无法爬取
- 需要高成功率
- 预算允许

### Q: 如何控制成本？
**A:** 
- 设置为最低优先级
- 只在其他策略失败时使用
- 实现缓存机制
- 监控API使用量

## 总结

✅ **Firecrawl已成功集成**

- 作为第6个策略（最低优先级）
- 提供强大的备选方案
- 提高整体爬取成功率
- 完全可选，不影响现有功能

✅ **完整的策略链**

```
RSS → RSSHub → HTTP → Selenium → Custom → Firecrawl
```

✅ **灵活的使用方式**

- 可以单独使用
- 可以作为备选方案
- 可以自定义解析逻辑
- 可以随时启用/禁用

🎉 **现在系统拥有最完整的爬取策略链，可以应对各种复杂的网站！**
