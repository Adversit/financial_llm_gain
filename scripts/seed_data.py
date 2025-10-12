"""数据库种子数据脚本 - 填充初始信息源"""
import sys
from pathlib import Path
import yaml

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models.source import Source
from app.utils.logger import app_logger


def load_config():
    """加载配置文件"""
    config_path = project_root / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def seed_sources(db, config):
    """填充信息源数据"""
    sources_config = config.get('sources', {})
    
    # 处理RSS源
    for source_data in sources_config.get('rss', []):
        source = Source(
            name=source_data['name'],
            category=source_data['category'],
            type='rss',
            url=source_data['url'],
            enabled=source_data.get('enabled', True)
        )
        db.add(source)
        app_logger.info(f"添加RSS源: {source.name}")
    
    # 处理RSSHub源
    for source_data in sources_config.get('rsshub', []):
        source = Source(
            name=source_data['name'],
            category=source_data['category'],
            type='rsshub',
            rsshub_route=source_data['route'],
            enabled=source_data.get('enabled', True)
        )
        db.add(source)
        app_logger.info(f"添加RSSHub源: {source.name}")
    
    # 处理自定义爬虫源
    for source_data in sources_config.get('custom', []):
        source = Source(
            name=source_data['name'],
            category=source_data['category'],
            type='custom',
            url=source_data['url'],
            crawler_class=source_data['crawler_class'],
            enabled=source_data.get('enabled', True)
        )
        db.add(source)
        app_logger.info(f"添加自定义爬虫源: {source.name}")
    
    db.commit()


def main():
    """主函数"""
    try:
        app_logger.info("开始填充种子数据...")
        
        # 加载配置
        config = load_config()
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 检查是否已有数据
            existing_count = db.query(Source).count()
            if existing_count > 0:
                app_logger.warning(f"数据库中已有 {existing_count} 个信息源")
                response = input("是否清空现有数据并重新填充？(y/N): ")
                if response.lower() == 'y':
                    db.query(Source).delete()
                    db.commit()
                    app_logger.info("已清空现有信息源数据")
                else:
                    app_logger.info("取消操作")
                    return
            
            # 填充信息源
            seed_sources(db, config)
            
            # 统计
            total_count = db.query(Source).count()
            app_logger.info(f"种子数据填充完成！共添加 {total_count} 个信息源")
            
        finally:
            db.close()
            
    except Exception as e:
        app_logger.error(f"填充种子数据失败: {e}")
        raise


if __name__ == "__main__":
    main()
