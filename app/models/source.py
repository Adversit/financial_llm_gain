"""信息源数据模型"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Source(Base):
    """信息源模型"""
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, comment="信息源名称")
    category = Column(String(50), nullable=False, comment="层面：政治/经济/技术/金融科技")
    type = Column(String(20), nullable=False, comment="类型：rss/rsshub/custom")
    url = Column(Text, comment="RSS地址或网站地址")
    rsshub_route = Column(String(200), comment="RSSHub路由")
    crawler_class = Column(String(100), comment="自定义爬虫类名")
    enabled = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', category='{self.category}', type='{self.type}')>"
