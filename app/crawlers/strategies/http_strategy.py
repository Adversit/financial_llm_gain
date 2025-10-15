"""HTTP Request爬取策略"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime

from app.crawlers.strategies.base_strategy import CrawlerStrategy
from app.crawlers.base import Article


class HTTPStrategy(CrawlerStrategy):
    """HTTP Request爬取策略 - 优先级第三"""
    
    def __init__(
        self,
        source_name: str,
        source_url: str,
        timeout: int = 30,
        headers: Optional[dict] = None
    ):
        """
        初始化HTTP策略
        
        Args:
            source_name: 信息源名称
            source_url: 目标URL
            timeout: 请求超时时间
            headers: 自定义请求头
        """
        super().__init__(source_name, source_url)
        self.timeout = timeout
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_priority(self) -> int:
        """HTTP策略优先级第三"""
        return self.PRIORITY_HTTP
    
    def can_handle(self) -> bool:
        """检查URL是否可访问"""
        try:
            response = requests.head(self.source_url, timeout=5, headers=self.headers)
            return response.status_code == 200
        except:
            return False
    
    def fetch(self) -> List[Article]:
        """
        获取文章列表
        
        子类应该重写此方法实现具体的解析逻辑
        """
        articles = []
        
        try:
            self.logger.info(f"使用HTTP策略获取: {self.source_url}")
            
            response = requests.get(
                self.source_url,
                timeout=self.timeout,
                headers=self.headers
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 调用子类实现的解析方法
            articles = self.parse_page(soup)
            
            self.log_success(len(articles))
            
        except Exception as e:
            self.log_error(e)
            raise
        
        return articles
    
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        """
        解析页面内容
        
        子类必须实现此方法
        
        Args:
            soup: BeautifulSoup对象
        
        Returns:
            文章列表
        """
        raise NotImplementedError("子类必须实现parse_page方法")
    
    def extract_text(self, element) -> str:
        """提取元素文本"""
        if element:
            return self.clean_text(element.get_text())
        return ""
    
    def extract_link(self, element, base_url: Optional[str] = None) -> str:
        """提取链接"""
        if not element:
            return ""
        
        link = element.get('href', '')
        
        # 处理相对链接
        if link and base_url and not link.startswith('http'):
            from urllib.parse import urljoin
            link = urljoin(base_url, link)
        
        return link
