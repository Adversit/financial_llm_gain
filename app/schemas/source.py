"""信息源相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SourceBase(BaseModel):
    """信息源基础模式"""
    name: str = Field(..., description="信息源名称")
    category: str = Field(..., description="层面：政治/经济/技术/金融科技")
    type: str = Field(..., description="类型：rss/rsshub/custom")
    url: Optional[str] = Field(None, description="RSS地址或网站地址")
    rsshub_route: Optional[str] = Field(None, description="RSSHub路由")
    crawler_class: Optional[str] = Field(None, description="自定义爬虫类名")
    enabled: bool = Field(True, description="是否启用")


class SourceCreate(SourceBase):
    """创建信息源"""
    pass


class SourceUpdate(BaseModel):
    """更新信息源"""
    name: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    rsshub_route: Optional[str] = None
    crawler_class: Optional[str] = None
    enabled: Optional[bool] = None


class SourceResponse(SourceBase):
    """信息源响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SourceTestRequest(BaseModel):
    """测试信息源请求"""
    type: str = Field(..., description="类型：rss/rsshub/custom")
    url: Optional[str] = Field(None, description="RSS地址或网站地址")
    rsshub_route: Optional[str] = Field(None, description="RSSHub路由")
    crawler_class: Optional[str] = Field(None, description="自定义爬虫类名")


class SourceTestResponse(BaseModel):
    """测试信息源响应"""
    success: bool
    message: str
    article_count: int = 0
    sample_titles: list[str] = []
