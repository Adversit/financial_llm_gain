## 爬虫架构重构文档

### 概述

新的爬虫架构采用**策略模式**，将不同的爬取方式拆分成独立的策略类，便于扩展和维护。

### 策略优先级

系统会按照以下优先级自动选择最佳的爬取策略：

1. **RSS** (优先级: 1) - 如果有RSS源，优先使用
2. **RSSHub** (优先级: 2) - 如果配置了RSSHub，次优先
3. **HTTP Request** (优先级: 3) - 普通HTTP请求+HTML解析
4. **Selenium** (优先级: 4) - 需要JavaScript渲染的页面
5. **Custom Parser** (优先级: 5) - 特殊页面的自定义解析逻辑
6. **Firecrawl** (优先级: 6) - 使用Firecrawl API（最后的备选方案）

### 目录结构

```
app/crawlers/
├── base.py                          # 基础爬虫类
├── factory.py                       # 爬虫工厂（兼容旧代码）
├── rss_crawler.py                   # RSS爬虫（兼容旧代码）
├── rsshub_crawler.py                # RSSHub爬虫（兼容旧代码）
├── strategies/                      # 新的策略模块
│   ├── __init__.py
│   ├── base_strategy.py             # 策略基类
│   ├── rss_strategy.py              # RSS策略
│   ├── rsshub_strategy.py           # RSSHub策略
│   ├── http_strategy.py             # HTTP请求策略
│   ├── selenium_strategy.py         # Selenium策略
│   ├── custom_strategy.py           # 自定义策略
│   └── strategy_manager.py          # 策略管理器
└── custom/                          # 自定义爬虫
    ├── example_http_crawler.py      # HTTP策略示例
    ├── example_selenium_crawler.py  # Selenium策略示例
    ├── miit_crawler.py              # 工信部爬虫
    ├── csrc_crawler.py              # 证监会爬虫
    └── ...
```

---

## 策略详解

### 1. RSS策略 (RSSStrategy)

**适用场景：** 网站提供RSS/Atom订阅源

**优点：**
- 速度快，稳定性高
- 数据结构标准化
- 不易被反爬

**使用方法：**
```python
from app.crawlers.strategies import RSSStrategy

strategy = RSSStrategy(
    source_name="人民日报",
    feed_url="http://www.people.com.cn/rss/finance.xml"
)

articles = strategy.fetch()
```

---

### 2. RSSHub策略 (RSSHubStrategy)

**适用场景：** 使用RSSHub服务生成RSS源

**优点：**
- 支持大量网站
- 统一的RSS格式
- 社区维护

**使用方法：**
```python
from app.crawlers.strategies import RSSHubStrategy

strategy = RSSHubStrategy(
    source_name="36氪",
    rsshub_base="http://101.42.187.241:1200",
    route="36kr/news/latest"
)

articles = strategy.fetch()
```

---

### 3. HTTP策略 (HTTPStrategy)

**适用场景：** 静态HTML页面，不需要JavaScript渲染

**优点：**
- 速度快
- 资源占用少
- 易于调试

**使用方法：**

**步骤1：创建解析器类**
```python
from app.crawlers.strategies import HTTPStrategy
from bs4 import BeautifulSoup

class MyHTTPParser(HTTPStrategy):
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        articles = []
        
        # 根据网站结构编写解析逻辑
        for item in soup.select('.article-item'):
            title = self.extract_text(item.select_one('.title'))
            link = self.extract_link(item.select_one('a'), self.source_url)
            content = self.extract_text(item.select_one('.content'))
            
            if title and link and self.validate_content(content):
                articles.append(Article(
                    title=title,
                    link=link,
                    content=content,
                    source_name=self.source_name
                ))
        
        return articles
```

**步骤2：使用解析器**
```python
parser = MyHTTPParser(
    source_name="示例网站",
    source_url="https://example.com/news"
)

articles = parser.fetch()
```

---

### 4. Selenium策略 (SeleniumStrategy)

**适用场景：** 需要JavaScript渲染的动态页面

**优点：**
- 可以处理JavaScript渲染的内容
- 支持滚动加载、点击操作
- 模拟真实浏览器行为

**缺点：**
- 速度较慢
- 资源占用大
- 需要安装Chrome/ChromeDriver

**安装依赖：**
```bash
pip install selenium
# 下载ChromeDriver: https://chromedriver.chromium.org/
```

**使用方法：**

**步骤1：创建解析器类**
```python
from app.crawlers.strategies import SeleniumStrategy
from bs4 import BeautifulSoup

class MySeleniumParser(SeleniumStrategy):
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        articles = []
        
        # 解析逻辑与HTTP策略类似
        for item in soup.select('.article-item'):
            # ... 解析代码
            pass
        
        return articles
    
    def fetch(self) -> List[Article]:
        """可以重写fetch方法添加特殊操作"""
        articles = []
        
        try:
            self._init_driver()
            self.driver.get(self.source_url)
            
            # 特殊操作：滚动到底部
            self.scroll_to_bottom(pause_time=2.0)
            
            # 特殊操作：点击"加载更多"
            self.click_load_more('.load-more-btn', max_clicks=3)
            
            # 特殊操作：等待元素加载
            from selenium.webdriver.common.by import By
            self.wait_for_element(By.CLASS_NAME, 'article-list')
            
            # 获取页面并解析
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            articles = self.parse_page(soup)
            
            self.log_success(len(articles))
            
        finally:
            self._close_driver()
        
        return articles
```

