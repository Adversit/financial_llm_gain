"""Firecrawl爬取策略 - 使用Firecrawl API作为最后的备选方案"""
from typing import List, Optional
from datetime import datetime
import requests

from app.crawlers.strategies.base_strategy import CrawlerStrategy
from app.crawlers.base import Article


class FirecrawlStrategy(CrawlerStrategy):
    """
    Firecrawl爬取策略 - 优先级最低（作为最后的备选方案）
    
    Firecrawl是一个强大的网页爬取API，可以：
    - 处理JavaScript渲染
    - 绕过反爬机制
    - 提取结构化数据
    - 转换为Markdown格式
    
    优先级：6（最低，仅在其他策略都失败时使用）
    """
    
    PRIORITY_FIRECRAWL = 6
    
    def __init__(
        self,
        source_name: str,
        source_url: str,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: int = 60,
        formats: List[str] = None
    ):
        """
        初始化Firecrawl策略
        
        Args:
            source_name: 信息源名称
            source_url: 目标URL
            api_key: Firecrawl API密钥（如果为None，从配置中读取）
            api_url: Firecrawl API地址（如果为None，从配置中读取）
            timeout: 请求超时时间
            formats: 返回格式列表，如['markdown', 'html']
        """
        super().__init__(source_name, source_url)
        
        # 如果没有提供API密钥，从配置中读取
        if api_key is None:
            api_key = self._get_api_key_from_config()
        
        # 如果没有提供API URL，从配置中读取
        if api_url is None:
            api_url = self._get_api_url_from_config()
        
        self.api_key = api_key
        self.api_url = api_url.rstrip('/') if api_url else "https://api.firecrawl.dev/v0"
        self.timeout = timeout
        self.formats = formats or ['markdown', 'html']
    
    def _get_api_key_from_config(self) -> Optional[str]:
        """从配置中获取API密钥"""
        try:
            from app.config import get_config
            config = get_config()
            return config.get('firecrawl', {}).get('api_key')
        except:
            return None
    
    def _get_api_url_from_config(self) -> Optional[str]:
        """从配置中获取API URL"""
        try:
            from app.config import get_config
            config = get_config()
            return config.get('firecrawl', {}).get('api_url')
        except:
            return None
    
    def get_priority(self) -> int:
        """Firecrawl策略优先级最低"""
        return self.PRIORITY_FIRECRAWL
    
    def can_handle(self) -> bool:
        """检查Firecrawl是否可用"""
        if not self.api_key:
            self.log_warning("未配置Firecrawl API密钥")
            return False
        
        try:
            # 测试API连接
            response = requests.get(
                f"{self.api_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def fetch(self) -> List[Article]:
        """使用Firecrawl获取文章列表"""
        articles = []
        
        try:
            self.logger.info(f"使用Firecrawl策略获取: {self.source_url}")
            
            # 调用Firecrawl API爬取页面
            page_data = self._scrape_page()
            
            if not page_data:
                self.log_warning("Firecrawl未返回数据")
                return articles
            
            # 解析Firecrawl返回的数据
            articles = self.parse_firecrawl_data(page_data)
            
            self.log_success(len(articles))
            
        except Exception as e:
            self.log_error(e)
            raise
        
        return articles
    
    def _scrape_page(self) -> dict:
        """
        调用Firecrawl API爬取页面
        
        Returns:
            Firecrawl返回的数据
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'url': self.source_url,
            'formats': self.formats,
            'onlyMainContent': True,  # 只提取主要内容
            'waitFor': 2000,  # 等待2秒让JavaScript执行
        }
        
        response = requests.post(
            f"{self.api_url}/scrape",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        result = response.json()
        
        if not result.get('success'):
            raise Exception(f"Firecrawl爬取失败: {result.get('error', 'Unknown error')}")
        
        return result.get('data', {})
    
    def parse_firecrawl_data(self, data: dict) -> List[Article]:
        """
        解析Firecrawl返回的数据
        
        子类可以重写此方法来实现自定义解析逻辑
        
        Args:
            data: Firecrawl返回的数据
        
        Returns:
            文章列表
        """
        articles = []
        
        # 默认实现：将整个页面作为一篇文章
        title = data.get('metadata', {}).get('title', '未知标题')
        content = data.get('markdown', '') or data.get('html', '')
        
        if not content:
            self.log_warning("Firecrawl未返回内容")
            return articles
        
        # 清理内容
        content = self.clean_text(content)
        
        if self.validate_content(content, min_length=100):
            articles.append(Article(
                title=title,
                link=self.source_url,
                content=content,
                publish_time=datetime.now(),
                source_name=self.source_name
            ))
        
        return articles
    
    def crawl_multiple_pages(self, urls: List[str]) -> List[Article]:
        """
        批量爬取多个页面
        
        Args:
            urls: URL列表
        
        Returns:
            文章列表
        """
        all_articles = []
        
        for url in urls:
            try:
                # 临时修改source_url
                original_url = self.source_url
                self.source_url = url
                
                articles = self.fetch()
                all_articles.extend(articles)
                
                # 恢复原始URL
                self.source_url = original_url
                
            except Exception as e:
                self.logger.error(f"爬取 {url} 失败: {e}")
                continue
        
        return all_articles
    
    def extract_links(self, data: dict) -> List[str]:
        """
        从Firecrawl数据中提取链接
        
        Args:
            data: Firecrawl返回的数据
        
        Returns:
            链接列表
        """
        links = []
        
        # 从metadata中提取链接
        metadata = data.get('metadata', {})
        if 'links' in metadata:
            links.extend(metadata['links'])
        
        return links


class FirecrawlListStrategy(FirecrawlStrategy):
    """
    Firecrawl列表页策略
    
    用于爬取列表页，然后提取文章链接
    """
    
    def parse_firecrawl_data(self, data: dict) -> List[Article]:
        """
        解析列表页，提取文章链接
        
        Args:
            data: Firecrawl返回的数据
        
        Returns:
            文章列表
        """
        articles = []
        
        # 提取链接
        links = self.extract_links(data)
        
        if not links:
            self.log_warning("未找到文章链接")
            return articles
        
        self.logger.info(f"找到 {len(links)} 个链接")
        
        # 爬取每个链接（限制数量）
        max_articles = 20
        for link in links[:max_articles]:
            try:
                # 创建新的Firecrawl策略实例爬取详情页
                detail_strategy = FirecrawlStrategy(
                    source_name=self.source_name,
                    source_url=link,
                    api_key=self.api_key,
                    api_url=self.api_url
                )
                
                detail_articles = detail_strategy.fetch()
                articles.extend(detail_articles)
                
            except Exception as e:
                self.logger.error(f"爬取详情页 {link} 失败: {e}")
                continue
        
        return articles
