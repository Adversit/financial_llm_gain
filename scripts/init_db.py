"""数据库初始化脚本"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import init_db, engine
from app.utils.logger import app_logger


def main():
    """初始化数据库"""
    try:
        app_logger.info("开始初始化数据库...")
        
        # 创建所有表
        init_db()
        
        app_logger.info("数据库初始化完成！")
        app_logger.info(f"数据库位置: {engine.url}")
        
    except Exception as e:
        app_logger.error(f"数据库初始化失败: {e}")
        raise


if __name__ == "__main__":
    main()