**步骤2：使用解析器**
```python
parser = MySeleniumParser(
    source_name="动态网站",
    source_url="https://example.com/news",
    headless=True,  # 无头模式
    wait_time=5  # 等待JavaScript执行
)

articles = parser.fetch()
```

---

### 5. 自定义策略 (CustomStrategy)

**适用场景：** 特殊格式的数据源（如API、特殊协议等）

**使用方法：**
```python
from app.crawlers.strategies import CustomStrategy

class MyCustomParser(CustomStrategy):
    def fetch(self) -> List[Article]:
        articles = []
        
        # 自定义的爬取逻辑
        # 例如：调用API、解析特殊格式等
        
        return articles
```

---

### 6. Firecrawl策略 (FirecrawlStrategy)

**适用场景：** 难以用常规方法爬取的网站（作为最后的备选方案）

**优点：**
- 可以处理复杂的JavaScript渲染
- 绕过大部分反爬机制
- 自动提取主要内容
- 支持转换为Markdown格式
- 云端处理，无需本地资源

**缺点：**
- 需要API密钥（付费服务）
- 响应时间较长
- 有API调用限制

**安装：**
Firecrawl是API服务，无需安装额外依赖，但需要：
1. 注册账号：https://firecrawl.dev
2. 获取API密钥
3. 配置到环境变量或代码中

**使用方法：**

**步骤1：配置API密钥**
```bash
# 在.env文件中添加
FIRECRAWL_API_KEY=your_api_key_here
```

**步骤2：创建解析器类**
```python
from app.crawlers.strategies import FirecrawlStrategy

class MyFirecrawlParser(FirecrawlStrategy):
    def parse_firecrawl_data(self, data: dict) -> List[Article]:
        """解析Firecrawl返回的数据"""
        articles = []
        
        # 获取Markdown内容
        content = data.get('markdown', '')
        title = data.get('metadata', {}).get('title', '')
        
        if title and content and self.validate_content(content):
            articles.append(Article(
                title=title,
                link=self.source_url,
                content=content,
                source_name=self.source_name
            ))
        
        return articles
```

**步骤3：使用解析器**
```python
parser = MyFirecrawlParser(
    source_name="难爬的网站",
    source_url="https://example.com",
    api_key="your_api_key"
)

articles = parser.fetch()
```

**高级用法：作为备选方案**
```python
from app.crawlers.strategies import StrategyManager

manager = StrategyManager()

# 添加多个策略
manager.add_strategy(RSSStrategy(...))      # 优先级1
manager.add_strategy(HTTPStrategy(...))     # 优先级3
manager.add_strategy(SeleniumStrategy(...)) # 优先级4
manager.add_strategy(FirecrawlStrategy(...))# 优先级6（最后）

# 自动选择，如果前面的都失败，会使用Firecrawl
articles = manager.fetch_with_fallback()
```

**Firecrawl API特性：**
- 自动处理JavaScript
- 提取主要内容（去除广告、导航等）
- 支持多种格式（HTML、Markdown、结构化数据）
- 自动处理反爬机制
- 支持批量爬取

**注意事项：**
- Firecrawl是付费服务，有API调用限制
- 建议只在其他策略都失败时使用
- 响应时间通常在10-30秒
- 需要稳定的网络连接

---

## 策略管理器 (StrategyManager)

策略管理器可以自动选择最佳策略，并提供回退机制。

### 基本用法

```python
from app.crawlers.strategies import StrategyManager, StrategyBuilder

# 创建管理器
manager = StrategyManager()

# 添加多个策略（按优先级）
manager.add_strategy(StrategyBuilder.build_rss_strategy(
    source_name="人民日报",
    feed_url="http://www.people.com.cn/rss/finance.xml"
))

manager.add_strategy(MyHTTPParser(
    source_name="人民日报",
    source_url="http://www.people.com.cn/finance/"
))

# 自动选择最佳策略获取文章
articles = manager.fetch_with_fallback()
```

### 回退机制

如果高优先级的策略失败，会自动尝试下一个策略：

```
尝试 RSS策略 → 失败
尝试 HTTP策略 → 成功 ✓
```

---

## 完整示例：创建新的爬虫

### 示例1：简单的HTTP爬虫

```python
# app/crawlers/custom/my_news_crawler.py

from typing import List
from bs4 import BeautifulSoup
from app.crawlers.base import BaseCrawler, Article
from app.crawlers.strategies import HTTPStrategy, StrategyManager

class MyNewsParser(HTTPStrategy):
    """我的新闻网站解析器"""
    
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        articles = []
        
        for item in soup.select('.news-item'):
            title = self.extract_text(item.select_one('h3'))
            link = self.extract_link(item.select_one('a'), self.source_url)
            content = self.extract_text(item.select_one('.summary'))
            
            if title and link and self.validate_content(content):
                articles.append(Article(
                    title=title,
                    link=link,
                    content=content,
                    source_name=self.source_name
                ))
        
        return articles

class MyNewsCrawler(BaseCrawler):
    """我的新闻爬虫"""
    
    def fetch(self) -> List[Article]:
        manager = StrategyManager()
        
        # 添加HTTP策略
        manager.add_strategy(MyNewsParser(
            source_name=self.source_name,
            source_url=self.source_url
        ))
        
        return manager.fetch_with_fallback()
```

