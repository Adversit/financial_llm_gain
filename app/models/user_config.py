"""用户配置数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base


class UserConfig(Base):
    """用户配置模型"""
    __tablename__ = 'user_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, unique=True, comment="用户标识（预留）")
    selected_sources = Column(Text, comment="选中的信息源ID（JSON数组）")
    article_prompt = Column(Text, comment="单篇文章摘要提示词")
    report_prompt = Column(Text, comment="每日报告提示词")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    def __repr__(self):
        return f"<UserConfig(id={self.id}, user_id='{self.user_id}')>"
