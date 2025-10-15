"""策略管理器 - 自动选择最佳爬取策略"""
from typing import List, Type, Optional
from app.crawlers.strategies.base_strategy import CrawlerStrategy
from app.crawlers.strategies.rss_strategy import RSSStrategy
from app.crawlers.strategies.rsshub_strategy import RSSHubStrategy
from app.crawlers.strategies.http_strategy import HTTPStrategy
from app.crawlers.strategies.selenium_strategy import SeleniumStrategy
from app.crawlers.strategies.custom_strategy import CustomStrategy
from app.crawlers.base import Article
from app.utils.logger import crawler_logger


class StrategyManager:
    """
    策略管理器
    
    根据优先级自动选择最佳的爬取策略：
    1. RSS - 如果有RSS源，优先使用
    2. RSSHub - 如果配置了RSSHub，次优先
    3. HTTP Request - 普通HTTP请求
    4. Selenium - 需要JavaScript渲染的页面
    5. Custom Parser - 特殊页面的自定义解析
    6. Firecrawl - 使用Firecrawl API（最后的备选方案）
    """
    
    def __init__(self):
        """初始化策略管理器"""
        self.logger = crawler_logger
        self.strategies: List[CrawlerStrategy] = []
    
    def add_strategy(self, strategy: CrawlerStrategy):
        """
        添加策略
        
        Args:
            strategy: 爬虫策略实例
        """
        self.strategies.append(strategy)
        self.logger.debug(f"添加策略: {strategy.__class__.__name__} (优先级: {strategy.get_priority()})")
    
    def fetch_with_fallback(self) -> List[Article]:
        """
        使用回退机制获取文章
        
        按优先级尝试每个策略，如果失败则尝试下一个
        
        Returns:
            文章列表
        """
        if not self.strategies:
            raise ValueError("没有可用的爬取策略")
        
        # 按优先级排序
        sorted_strategies = sorted(self.strategies, key=lambda s: s.get_priority())
        
        last_error = None
        
        for strategy in sorted_strategies:
            try:
                # 检查策略是否可以处理
                if not strategy.can_handle():
                    self.logger.info(f"策略 {strategy.__class__.__name__} 无法处理，跳过")
                    continue
                
                self.logger.info(f"尝试使用策略: {strategy.__class__.__name__} (优先级: {strategy.get_priority()})")
                
                # 执行爬取
                articles = strategy.fetch()
                
                if articles:
                    self.logger.info(f"策略 {strategy.__class__.__name__} 成功获取 {len(articles)} 篇文章")
                    return articles
                else:
                    self.logger.warning(f"策略 {strategy.__class__.__name__} 未获取到文章")
                    
            except Exception as e:
                last_error = e
                self.logger.warning(f"策略 {strategy.__class__.__name__} 失败: {e}")
                continue
        
        # 所有策略都失败
        error_msg = f"所有爬取策略都失败"
        if last_error:
            error_msg += f"，最后的错误: {last_error}"
        
        self.logger.error(error_msg)
        raise Exception(error_msg)
    
    def fetch_with_specific_strategy(self, strategy_class: Type[CrawlerStrategy]) -> List[Article]:
        """
        使用指定的策略获取文章
        
        Args:
            strategy_class: 策略类
        
        Returns:
            文章列表
        """
        for strategy in self.strategies:
            if isinstance(strategy, strategy_class):
                self.logger.info(f"使用指定策略: {strategy.__class__.__name__}")
                return strategy.fetch()
        
        raise ValueError(f"未找到策略: {strategy_class.__name__}")
    
    def get_available_strategies(self) -> List[str]:
        """
        获取可用的策略列表
        
        Returns:
            策略名称列表
        """
        return [s.__class__.__name__ for s in self.strategies if s.can_handle()]
    
    def clear_strategies(self):
        """清空所有策略"""
        self.strategies.clear()
        self.logger.debug("已清空所有策略")


class StrategyBuilder:
    """策略构建器 - 简化策略创建过程"""
    
    @staticmethod
    def build_rss_strategy(source_name: str, feed_url: str) -> RSSStrategy:
        """构建RSS策略"""
        return RSSStrategy(source_name, feed_url)
    
    @staticmethod
    def build_rsshub_strategy(source_name: str, rsshub_base: str, route: str) -> RSSHubStrategy:
        """构建RSSHub策略"""
        return RSSHubStrategy(source_name, rsshub_base, route)
    
    @staticmethod
    def build_http_strategy(
        source_name: str,
        source_url: str,
        parser_class: Type[HTTPStrategy]
    ) -> HTTPStrategy:
        """
        构建HTTP策略
        
        Args:
            source_name: 信息源名称
            source_url: 目标URL
            parser_class: HTTP策略的子类（实现了parse_page方法）
        """
        return parser_class(source_name, source_url)
    
    @staticmethod
    def build_selenium_strategy(
        source_name: str,
        source_url: str,
        parser_class: Type[SeleniumStrategy],
        headless: bool = True
    ) -> SeleniumStrategy:
        """
        构建Selenium策略
        
        Args:
            source_name: 信息源名称
            source_url: 目标URL
            parser_class: Selenium策略的子类（实现了parse_page方法）
            headless: 是否无头模式
        """
        return parser_class(source_name, source_url, headless=headless)
    
    @staticmethod
    def build_custom_strategy(
        source_name: str,
        source_url: str,
        parser_class: Type[CustomStrategy]
    ) -> CustomStrategy:
        """
        构建自定义策略
        
        Args:
            source_name: 信息源名称
            source_url: 目标URL
            parser_class: 自定义策略的子类
        """
        return parser_class(source_name, source_url)
    
    @staticmethod
    def build_firecrawl_strategy(
        source_name: str,
        source_url: str,
        api_key: str,
        api_url: str = "https://api.firecrawl.dev/v0"
    ):
        """
        构建Firecrawl策略
        
        Args:
            source_name: 信息源名称
            source_url: 目标URL
            api_key: Firecrawl API密钥
            api_url: Firecrawl API地址
        """
        from app.crawlers.strategies.firecrawl_strategy import FirecrawlStrategy
        return FirecrawlStrategy(
            source_name=source_name,
            source_url=source_url,
            api_key=api_key,
            api_url=api_url
        )
