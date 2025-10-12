"""日志配置模块"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    name: str,
    log_file: str = "logs/app.log",
    level: str = "INFO",
    max_bytes: int = 10485760,
    backup_count: int = 5
) -> logging.Logger:
    """
    配置并返回logger实例
    
    Args:
        name: logger名称
        log_file: 日志文件路径
        level: 日志级别
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的日志文件数量
    
    Returns:
        配置好的logger实例
    """
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（带轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# 创建各模块的logger实例
app_logger = setup_logger('app')
crawler_logger = setup_logger('crawler')
ai_logger = setup_logger('ai')
email_logger = setup_logger('email')
scheduler_logger = setup_logger('scheduler')
