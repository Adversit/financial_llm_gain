"""中国证券监督管理委员会爬虫"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
from app.crawlers.base import BaseCrawler, Article


class CSRCCrawler(BaseCrawler):
    """中国证券监督管理委员会（CSRC）自定义爬虫"""
    
    def __init__(self, source_name: str = None, source_url: str = None):
        """
        初始化CSRC爬虫
        
        Args:
            source_name: 信息源名称
            source_url: 信息源URL
        """
        super().__init__(source_name=source_name, source_url=source_url or "http://www.csrc.gov.cn/")
        self.timeout = 30
    
    def fetch(self) -> List[Article]:
        """
        获取证监会新闻列表
        
        Returns:
            文章列表
        """
        articles = []
        
        try:
            self.logger.info(f"开始爬取证监会网站: {self.source_url}")
            
            # 证监会新闻列表页面
            news_url = f"{self.source_url.rstrip('/')}/csrc/c100028/common_list.shtml"
            
            response = requests.get(
                news_url,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找新闻列表（根据实际网站结构调整选择器）
            news_items = soup.select('.list-item') or soup.select('ul.list li')
            
            for item in news_items[:10]:  # 限制获取前10条
                try:
                    article = self._parse_news_item(item)
                    if article and self.validate_content(article.content):
                        articles.append(article)
                except Exception as e:
                    self.logger.error(f"解析新闻项失败: {e}")
                    continue
            
            self.log_success(len(articles))
            
        except Exception as e:
            self.log_error(e)
            # 不抛出异常，返回空列表
        
        return articles
    
    def _parse_news_item(self, item) -> Article:
        """
        解析新闻项
        
        Args:
            item: BeautifulSoup元素
        
        Returns:
            Article对象
        """
        # 提取标题和链接
        link_elem = item.select_one('a')
        if not link_elem:
            raise ValueError("未找到链接元素")
        
        title = self.clean_text(link_elem.get('title') or link_elem.get_text())
        link = link_elem.get('href', '')
        
        # 处理相对链接
        if link and not link.startswith('http'):
            link = f"{self.source_url.rstrip('/')}/{link.lstrip('/')}"
        
        # 提取日期
        date_elem = item.select_one('.time') or item.select_one('span')
        publish_time = None
        if date_elem:
            date_text = date_elem.get_text().strip()
            try:
                # 尝试多种日期格式
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日']:
                    try:
                        publish_time = datetime.strptime(date_text, fmt)
                        break
                    except:
                        continue
            except:
                pass
        
        # 获取文章详情页内容
        content = self._fetch_article_content(link)
        
        return Article(
            title=title,
            link=link,
            content=content,
            publish_time=publish_time,
            source_name=self.source_name
        )
    
    def _fetch_article_content(self, url: str) -> str:
        """
        获取文章详情页内容
        
        Args:
            url: 文章URL
        
        Returns:
            文章内容
        """
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找正文内容（根据实际网站结构调整选择器）
            content_elem = (
                soup.select_one('.article-content') or 
                soup.select_one('.content') or
                soup.select_one('#content')
            )
            
            if content_elem:
                # 移除脚本和样式
                for script in content_elem(['script', 'style']):
                    script.decompose()
                
                content = content_elem.get_text(separator='\n', strip=True)
                return self.clean_text(content)
            
            return ""
            
        except Exception as e:
            self.logger.warning(f"获取文章内容失败 {url}: {e}")
            return ""
