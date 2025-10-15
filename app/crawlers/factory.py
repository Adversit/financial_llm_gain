"""爬虫工厂 - 使用新的策略架构"""
import importlib
from typing import Optional
from app.crawlers.base import BaseCrawler
from app.crawlers.strategies import (
    RSSStrategy,
    RSSHubStrategy,
    StrategyManager,
    StrategyBuilder
)
from app.utils.logger import crawler_logger


class StrategyCrawler(BaseCrawler):
    """
    策略爬虫 - 使用策略管理器的通用爬虫
    
    这个爬虫会根据配置自动选择最佳策略
    """
    
    def __init__(
        self,
        source_name: str,
        source_url: Optional[str] = None,
        source_type: str = None,
        rsshub_base: Optional[str] = None,
        rsshub_route: Optional[str] = None
    ):
        """
        初始化策略爬虫
        
        Args:
            source_name: 信息源名称
            source_url: 信息源URL
            source_type: 源类型（rss/rsshub）
            rsshub_base: RSSHub基础URL
            rsshub_route: RSSHub路由
        """
        super().__init__(source_name, source_url)
        self.source_type = source_type
        self.rsshub_base = rsshub_base
        self.rsshub_route = rsshub_route
    
    def fetch(self):
        """使用策略管理器获取文章"""
        manager = StrategyManager()
        
        # 根据类型添加策略
        if self.source_type == 'rss' and self.source_url:
            manager.add_strategy(RSSStrategy(
                source_name=self.source_name,
                feed_url=self.source_url
            ))
        
        elif self.source_type == 'rsshub' and self.rsshub_base and self.rsshub_route:
            manager.add_strategy(RSSHubStrategy(
                source_name=self.source_name,
                rsshub_base=self.rsshub_base,
                route=self.rsshub_route
            ))
        
        # 使用策略管理器获取文章（自动回退）
        return manager.fetch_with_fallback()


class CrawlerFactory:
    """爬虫工厂类 - 使用新的策略架构"""
    
    @staticmethod
    def create_crawler(
        source_type: str,
        source_name: str,
        url: Optional[str] = None,
        rsshub_base: Optional[str] = None,
        rsshub_route: Optional[str] = None,
        crawler_class: Optional[str] = None
    ) -> BaseCrawler:
        """
        根据配置创建相应的爬虫实例
        
        Args:
            source_type: 爬虫类型（rss/rsshub/custom）
            source_name: 信息源名称
            url: RSS地址或网站地址
            rsshub_base: RSSHub基础URL
            rsshub_route: RSSHub路由
            crawler_class: 自定义爬虫类名
        
        Returns:
            爬虫实例
        """
        if source_type == 'rss':
            if not url:
                raise ValueError(f"RSS源 [{source_name}] 缺少url参数")
            return StrategyCrawler(
                source_name=source_name,
                source_url=url,
                source_type='rss'
            )
        
        elif source_type == 'rsshub':
            if not rsshub_base or not rsshub_route:
                raise ValueError(f"RSSHub源 [{source_name}] 缺少rsshub_base或rsshub_route参数")
            return StrategyCrawler(
                source_name=source_name,
                source_type='rsshub',
                rsshub_base=rsshub_base,
                rsshub_route=rsshub_route
            )
        
        elif source_type == 'custom':
            if not crawler_class:
                raise ValueError(f"自定义爬虫源 [{source_name}] 缺少crawler_class参数")
            return CrawlerFactory._load_custom_crawler(
                crawler_class=crawler_class,
                source_name=source_name,
                source_url=url
            )
        
        else:
            raise ValueError(f"不支持的爬虫类型: {source_type}")
    
    @staticmethod
    def _load_custom_crawler(
        crawler_class: str,
        source_name: str,
        source_url: Optional[str] = None
    ) -> BaseCrawler:
        """
        动态加载自定义爬虫类
        
        Args:
            crawler_class: 爬虫类名
            source_name: 信息源名称
            source_url: 信息源URL
        
        Returns:
            爬虫实例
        """
        try:
            # 构建模块路径
            module_path = f"app.crawlers.custom.{CrawlerFactory._class_to_module(crawler_class)}"
            
            crawler_logger.info(f"加载自定义爬虫: {module_path}.{crawler_class}")
            
            # 动态导入模块
            module = importlib.import_module(module_path)
            
            # 获取爬虫类
            crawler_cls = getattr(module, crawler_class)
            
            # 验证是否继承自BaseCrawler
            if not issubclass(crawler_cls, BaseCrawler):
                raise TypeError(f"{crawler_class} 必须继承自 BaseCrawler")
            
            # 创建实例
            return crawler_cls(source_name=source_name, source_url=source_url)
            
        except ImportError as e:
            crawler_logger.error(f"无法导入自定义爬虫 {crawler_class}: {e}")
            raise ImportError(
                f"自定义爬虫 {crawler_class} 不存在。"
                f"请在 app/crawlers/custom/ 目录下创建对应的爬虫文件。"
            )
        except AttributeError as e:
            crawler_logger.error(f"爬虫类 {crawler_class} 不存在: {e}")
            raise ImportError(f"在模块中找不到爬虫类 {crawler_class}")
    
    @staticmethod
    def _class_to_module(class_name: str) -> str:
        """将类名转换为模块名"""
        if class_name.endswith('Crawler'):
            class_name = class_name[:-7]
        
        result = []
        for i, char in enumerate(class_name):
            if char.isupper():
                if i > 0 and (not class_name[i-1].isupper() or 
                             (i < len(class_name) - 1 and class_name[i+1].islower())):
                    result.append('_')
            result.append(char.lower())
        
        return ''.join(result) + '_crawler'
