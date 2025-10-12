"""摘要数据模型"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Summary(Base):
    """摘要模型"""
    __tablename__ = 'summaries'
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False, unique=True, comment="文章ID")
    summary = Column(Text, nullable=False, comment="AI摘要（100-200字）")
    keywords = Column(Text, comment="关键词（JSON数组格式）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    article = relationship("Article", back_populates="summaries")
    
    def __repr__(self):
        return f"<Summary(id={self.id}, article_id={self.article_id})>"
