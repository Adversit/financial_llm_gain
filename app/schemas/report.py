"""报告相关的Pydantic模式"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class ReportSummary(BaseModel):
    """报告摘要"""
    report_date: date
    political_count: int = 0
    economic_count: int = 0
    technical_count: int = 0
    fintech_count: int = 0
    total_count: int = 0


class ReportResponse(BaseModel):
    """报告响应"""
    id: int
    report_date: date
    political_summary: Optional[str] = None
    economic_summary: Optional[str] = None
    technical_summary: Optional[str] = None
    fintech_summary: Optional[str] = None
    overall_summary: Optional[str] = None
    html_content: Optional[str] = None
    pdf_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """报告列表响应"""
    total: int
    reports: list[ReportSummary]


class GenerateReportRequest(BaseModel):
    """生成报告请求"""
    report_date: date = Field(..., description="报告日期")
    generate_summaries: bool = Field(True, description="是否生成AI摘要")


class GenerateReportResponse(BaseModel):
    """生成报告响应"""
    success: bool
    message: str
    report_id: Optional[int] = None
