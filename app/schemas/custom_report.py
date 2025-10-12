"""个性化报告相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class CustomReportConfig(BaseModel):
    """个性化报告配置"""
    report_date: date = Field(..., description="报告日期")
    selected_sources: list[int] = Field(..., description="选中的信息源ID列表")
    article_prompt: Optional[str] = Field(None, description="自定义文章摘要提示词")
    report_prompt: Optional[str] = Field(None, description="自定义报告提示词")


class CustomReportResponse(BaseModel):
    """个性化报告响应"""
    success: bool
    message: str
    html_content: Optional[str] = None
    pdf_path: Optional[str] = None