### 示例2：多策略爬虫（带回退）

```python
# app/crawlers/custom/advanced_crawler.py

from typing import List
from bs4 import BeautifulSoup
from app.crawlers.base import BaseCrawler, Article
from app.crawlers.strategies import (
    RSSStrategy, HTTPStrategy, SeleniumStrategy,
    StrategyManager, StrategyBuilder
)

class AdvancedHTTPParser(HTTPStrategy):
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        # HTTP解析逻辑
        pass

class AdvancedSeleniumParser(SeleniumStrategy):
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        # Selenium解析逻辑
        pass

class AdvancedCrawler(BaseCrawler):
    """高级爬虫 - 支持多种策略"""
    
    def fetch(self) -> List[Article]:
        manager = StrategyManager()
        
        # 策略1: 尝试RSS（如果有）
        if hasattr(self, 'rss_url'):
            manager.add_strategy(StrategyBuilder.build_rss_strategy(
                source_name=self.source_name,
                feed_url=self.rss_url
            ))
        
        # 策略2: 尝试HTTP
        manager.add_strategy(AdvancedHTTPParser(
            source_name=self.source_name,
            source_url=self.source_url
        ))
        
        # 策略3: 最后尝试Selenium
        manager.add_strategy(AdvancedSeleniumParser(
            source_name=self.source_name,
            source_url=self.source_url,
            headless=True
        ))
        
        # 自动选择最佳策略
        return manager.fetch_with_fallback()
```

---

## 配置文件集成

在`config.yaml`中配置新的爬虫：

```yaml
sources:
  custom:
    - name: "我的新闻网站"
      category: "经济"
      crawler_class: "MyNewsCrawler"
      url: "https://mynews.com"
      enabled: true
```

---

## 迁移指南

### 从旧爬虫迁移到新架构

**旧代码：**
```python
class OldCrawler(BaseCrawler):
    def fetch(self) -> List[Article]:
        response = requests.get(self.source_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 解析逻辑...
        return articles
```

**新代码：**
```python
class NewParser(HTTPStrategy):
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        # 将原来的解析逻辑移到这里
        return articles

class NewCrawler(BaseCrawler):
    def fetch(self) -> List[Article]:
        manager = StrategyManager()
        manager.add_strategy(NewParser(
            source_name=self.source_name,
            source_url=self.source_url
        ))
        return manager.fetch_with_fallback()
```

---

## 最佳实践

### 1. 优先使用高优先级策略
- 如果网站有RSS，优先使用RSS策略
- 避免不必要地使用Selenium（资源消耗大）

### 2. 合理设置超时时间
```python
strategy = HTTPStrategy(
    source_name="示例",
    source_url="https://example.com",
    timeout=30  # 30秒超时
)
```

### 3. 添加错误处理
```python
try:
    articles = manager.fetch_with_fallback()
except Exception as e:
    logger.error(f"爬取失败: {e}")
    # 发送告警、记录日志等
```

### 4. 使用日志记录
```python
self.logger.info("开始爬取")
self.logger.debug(f"找到 {len(articles)} 篇文章")
self.logger.error(f"爬取失败: {error}")
```

### 5. 内容验证
```python
if self.validate_content(content, min_length=100):
    # 内容有效，至少100字
    articles.append(article)
```

---

## 常见问题

### Q1: Selenium策略报错"ChromeDriver not found"
**A:** 需要下载ChromeDriver并添加到PATH，或在代码中指定路径。

### Q2: 如何调试解析逻辑？
**A:** 可以单独测试解析器：
```python
parser = MyHTTPParser("测试", "https://example.com")
articles = parser.fetch()
print(f"获取到 {len(articles)} 篇文章")
```

### Q3: 如何处理需要登录的网站？
**A:** 使用Selenium策略，在fetch方法中添加登录逻辑：
```python
def fetch(self) -> List[Article]:
    self._init_driver()
    self.driver.get("https://example.com/login")
    # 填写登录表单
    # ...
    return super().fetch()
```

### Q4: 如何提高爬取速度？
**A:** 
- 优先使用RSS/RSSHub策略
- HTTP策略比Selenium快得多
- 使用异步爬取（未来版本支持）

---

## 总结

新的爬虫架构具有以下优势：

1. **清晰的层次结构** - 策略模式使代码更易维护
2. **自动回退机制** - 提高爬取成功率
3. **易于扩展** - 添加新策略只需继承基类
4. **优先级管理** - 自动选择最佳策略
5. **向后兼容** - 旧代码仍然可以正常工作

建议新的爬虫都使用新架构开发，旧爬虫可以逐步迁移。
