"""RSS爬虫"""
import feedparser
import requests
from datetime import datetime
from typing import List
from time import mktime
from app.crawlers.base import BaseCrawler, Article


class RSSCrawler(BaseCrawler):
    """RSS爬虫 - 使用feedparser解析RSS源"""
    
    def __init__(self, feed_url: str, source_name: str = None, timeout: int = 30):
        """
        初始化RSS爬虫
        
        Args:
            feed_url: RSS订阅地址
            source_name: 信息源名称
            timeout: 请求超时时间（秒）
        """
        super().__init__(source_name=source_name, source_url=feed_url)
        self.feed_url = feed_url
        self.timeout = timeout
    
    def fetch(self) -> List[Article]:
        """
        获取RSS文章列表
        
        Returns:
            文章列表
        """
        articles = []
        
        try:
            self.logger.info(f"开始获取RSS源: {self.feed_url}")
            
            # 使用requests获取RSS内容（支持更好的错误处理）
            response = requests.get(
                self.feed_url,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
            
            # 解析RSS
            feed = feedparser.parse(response.content)
            
            # 检查是否解析成功
            if feed.bozo:
                self.log_warning(f"RSS解析警告: {feed.bozo_exception}")
            
            # 处理每个条目
            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry)
                    if article and self.validate_content(article.content):
                        articles.append(article)
                except Exception as e:
                    self.logger.error(f"解析RSS条目失败: {e}")
                    continue
            
            self.log_success(len(articles))
            
        except requests.RequestException as e:
            self.log_error(e)
            raise
        except Exception as e:
            self.log_error(e)
            raise
        
        return articles
    
    def _parse_entry(self, entry) -> Article:
        """
        解析RSS条目
        
        Args:
            entry: feedparser的entry对象
        
        Returns:
            Article对象
        """
        # 提取标题
        title = self.clean_text(entry.get('title', ''))
        
        # 提取链接
        link = entry.get('link', '')
        
        # 提取内容（优先使用content，其次summary，最后description）
        content = ''
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].get('value', '')
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        content = self.clean_text(content)
        
        # 提取发布时间
        publish_time = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            publish_time = datetime.fromtimestamp(mktime(entry.published_parsed))
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            publish_time = datetime.fromtimestamp(mktime(entry.updated_parsed))
        
        return Article(
            title=title,
            link=link,
            content=content,
            publish_time=publish_time,
            source_name=self.source_name
        )
