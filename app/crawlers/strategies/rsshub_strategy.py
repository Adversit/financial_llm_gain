"""RSSHub爬取策略"""
from typing import List
from app.crawlers.strategies.rss_strategy import RSSStrategy
from app.crawlers.base import Article


class RSSHubStrategy(RSSStrategy):
    """RSSHub爬取策略 - 基于RSS策略，优先级第二"""
    
    def __init__(self, source_name: str, rsshub_base: str, route: str, timeout: int = 30):
        """
        初始化RSSHub策略
        
        Args:
            source_name: 信息源名称
            rsshub_base: RSSHub基础URL
            route: RSSHub路由
            timeout: 请求超时时间
        """
        # 构建完整的RSS URL
        feed_url = f"{rsshub_base.rstrip('/')}/{route.lstrip('/')}"
        super().__init__(source_name, feed_url, timeout)
        self.rsshub_base = rsshub_base
        self.route = route
    
    def get_priority(self) -> int:
        """RSSHub策略优先级第二"""
        return self.PRIORITY_RSSHUB
    
    def can_handle(self) -> bool:
        """RSSHub总是可以处理（如果配置正确）"""
        return True
    
    def fetch(self) -> List[Article]:
        """获取RSSHub文章列表"""
        self.logger.info(f"使用RSSHub策略获取: {self.route}")
        return super().fetch()
