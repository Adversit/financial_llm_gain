"""通用的Pydantic模式"""
from pydantic import BaseModel


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str


class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool
    message: str


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: str = ""
