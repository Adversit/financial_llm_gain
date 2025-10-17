"""
词云API
"""
from datetime import datetime, date
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
import os

from app.services.wordcloud_service import wordcloud_service


router = APIRouter(prefix="/wordcloud", tags=["wordcloud"])


@router.get("/generate")
def generate_wordcloud(
    date: str = Query(..., description="日期 (YYYY-MM-DD)"),
    keyword_type: Optional[str] = Query(None, description="关键词类型"),
    category: Optional[str] = Query(None, description="文章类别")
):
    """
    生成词云
    
    - **date**: 日期
    - **keyword_type**: 关键词类型（可选）
    - **category**: 文章类别（可选）
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYY-MM-DD")
    
    # 生成词云
    wordcloud_path = wordcloud_service.generate_wordcloud_from_keywords(
        target_date,
        keyword_type=keyword_type,
        category=category
    )
    
    if not wordcloud_path:
        raise HTTPException(status_code=404, detail="无法生成词云，可能没有数据")
    
    return {
        "success": True,
        "path": wordcloud_path.replace('\\', '/'),
        "url": f"/wordcloud/image?date={date}" + 
               (f"&keyword_type={keyword_type}" if keyword_type else "") +
               (f"&category={category}" if category else "")
    }


@router.get("/image")
def get_wordcloud_image(
    date: str = Query(..., description="日期 (YYYY-MM-DD)"),
    keyword_type: Optional[str] = Query(None, description="关键词类型"),
    category: Optional[str] = Query(None, description="文章类别")
):
    """
    获取词云图片
    
    - **date**: 日期
    - **keyword_type**: 关键词类型（可选）
    - **category**: 文章类别（可选）
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYY-MM-DD")
    
    # 检查词云是否存在
    wordcloud_path = wordcloud_service.get_wordcloud_path(
        target_date,
        keyword_type=keyword_type,
        category=category
    )
    
    # 如果不存在，尝试生成
    if not wordcloud_path:
        wordcloud_path = wordcloud_service.generate_wordcloud_from_keywords(
            target_date,
            keyword_type=keyword_type,
            category=category
        )
    
    if not wordcloud_path or not os.path.exists(wordcloud_path):
        raise HTTPException(status_code=404, detail="词云不存在")
    
    return FileResponse(
        wordcloud_path,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"}  # 缓存1天
    )


@router.get("/list")
def list_wordclouds(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)")
):
    """
    列出可用的词云
    
    - **date**: 日期（可选，如果提供则只列出该日期的词云）
    """
    wordclouds = []
    
    for filename in os.listdir(wordcloud_service.output_dir):
        if filename.endswith('.png'):
            try:
                # 解析文件名
                parts = filename.replace('.png', '').split('_')
                file_date = datetime.strptime(parts[0], '%Y%m%d').date()
                
                # 日期筛选
                if date:
                    target_date = datetime.strptime(date, "%Y-%m-%d").date()
                    if file_date != target_date:
                        continue
                
                # 提取类别和类型
                category = parts[1] if len(parts) > 1 and parts[1] in ['政治', '经济', '技术', '金融科技'] else None
                keyword_type = parts[1] if len(parts) > 1 and category is None else (parts[2] if len(parts) > 2 else None)
                
                wordclouds.append({
                    'date': file_date.strftime('%Y-%m-%d'),
                    'category': category,
                    'keyword_type': keyword_type,
                    'filename': filename,
                    'url': f"/wordcloud/image?date={file_date.strftime('%Y-%m-%d')}" +
                           (f"&category={category}" if category else "") +
                           (f"&keyword_type={keyword_type}" if keyword_type else "")
                })
            except:
                pass
    
    # 按日期排序
    wordclouds.sort(key=lambda x: x['date'], reverse=True)
    
    return {
        "wordclouds": wordclouds,
        "total": len(wordclouds)
    }


@router.post("/cleanup")
def cleanup_old_wordclouds(
    days: int = Query(30, ge=1, le=365, description="保留最近多少天的词云")
):
    """
    清理旧的词云
    
    - **days**: 保留最近多少天的词云（默认30天）
    """
    try:
        wordcloud_service.cleanup_old_wordclouds(days)
        return {"success": True, "message": f"已清理 {days} 天前的词云"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")
