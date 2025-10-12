"""文章相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ArticleBase(BaseModel):
    """文章基础模式"""
    title: str
    link: str
    content: str
    publish_time: Optional[datetime] = None


class ArticleResponse(ArticleBase):
    """文章响应"""
    id: int
    source_id: int
    source_name: str = Field(..., description="信息源名称")
    saved_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ArticleWithSummary(ArticleResponse):
    """带摘要的文章响应"""
    summary: Optional[str] = None
    keywords: list[str] = []


class ArticleListResponse(BaseModel):
    """文章列表响应"""
    total: int
    articles: list[ArticleWithSummary]
