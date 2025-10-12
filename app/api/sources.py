"""信息源相关的API路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.source import Source
from app.schemas.source import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceTestRequest,
    SourceTestResponse
)
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/", response_model=List[SourceResponse])
def list_sources(
    category: str = None,
    enabled: bool = None,
    db: Session = Depends(get_db)
):
    """获取所有信息源列表"""
    query = db.query(Source)
    
    if category:
        query = query.filter(Source.category == category)
    if enabled is not None:
        query = query.filter(Source.enabled == enabled)
    
    sources = query.all()
    return sources


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: int, db: Session = Depends(get_db)):
    """获取单个信息源"""
    source = db.query(Source).filter(Source.id == source_id).first()
    
    if not source:
        raise HTTPException(status_code=404, detail="信息源不存在")
    
    return source


@router.post("/", response_model=SourceResponse)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    """添加新信息源"""
    # 检查名称是否已存在
    existing = db.query(Source).filter(Source.name == source.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="信息源名称已存在")
    
    # 创建信息源
    db_source = Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    
    return db_source


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: int,
    source_update: SourceUpdate,
    db: Session = Depends(get_db)
):
    """更新信息源"""
    source = db.query(Source).filter(Source.id == source_id).first()
    
    if not source:
        raise HTTPException(status_code=404, detail="信息源不存在")
    
    # 更新字段
    update_data = source_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)
    
    db.commit()
    db.refresh(source)
    
    return source


@router.post("/{source_id}/toggle", response_model=SourceResponse)
def toggle_source(source_id: int, db: Session = Depends(get_db)):
    """启用/停用信息源"""
    source = db.query(Source).filter(Source.id == source_id).first()
    
    if not source:
        raise HTTPException(status_code=404, detail="信息源不存在")
    
    source.enabled = not source.enabled
    db.commit()
    db.refresh(source)
    
    return source


@router.delete("/{source_id}", response_model=SuccessResponse)
def delete_source(source_id: int, db: Session = Depends(get_db)):
    """删除信息源"""
    source = db.query(Source).filter(Source.id == source_id).first()
    
    if not source:
        raise HTTPException(status_code=404, detail="信息源不存在")
    
    db.delete(source)
    db.commit()
    
    return SuccessResponse(success=True, message="信息源已删除")


@router.post("/test", response_model=SourceTestResponse)
def test_source(request: SourceTestRequest, db: Session = Depends(get_db)):
    """测试信息源可用性"""
    try:
        from app.services.crawler_service import CrawlerService
        from app.config import get_config
        
        config = get_config()
        
        crawler_service = CrawlerService(
            db=db,
            rsshub_base_url=config['rsshub']['base_url']
        )
        
        result = crawler_service.test_source(
            source_type=request.type,
            url=request.url,
            rsshub_route=request.rsshub_route,
            crawler_class=request.crawler_class
        )
        
        return SourceTestResponse(**result)
        
    except Exception as e:
        return SourceTestResponse(
            success=False,
            message=f"测试失败: {str(e)}",
            article_count=0,
            sample_titles=[]
        )
