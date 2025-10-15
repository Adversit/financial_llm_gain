"""爬虫策略基类 - 定义不同的爬取策略"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.crawlers.base import Article
from app.utils.logger import crawler_logger


class CrawlerStrategy(ABC):
    """
    爬虫策略基类
    
    定义了爬取策略的优先级和接口
    优先级: RSS > RSSHub > HTTP Request > Selenium > Custom Parser
    """
    
    # 策略优先级（数字越小优先级越高）
    PRIORITY_RSS = 1
    PRIORITY_RSSHUB = 2
    PRIORITY_HTTP = 3
    PRIORITY_SELENIUM = 4
    PRIORITY_CUSTOM = 5
    PRIORITY_FIRECRAWL = 6
    
    def __init__(self, source_name: str, source_url: str):
        """
        初始化策略
        
        Args:
            source_name: 信息源名称
            source_url: 信息源URL
        """
        self.source_name = source_name
        self.source_url = source_url
        self.logger = crawler_logger
    
    @abstractmethod
    def fetch(self) -> List[Article]:
        """
        执行爬取
        
        Returns:
            文章列表
        """
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """
        获取策略优先级
        
        Returns:
            优先级数字（越小越优先）
        """
        pass
    
    @abstractmethod
    def can_handle(self) -> bool:
        """
        判断是否可以处理该源
        
        Returns:
            是否可以处理
        """
        pass
    
    def validate_content(self, content: str, min_length: int = 50) -> bool:
        """验证内容有效性"""
        if not content:
            return False
        clean_content = content.strip()
        return len(clean_content) >= min_length
    
    def clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        text = " ".join(text.split())
        return text.strip()
    
    def log_success(self, count: int):
        """记录成功日志"""
        self.logger.info(f"[{self.source_name}] [{self.__class__.__name__}] 成功获取 {count} 篇文章")
    
    def log_error(self, error: Exception):
        """记录错误日志"""
        self.logger.error(f"[{self.source_name}] [{self.__class__.__name__}] 爬取失败: {str(error)}")
    
    def log_warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(f"[{self.source_name}] [{self.__class__.__name__}] {message}")
