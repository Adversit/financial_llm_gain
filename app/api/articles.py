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
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    keyword_type: Optional[str] = Query(None, description="关键词类型"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    获取文章列表
    
    - **date**: 筛选日期
    - **category**: 筛选层面
    - **source_id**: 筛选信息源
    - **keyword**: 关键词搜索
    - **keyword_type**: 关键词类型（如"公司"、"行业"等）
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
            target_date = datetime.strptime(date, "%Y-%m-d").date()
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
    
    # 关键词筛选
    if keyword or keyword_type:
        query = query.join(Article.summaries)
        if keyword and keyword_type:
            # 同时筛选关键词和类型
            query = query.filter(Summary.keywords.like(f'%"word": "{keyword}"%'))
            query = query.filter(Summary.keywords.like(f'%"type": "{keyword_type}"%'))
        elif keyword:
            # 只筛选关键词
            query = query.filter(Summary.keywords.like(f'%{keyword}%'))
        elif keyword_type:
            # 只筛选类型
            query = query.filter(Summary.keywords.like(f'%"type": "{keyword_type}"%'))
    
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


@router.get("/keywords/all")
def get_all_keywords(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    获取所有关键词及其类型
    
    - **date**: 筛选日期
    """
    import json
    from collections import defaultdict
    
    query = db.query(Summary).join(Summary.article)
    
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
    
    summaries = query.all()
    
    # 统计关键词
    keyword_stats = defaultdict(lambda: {"count": 0, "types": set()})
    keyword_types = set()
    
    for summary in summaries:
        if summary.keywords:
            try:
                keywords = json.loads(summary.keywords)
                for kw in keywords:
                    word = kw.get('word', '')
                    kw_type = kw.get('type', '')
                    if word:
                        keyword_stats[word]["count"] += 1
                        if kw_type:
                            keyword_stats[word]["types"].add(kw_type)
                            keyword_types.add(kw_type)
            except:
                pass
    
    # 转换为列表
    keywords_list = [
        {
            "word": word,
            "count": stats["count"],
            "types": list(stats["types"])
        }
        for word, stats in keyword_stats.items()
    ]
    
    # 按出现次数排序
    keywords_list.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "keywords": keywords_list,
        "keyword_types": sorted(list(keyword_types)),
        "total": len(keywords_list)
    }


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
