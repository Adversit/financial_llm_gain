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
        
        # 清理HTML标签
        if content:
            from bs4 import BeautifulSoup
            content = BeautifulSoup(content, 'html.parser').get_text(strip=True)
        
        content = self.clean_text(content)
        
        # 如果内容为空，使用标题作为内容（避免Article验证失败）
        if not content:
            content = title
            self.logger.debug(f"RSS条目没有内容，使用标题作为内容: {title[:50]}")
        
        # 提取发布时间
        publish_time = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            publish_time = datetime.fromtimestamp(mktime(entry.published_parsed))
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            publish_time = datetime.fromtimestamp(mktime(entry.updated_parsed))
        
        # 如果 RSS 没有提供日期，尝试从 URL 中提取
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
        """
        从 URL 中提取日期
        
        支持的格式:
        - /2022-12/10/ (新华社格式)
        - /2022/12/10/
        - /20221210/
        
        Args:
            url: 文章 URL
        
        Returns:
            datetime 对象，如果无法提取则返回 None
        """
        import re
        
        # 格式1: /YYYY-MM/DD/ (新华社)
        pattern1 = r'/(\d{4})-(\d{1,2})/(\d{1,2})/'
        match = re.search(pattern1, url)
        if match:
            year, month, day = match.groups()
            try:
                return datetime(int(year), int(month), int(day))
            except ValueError:
                pass
        
        # 格式2: /YYYY/MM/DD/
        pattern2 = r'/(\d{4})/(\d{1,2})/(\d{1,2})/'
        match = re.search(pattern2, url)
        if match:
            year, month, day = match.groups()
            try:
                return datetime(int(year), int(month), int(day))
            except ValueError:
                pass
        
        # 格式3: /YYYYMMDD/
        pattern3 = r'/(\d{8})/'
        match = re.search(pattern3, url)
        if match:
            date_str = match.group(1)
            try:
                return datetime.strptime(date_str, '%Y%m%d')
            except ValueError:
                pass
        
        return None
