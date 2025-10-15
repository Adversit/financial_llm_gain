"""自定义解析策略 - 用于特殊页面的独有解析逻辑"""
from typing import List
from bs4 import BeautifulSoup

from app.crawlers.strategies.base_strategy import CrawlerStrategy
from app.crawlers.base import Article


class CustomStrategy(CrawlerStrategy):
    """
    自定义解析策略 - 优先级最低
    
    用于那些需要特殊解析逻辑的页面
    子类需要实现具体的解析方法
    """
    
    def get_priority(self) -> int:
        """自定义策略优先级最低"""
        return self.PRIORITY_CUSTOM
    
    def can_handle(self) -> bool:
        """自定义策略总是可以处理（作为最后的备选）"""
        return True
    
    def fetch(self) -> List[Article]:
        """
        获取文章列表
        
        子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现fetch方法")
    
    def parse_custom_format(self, data: any) -> List[Article]:
        """
        解析自定义格式的数据
        
        子类可以重写此方法来处理特殊格式
        
        Args:
            data: 任意格式的数据
        
        Returns:
            文章列表
        """
        raise NotImplementedError("子类必须实现parse_custom_format方法")
