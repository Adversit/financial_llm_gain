"""爬虫工厂 - 根据配置创建爬虫实例"""
import importlib
import os
from typing import Optional
from app.crawlers.base import BaseCrawler
from app.crawlers.rss_crawler import RSSCrawler
from app.crawlers.rsshub_crawler import RSSHubCrawler
from app.utils.logger import crawler_logger


class CrawlerFactory:
    """爬虫工厂类"""
    
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
        
        Raises:
            ValueError: 参数不足或类型不支持
            ImportError: 自定义爬虫类导入失败
        """
        if source_type == 'rss':
            if not url:
                raise ValueError(f"RSS源 [{source_name}] 缺少url参数")
            return RSSCrawler(feed_url=url, source_name=source_name)
        
        elif source_type == 'rsshub':
            if not rsshub_base or not rsshub_route:
                raise ValueError(f"RSSHub源 [{source_name}] 缺少rsshub_base或rsshub_route参数")
            return RSSHubCrawler(
                rsshub_base=rsshub_base,
                route=rsshub_route,
                source_name=source_name
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
        
        Raises:
            ImportError: 爬虫类导入失败
        """
        try:
            # 构建模块路径
            module_path = f"app.crawlers.custom.{CrawlerFactory._class_to_module(crawler_class)}"
            
            crawler_logger.info(f"尝试加载自定义爬虫: {module_path}.{crawler_class}")
            
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
        """
        将类名转换为模块名
        例如: MIITCrawler -> miit_crawler
        
        Args:
            class_name: 类名
        
        Returns:
            模块名
        """
        # 移除Crawler后缀
        if class_name.endswith('Crawler'):
            class_name = class_name[:-7]
        
        # 转换为snake_case
        result = []
        for i, char in enumerate(class_name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        
        return ''.join(result) + '_crawler'
