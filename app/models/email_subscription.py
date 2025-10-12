"""邮件订阅数据模型"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base


class EmailSubscription(Base):
    """邮件订阅模型"""
    __tablename__ = 'email_subscriptions'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), nullable=False, unique=True, comment="邮箱地址")
    enabled = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    def __repr__(self):
        return f"<EmailSubscription(id={self.id}, email='{self.email}', enabled={self.enabled})>"
