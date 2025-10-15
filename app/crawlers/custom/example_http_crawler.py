"""示例：使用HTTP策略的爬虫"""
from typing import List
from bs4 import BeautifulSoup
from datetime import datetime

from app.crawlers.base import BaseCrawler, Article
from app.crawlers.strategies import HTTPStrategy, StrategyManager, StrategyBuilder


class ExampleHTTPParser(HTTPStrategy):
    """示例HTTP解析器 - 继承HTTPStrategy并实现parse_page方法"""
    
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        """
        解析页面内容
        
        这里是示例代码，实际使用时需要根据目标网站的HTML结构修改
        """
        articles = []
        
        # 示例：查找所有文章容器
        article_elements = soup.select('.article-item')  # 根据实际情况修改选择器
        
        for element in article_elements:
            try:
                # 提取标题
                title_elem = element.select_one('.title')
                title = self.extract_text(title_elem)
                
                # 提取链接
                link_elem = element.select_one('a')
                link = self.extract_link(link_elem, self.source_url)
                
                # 提取内容/摘要
                content_elem = element.select_one('.content')
                content = self.extract_text(content_elem) or title
                
                # 提取时间（可选）
                time_elem = element.select_one('.time')
                publish_time = None
                if time_elem:
                    time_text = self.extract_text(time_elem)
                    # 这里需要根据实际格式解析时间
                    # publish_time = datetime.strptime(time_text, '%Y-%m-%d')
                
                if title and link and self.validate_content(content):
                    articles.append(Article(
                        title=title,
                        link=link,
                        content=content,
                        publish_time=publish_time,
                        source_name=self.source_name
                    ))
                    
            except Exception as e:
                self.logger.error(f"解析文章失败: {e}")
                continue
        
        return articles


class ExampleHTTPCrawler(BaseCrawler):
    """
    示例HTTP爬虫 - 使用策略模式
    
    这个爬虫展示了如何使用新的策略系统
    """
    
    def fetch(self) -> List[Article]:
        """使用策略管理器获取文章"""
        # 创建策略管理器
        manager = StrategyManager()
        
        # 添加HTTP策略
        http_strategy = ExampleHTTPParser(
            source_name=self.source_name,
            source_url=self.source_url
        )
        manager.add_strategy(http_strategy)
        
        # 使用策略获取文章
        return manager.fetch_with_fallback()
