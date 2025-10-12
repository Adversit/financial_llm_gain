"""数据库连接和配置"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from pathlib import Path

# 从环境变量获取数据库URL，默认使用SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/financial_daily.db")

# 确保数据目录存在
if DATABASE_URL.startswith("sqlite"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,  # 设置为True可以看到SQL语句
    pool_pre_ping=True,  # 连接池预检查
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于FastAPI的依赖注入
    
    Yields:
        数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库，创建所有表
    """
    from app.models import source, article, summary, daily_report, email_subscription, user_config
    Base.metadata.create_all(bind=engine)
