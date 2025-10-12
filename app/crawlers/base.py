"""基础爬虫类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from app.utils.logger import crawler_logger


@dataclass
class Article:
    """文章数据类 - 标准化的文章数据结构"""
    title: str
    link: str
    content: str
    publish_time: Optional[datetime] = None
    source_name: Optional[str] = None
    
    def __post_init__(self):
        """数据验证"""
        if not self.title:
            raise ValueError("文章标题不能为空")
        if not self.link:
            raise ValueError("文章链接不能为空")
        if not self.content:
            raise ValueError("文章内容不能为空")


class BaseCrawler(ABC):
    """
    爬虫基类
    所有爬虫必须继承此类并实现fetch方法
    """
    
    def __init__(self, source_name: str = None, source_url: str = None):
        """
        初始化爬虫
        
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
        获取文章列表
        子类必须实现此方法
        
        Returns:
            文章列表
        """
        pass
    
    def validate_content(self, content: str, min_length: int = 50) -> bool:
        """
        验证内容有效性（字数检查）
        
        Args:
            content: 文章内容
            min_length: 最小字数要求（默认50字）
        
        Returns:
            是否有效
        """
        if not content:
            return False
        
        # 去除空白字符后检查长度
        clean_content = content.strip()
        is_valid = len(clean_content) >= min_length
        
        if not is_valid:
            self.logger.debug(
                f"内容长度不足: {len(clean_content)} < {min_length}"
            )
        
        return is_valid
    
    def clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
        
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 去除多余空白
        text = " ".join(text.split())
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def log_success(self, count: int):
        """记录成功日志"""
        self.logger.info(
            f"[{self.source_name}] 成功获取 {count} 篇文章"
        )
    
    def log_error(self, error: Exception):
        """记录错误日志"""
        self.logger.error(
            f"[{self.source_name}] 爬取失败: {str(error)}"
        )
    
    def log_warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(
            f"[{self.source_name}] {message}"
        )
