"""文章管理API"""
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
import csv
import io

from app.database import get_db
from app.models.article import Article
from app.models.summary import Summary


router = APIRouter(prefix="/articles", tags=["articles"])


class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: int
    title: str
    link: str
    content: Optional[str]
    publish_time: Optional[datetime]
    source_name: str
    source_category: str
    summary: Optional[str]
    keywords: Optional[str]
    saved_at: datetime
    
    class Config:
        from_attributes = True


class ArticlesListResponse(BaseModel):
    """文章列表响应"""
    articles: List[ArticleResponse]
    total: int


@router.get("/", response_model=ArticlesListResponse)
def get_articles(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="层面"),
    source_id: Optional[int] = Query(None, description="信息源ID"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    获取文章列表
    
    - **date**: 筛选日期
    - **category**: 筛选层面
    - **source_id**: 筛选信息源
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    """
    query = db.query(Article).options(
        joinedload(Article.source),
        joinedload(Article.summaries)
    )
    
    # 日期筛选
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(
                Article.publish_time >= datetime.combine(target_date, datetime.min.time()),
                Article.publish_time < datetime.combine(target_date, datetime.max.time())
            )
        except ValueError:
            pass
    
    # 层面筛选
    if category:
        query = query.join(Article.source).filter(Article.source.has(category=category))
    
    # 信息源筛选
    if source_id:
        query = query.filter(Article.source_id == source_id)
    
    # 排序
    query = query.order_by(Article.publish_time.desc())
    
    # 总数
    total = query.count()
    
    # 分页
    articles = query.offset(offset).limit(limit).all()
    
    # 构建响应
    article_responses = []
    for article in articles:
        summary_obj = article.summaries[0] if article.summaries else None
        
        article_responses.append(ArticleResponse(
            id=article.id,
            title=article.title,
            link=article.link,
            content=article.content,
            publish_time=article.publish_time,
            source_name=article.source.name,
            source_category=article.source.category,
            summary=summary_obj.summary if summary_obj else None,
            keywords=summary_obj.keywords if summary_obj else None,
            saved_at=article.saved_at
        ))
    
    return ArticlesListResponse(
        articles=article_responses,
        total=total
    )


@router.get("/export")
def export_articles(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="层面"),
    format: str = Query("csv", description="导出格式: csv, json"),
    db: Session = Depends(get_db)
):
    """
    导出文章数据
    
    - **date**: 筛选日期
    - **category**: 筛选层面
    - **format**: 导出格式 (csv 或 json)
    """
    query = db.query(Article).options(
        joinedload(Article.source),
        joinedload(Article.summaries)
    )
    
    # 日期筛选
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(
                Article.publish_time >= datetime.combine(target_date, datetime.min.time()),
                Article.publish_time < datetime.combine(target_date, datetime.max.time())
            )
        except ValueError:
            pass
    
    # 层面筛选
    if category:
        query = query.join(Article.source).filter(Article.source.has(category=category))
    
    # 排序
    query = query.order_by(Article.publish_time.desc())
    
    articles = query.all()
    
    if format == "csv":
        # CSV 导出
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow([
            'ID', '标题', '链接', '信息源', '层面', 
            '发布时间', '摘要', '关键词', '保存时间'
        ])
        
        # 写入数据
        for article in articles:
            summary_obj = article.summaries[0] if article.summaries else None
            writer.writerow([
                article.id,
                article.title,
                article.link,
                article.source.name,
                article.source.category,
                article.publish_time.strftime('%Y-%m-%d %H:%M:%S') if article.publish_time else '',
                summary_obj.summary if summary_obj else '',
                summary_obj.keywords if summary_obj else '',
                article.saved_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # 返回 CSV
        filename = f"articles_{date or 'all'}.csv"
        return Response(
            content=output.getvalue().encode('utf-8-sig'),  # 使用 UTF-8 BOM 以便 Excel 正确识别
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    else:
        # JSON 导出
        article_list = []
        for article in articles:
            summary_obj = article.summaries[0] if article.summaries else None
            article_list.append({
                'id': article.id,
                'title': article.title,
                'link': article.link,
                'source_name': article.source.name,
                'source_category': article.source.category,
                'publish_time': article.publish_time.isoformat() if article.publish_time else None,
                'summary': summary_obj.summary if summary_obj else None,
                'keywords': summary_obj.keywords if summary_obj else None,
                'saved_at': article.saved_at.isoformat()
            })
        
        import json
        filename = f"articles_{date or 'all'}.json"
        return Response(
            content=json.dumps(article_list, ensure_ascii=False, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """获取单篇文章详情"""
    article = db.query(Article).options(
        joinedload(Article.source),
        joinedload(Article.summaries)
    ).filter(Article.id == article_id).first()
    
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="文章不存在")
    
    summary_obj = article.summaries[0] if article.summaries else None
    
    return ArticleResponse(
        id=article.id,
        title=article.title,
        link=article.link,
        content=article.content,
        publish_time=article.publish_time,
        source_name=article.source.name,
        source_category=article.source.category,
        summary=summary_obj.summary if summary_obj else None,
        keywords=summary_obj.keywords if summary_obj else None,
        saved_at=article.saved_at
    )
