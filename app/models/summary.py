"""摘要数据模型"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import json


class Summary(Base):
    """摘要模型"""
    __tablename__ = 'summaries'
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False, unique=True, comment="文章ID")
    summary = Column(Text, nullable=False, comment="AI摘要（100-200字）")
    keywords = Column(Text, comment="关键词（JSON数组格式，包含word和type）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    article = relationship("Article", back_populates="summaries")
    
    def get_keywords_list(self):
        """获取关键词列表"""
        if not self.keywords:
            return []
        try:
            return json.loads(self.keywords)
        except:
            return []
    
    def get_keywords_by_type(self, keyword_type=None):
        """按类型获取关键词"""
        keywords = self.get_keywords_list()
        if keyword_type:
            return [kw for kw in keywords if kw.get('type') == keyword_type]
        return keywords
    
    def __repr__(self):
        return f"<Summary(id={self.id}, article_id={self.article_id})>"
