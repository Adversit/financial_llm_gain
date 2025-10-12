"""配置加载模块"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置文件路径
CONFIG_FILE = Path("config.yaml")


def load_config() -> Dict[str, Any]:
    """
    加载配置文件
    
    Returns:
        配置字典
    """
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_FILE}")
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 从环境变量覆盖配置
    config = _override_from_env(config)
    
    return config


def _override_from_env(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    从环境变量覆盖配置
    
    Args:
        config: 原始配置
    
    Returns:
        覆盖后的配置
    """
    # 数据库
    if os.getenv('DATABASE_URL'):
        config['database']['url'] = os.getenv('DATABASE_URL')
    
    # RSSHub
    if os.getenv('RSSHUB_BASE_URL'):
        config['rsshub']['base_url'] = os.getenv('RSSHUB_BASE_URL')
    
    # AI配置
    if os.getenv('AI_PROVIDER'):
        config['ai']['provider'] = os.getenv('AI_PROVIDER')
    if os.getenv('AI_API_KEY'):
        config['ai']['api_key'] = os.getenv('AI_API_KEY')
    if os.getenv('AI_BASE_URL'):
        config['ai']['base_url'] = os.getenv('AI_BASE_URL')
    if os.getenv('AI_MODEL'):
        config['ai']['model'] = os.getenv('AI_MODEL')
    if os.getenv('AI_TIMEOUT'):
        config['ai']['timeout'] = int(os.getenv('AI_TIMEOUT'))
    if os.getenv('AI_MAX_RETRIES'):
        config['ai']['max_retries'] = int(os.getenv('AI_MAX_RETRIES'))
    
    # 邮件配置
    if os.getenv('SMTP_SERVER'):
        config['email']['smtp_server'] = os.getenv('SMTP_SERVER')
    if os.getenv('SMTP_PORT'):
        config['email']['smtp_port'] = int(os.getenv('SMTP_PORT'))
    if os.getenv('SMTP_USERNAME'):
        config['email']['username'] = os.getenv('SMTP_USERNAME')
    if os.getenv('SMTP_PASSWORD'):
        config['email']['password'] = os.getenv('SMTP_PASSWORD')
    if os.getenv('SMTP_USE_SSL'):
        config['email']['use_ssl'] = os.getenv('SMTP_USE_SSL').lower() == 'true'
    
    # 调度配置
    if os.getenv('DAILY_REPORT_TIME'):
        config['scheduler']['daily_report_time'] = os.getenv('DAILY_REPORT_TIME')
    if os.getenv('TIMEZONE'):
        config['scheduler']['timezone'] = os.getenv('TIMEZONE')
    
    return config


# 全局配置实例
_config = None


def get_config() -> Dict[str, Any]:
    """
    获取配置（单例模式）
    
    Returns:
        配置字典
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config():
    """重新加载配置"""
    global _config
    _config = load_config()
