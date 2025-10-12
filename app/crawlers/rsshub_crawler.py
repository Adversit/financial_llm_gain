"""RSSHub爬虫"""
from typing import List
from app.crawlers.rss_crawler import RSSCrawler
from app.crawlers.base import Article


class RSSHubCrawler(RSSCrawler):
    """
    RSSHub爬虫 - 从RSSHub获取RSS并解析
    继承自RSSCrawler，复用RSS解析逻辑
    """
    
    def __init__(self, rsshub_base: str, route: str, source_name: str = None, timeout: int = 30):
        """
        初始化RSSHub爬虫
        
        Args:
            rsshub_base: RSSHub基础URL（如：http://101.42.187.241:1200）
            route: RSSHub路由（如：36kr/news/latest）
            source_name: 信息源名称
            timeout: 请求超时时间（秒）
        """
        # 构建完整的RSSHub URL
        rsshub_url = f"{rsshub_base.rstrip('/')}/{route.lstrip('/')}"
        
        # 调用父类构造函数
        super().__init__(
            feed_url=rsshub_url,
            source_name=source_name,
            timeout=timeout
        )
        
        self.rsshub_base = rsshub_base
        self.route = route
    
    def fetch(self) -> List[Article]:
        """
        获取RSSHub文章列表
        直接调用父类的fetch方法
        
        Returns:
            文章列表
        """
        try:
            self.logger.info(f"开始获取RSSHub源: {self.route}")
            return super().fetch()
        except Exception as e:
            self.log_error(e)
            self.log_warning(f"RSSHub路由可能不可用: {self.route}")
            raise
