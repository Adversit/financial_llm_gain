"""每日报告数据模型"""
from sqlalchemy import Column, Integer, Text, Date, DateTime, String, Index
from datetime import datetime
from app.database import Base


class DailyReport(Base):
    """每日报告模型"""
    __tablename__ = 'daily_reports'
    
    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, nullable=False, unique=True, comment="报告日期")
    political_summary = Column(Text, comment="政治层面总结")
    economic_summary = Column(Text, comment="经济层面总结")
    technical_summary = Column(Text, comment="技术层面总结")
    fintech_summary = Column(Text, comment="金融科技层面总结")
    overall_summary = Column(Text, comment="总体总结")
    html_content = Column(Text, comment="HTML格式报告")
    pdf_path = Column(String(500), comment="PDF文件路径")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 索引
    __table_args__ = (
        Index('idx_report_date', 'report_date'),
    )
    
    def __repr__(self):
        return f"<DailyReport(id={self.id}, report_date={self.report_date})>"
