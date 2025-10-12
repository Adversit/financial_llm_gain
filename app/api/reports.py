"""报告相关的API路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import List
import json

from app.database import get_db
from app.models.daily_report import DailyReport
from app.models.article import Article
from app.models.summary import Summary
from app.schemas.report import (
    ReportResponse,
    ReportListResponse,
    ReportSummary,
    GenerateReportRequest,
    GenerateReportResponse
)
from app.schemas.article import ArticleWithSummary, ArticleListResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/", response_model=ReportListResponse)
def list_reports(
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """获取报告列表"""
    # 查询报告
    reports = db.query(DailyReport).order_by(
        DailyReport.report_date.desc()
    ).offset(skip).limit(limit).all()
    
    # 统计总数
    total = db.query(DailyReport).count()
    
    # 构建响应
    report_summaries = []
    for report in reports:
        # 统计各层面文章数
        articles = db.query(Article).filter(
            Article.publish_time >= report.report_date,
            Article.publish_time < report.report_date
        ).all()
        
        counts = {'政治': 0, '经济': 0, '技术': 0, '金融科技': 0}
        for article in articles:
            category = article.source.category
            if category in counts:
                counts[category] += 1
        
        report_summaries.append(ReportSummary(
            report_date=report.report_date,
            political_count=counts['政治'],
            economic_count=counts['经济'],
            technical_count=counts['技术'],
            fintech_count=counts['金融科技'],
            total_count=sum(counts.values())
        ))
    
    return ReportListResponse(total=total, reports=report_summaries)


@router.get("/{report_date}", response_model=ReportResponse)
def get_report(report_date: date, db: Session = Depends(get_db)):
    """获取指定日期的报告"""
    report = db.query(DailyReport).filter(
        DailyReport.report_date == report_date
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return report


@router.get("/articles/{report_date}/{category}", response_model=ArticleListResponse)
def get_articles_by_category(
    report_date: date,
    category: str,
    db: Session = Depends(get_db)
):
    """获取指定日期和层面的文章列表"""
    from datetime import datetime, timedelta
    
    # 验证层面
    valid_categories = ['政治', '经济', '技术', '金融科技']
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail="无效的层面")
    
    # 查询文章
    start_time = datetime.combine(report_date, datetime.min.time())
    end_time = start_time + timedelta(days=1)
    
    articles = db.query(Article).join(Article.source).filter(
        Article.publish_time >= start_time,
        Article.publish_time < end_time,
        Article.source.has(category=category)
    ).all()
    
    # 构建响应
    article_list = []
    for article in articles:
        # 获取摘要
        summary_obj = db.query(Summary).filter(
            Summary.article_id == article.id
        ).first()
        
        article_data = ArticleWithSummary(
            id=article.id,
            title=article.title,
            link=article.link,
            content=article.content,
            publish_time=article.publish_time,
            source_id=article.source_id,
            source_name=article.source.name,
            saved_at=article.saved_at,
            created_at=article.created_at,
            summary=summary_obj.summary if summary_obj else None,
            keywords=json.loads(summary_obj.keywords) if summary_obj and summary_obj.keywords else []
        )
        article_list.append(article_data)
    
    return ArticleListResponse(total=len(article_list), articles=article_list)


@router.get("/article/{article_id}", response_model=ArticleWithSummary)
def get_article_detail(article_id: int, db: Session = Depends(get_db)):
    """获取文章详情"""
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 获取摘要
    summary_obj = db.query(Summary).filter(
        Summary.article_id == article.id
    ).first()
    
    return ArticleWithSummary(
        id=article.id,
        title=article.title,
        link=article.link,
        content=article.content,
        publish_time=article.publish_time,
        source_id=article.source_id,
        source_name=article.source.name,
        saved_at=article.saved_at,
        created_at=article.created_at,
        summary=summary_obj.summary if summary_obj else None,
        keywords=json.loads(summary_obj.keywords) if summary_obj and summary_obj.keywords else []
    )


@router.post("/generate", response_model=GenerateReportResponse)
def generate_report(
    request: GenerateReportRequest,
    db: Session = Depends(get_db)
):
    """手动生成报告"""
    try:
        from app.scheduler.tasks import TaskScheduler
        from app.config import get_config
        
        config = get_config()
        
        # 创建调度器实例
        scheduler = TaskScheduler(
            rsshub_base_url=config['rsshub']['base_url'],
            ai_config=config['ai'],
            email_config=config['email']
        )
        
        # 执行流程
        scheduler.run_manual_pipeline(target_date=request.report_date)
        
        # 获取生成的报告
        report = db.query(DailyReport).filter(
            DailyReport.report_date == request.report_date
        ).first()
        
        return GenerateReportResponse(
            success=True,
            message="报告生成成功",
            report_id=report.id if report else None
        )
        
    except Exception as e:
        return GenerateReportResponse(
            success=False,
            message=f"报告生成失败: {str(e)}"
        )
