"""示例：使用Firecrawl策略的爬虫"""
from typing import List
from datetime import datetime

from app.crawlers.base import BaseCrawler, Article
from app.crawlers.strategies import FirecrawlStrategy, StrategyManager


class ExampleFirecrawlParser(FirecrawlStrategy):
    """示例Firecrawl解析器 - 用于难以爬取的网站"""
    
    def parse_firecrawl_data(self, data: dict) -> List[Article]:
        """
        解析Firecrawl返回的数据
        
        这里可以根据实际需求自定义解析逻辑
        """
        articles = []
        
        # 获取页面元数据
        metadata = data.get('metadata', {})
        title = metadata.get('title', '未知标题')
        description = metadata.get('description', '')
        
        # 获取Markdown内容
        markdown_content = data.get('markdown', '')
        
        # 获取HTML内容（如果需要）
        html_content = data.get('html', '')
        
        # 使用Markdown内容（更干净）
        content = markdown_content or html_content or description
        
        if not content:
            self.log_warning("Firecrawl未返回有效内容")
            return articles
        
        # 清理内容
        content = self.clean_text(content)
        
        # 验证内容长度
        if self.validate_content(content, min_length=100):
            articles.append(Article(
                title=title,
                link=self.source_url,
                content=content,
                publish_time=datetime.now(),
                source_name=self.source_name
            ))
            
            self.logger.info(f"成功解析文章: {title[:50]}...")
        else:
            self.log_warning(f"内容长度不足: {len(content)} 字符")
        
        return articles


class ExampleFirecrawlCrawler(BaseCrawler):
    """
    示例Firecrawl爬虫
    
    用于那些难以用常规方法爬取的网站：
    - 复杂的JavaScript渲染
    - 强反爬机制
    - 需要特殊处理的页面
    
    API密钥会自动从.env配置中读取
    """
    
    def fetch(self) -> List[Article]:
        """使用Firecrawl策略获取文章"""
        manager = StrategyManager()
        
        # 添加Firecrawl策略（API密钥自动从配置读取）
        manager.add_strategy(ExampleFirecrawlParser(
            source_name=self.source_name,
            source_url=self.source_url
            # api_key会自动从.env中的FIRECRAWL_API_KEY读取
        ))
        
        return manager.fetch_with_fallback()


class MultiStrategyWithFirecrawlCrawler(BaseCrawler):
    """
    多策略爬虫 - 包含Firecrawl作为最后的备选方案
    
    这个爬虫展示了如何使用完整的策略链：
    RSS → RSSHub → HTTP → Selenium → Custom → Firecrawl
    
    所有API密钥都会自动从配置中读取
    """
    
    def __init__(
        self,
        source_name: str,
        source_url: str,
        rss_url: str = None
    ):
        """
        初始化爬虫
        
        Args:
            source_name: 信息源名称
            source_url: 目标URL
            rss_url: RSS地址（可选）
        """
        super().__init__(source_name, source_url)
        self.rss_url = rss_url
    
    def fetch(self) -> List[Article]:
        """使用多策略获取文章"""
        from app.crawlers.strategies import (
            RSSStrategy,
            HTTPStrategy,
            StrategyManager
        )
        
        manager = StrategyManager()
        
        # 策略1: 尝试RSS（如果有）
        if self.rss_url:
            manager.add_strategy(RSSStrategy(
                source_name=self.source_name,
                feed_url=self.rss_url
            ))
            self.logger.info("添加RSS策略")
        
        # 策略2: 尝试HTTP（需要自定义解析器）
        # manager.add_strategy(MyHTTPParser(...))
        
        # 策略3: 尝试Selenium（如果需要）
        # manager.add_strategy(MySeleniumParser(...))
        
        # 策略4: 最后尝试Firecrawl（API密钥自动从配置读取）
        manager.add_strategy(ExampleFirecrawlParser(
            source_name=self.source_name,
            source_url=self.source_url
            # api_key会自动从.env中的FIRECRAWL_API_KEY读取
        ))
        self.logger.info("添加Firecrawl策略作为备选")
        
        # 自动选择最佳策略（带回退）
        return manager.fetch_with_fallback()
