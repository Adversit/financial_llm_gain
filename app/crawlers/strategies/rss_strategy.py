"""RSS爬取策略"""
import feedparser
import requests
from datetime import datetime
from typing import List
from time import mktime
from bs4 import BeautifulSoup
import re

from app.crawlers.strategies.base_strategy import CrawlerStrategy
from app.crawlers.base import Article


class RSSStrategy(CrawlerStrategy):
    """RSS爬取策略 - 优先级最高"""
    
    def __init__(self, source_name: str, feed_url: str, timeout: int = 30):
        """
        初始化RSS策略
        
        Args:
            source_name: 信息源名称
            feed_url: RSS订阅地址
            timeout: 请求超时时间
        """
        super().__init__(source_name, feed_url)
        self.feed_url = feed_url
        self.timeout = timeout
    
    def get_priority(self) -> int:
        """RSS策略优先级最高"""
        return self.PRIORITY_RSS
    
    def can_handle(self) -> bool:
        """检查是否为有效的RSS源"""
        try:
            # 尝试GET请求获取少量内容
            response = requests.get(
                self.feed_url, 
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0'},
                stream=True
            )
            response.raise_for_status()
            
            # 检查Content-Type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'xml' in content_type or 'rss' in content_type:
                return True
            
            # 如果Content-Type不明确，检查内容的前1024字节
            content_sample = next(response.iter_content(1024), b'').decode('utf-8', errors='ignore')
            return '<?xml' in content_sample or '<rss' in content_sample or '<feed' in content_sample
            
        except Exception as e:
            self.logger.debug(f"RSS can_handle检查失败: {e}")
            return False
    
    def fetch(self) -> List[Article]:
        """获取RSS文章列表"""
        articles = []
        
        try:
            self.logger.info(f"使用RSS策略获取: {self.feed_url}")
            
            response = requests.get(
                self.feed_url,
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                self.log_warning(f"RSS解析警告: {feed.bozo_exception}")
            
            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry)
                    if article and self.validate_content(article.content):
                        articles.append(article)
                except Exception as e:
                    self.logger.error(f"解析RSS条目失败: {e}")
                    continue
            
            self.log_success(len(articles))
            
        except Exception as e:
            self.log_error(e)
            raise
        
        return articles
    
    def _parse_entry(self, entry) -> Article:
        """解析RSS条目"""
        title = self.clean_text(entry.get('title', ''))
        link = entry.get('link', '')
        
        # 提取内容
        content = ''
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].get('value', '')
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        if content:
            content = BeautifulSoup(content, 'html.parser').get_text(strip=True)
        
        content = self.clean_text(content) or title
        
        # 提取发布时间
        publish_time = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            publish_time = datetime.fromtimestamp(mktime(entry.published_parsed))
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            publish_time = datetime.fromtimestamp(mktime(entry.updated_parsed))
        
        if not publish_time and link:
            publish_time = self._extract_date_from_url(link)
        
        return Article(
            title=title,
            link=link,
            content=content,
            publish_time=publish_time,
            source_name=self.source_name
        )
    
    def _extract_date_from_url(self, url: str) -> datetime:
        """从URL中提取日期"""
        patterns = [
            (r'/(\d{4})-(\d{1,2})/(\d{1,2})/', '%Y-%m-%d'),  # /2022-12/10/
            (r'/(\d{4})/(\d{1,2})/(\d{1,2})/', '%Y-%m-%d'),  # /2022/12/10/
            (r'/(\d{8})/', '%Y%m%d'),  # /20221210/
        ]
        
        for pattern, fmt in patterns:
            match = re.search(pattern, url)
            if match:
                try:
                    if len(match.groups()) == 3:
                        year, month, day = match.groups()
                        return datetime(int(year), int(month), int(day))
                    else:
                        date_str = match.group(1)
                        return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        
        return None
