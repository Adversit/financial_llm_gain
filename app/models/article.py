"""文章数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Article(Base):
    """文章模型"""
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False, comment="信息源ID")
    title = Column(Text, nullable=False, comment="标题")
    link = Column(Text, nullable=False, unique=True, comment="链接")
    content = Column(Text, comment="原始内容")
    publish_time = Column(DateTime, comment="发布时间")
    saved_at = Column(DateTime, default=datetime.utcnow, comment="保存时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    source = relationship("Source", back_populates="articles")
    summaries = relationship("Summary", back_populates="article", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_publish_time', 'publish_time'),
        Index('idx_source_id', 'source_id'),
    )
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:30]}...', source_id={self.source_id})>"
