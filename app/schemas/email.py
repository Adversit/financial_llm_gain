"""邮件相关的Pydantic模式"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class EmailSubscriptionBase(BaseModel):
    """邮件订阅基础模式"""
    email: EmailStr = Field(..., description="邮箱地址")
    enabled: bool = Field(True, description="是否启用")


class EmailSubscriptionCreate(BaseModel):
    """创建邮件订阅"""
    email: EmailStr


class EmailSubscriptionUpdate(BaseModel):
    """更新邮件订阅"""
    enabled: bool


class EmailSubscriptionResponse(EmailSubscriptionBase):
    """邮件订阅响应"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmailTestRequest(BaseModel):
    """测试邮件请求"""
    email: EmailStr = Field(..., description="测试邮箱地址")


class EmailTestResponse(BaseModel):
    """测试邮件响应"""
    success: bool
    message: str
