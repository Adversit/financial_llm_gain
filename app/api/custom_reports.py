"""个性化报告相关的API路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.custom_report import CustomReportConfig, CustomReportResponse

router = APIRouter(prefix="/custom-reports", tags=["custom-reports"])


@router.post("/", response_model=CustomReportResponse)
def create_custom_report(
    config: CustomReportConfig,
    db: Session = Depends(get_db)
):
    """生成个性化报告"""
    try:
        from app.services.report_service import ReportGenerator
        from app.services.ai_service import AIService
        from app.models.article import Article
        from app.models.summary import Summary
        from app.config import get_config
        from datetime import datetime, timedelta
        import json
        
        app_config = get_config()
        
        # 创建AI服务
        ai_service = AIService(
            provider=app_config['ai']['provider'],
            api_key=app_config['ai']['api_key'],
            base_url=app_config['ai']['base_url'],
            model=app_config['ai']['model'],
            timeout=app_config['ai'].get('timeout', 120),
            max_retries=app_config['ai'].get('max_retries', 3)
        )
        
        # 创建报告生成器
        report_generator = ReportGenerator(
            db=db,
            ai_service=ai_service
        )
        
        # 查询选中信息源的文章
        start_time = datetime.combine(config.report_date, datetime.min.time())
        end_time = start_time + timedelta(days=1)
        
        articles = db.query(Article).filter(
            Article.source_id.in_(config.selected_sources),
            Article.publish_time >= start_time,
            Article.publish_time < end_time
        ).all()
        
        if not articles:
            return CustomReportResponse(
                success=False,
                message="没有找到符合条件的文章"
            )
        
        # 按层面分组
        categories = {
            '政治': {'articles': [], 'summary': ''},
            '经济': {'articles': [], 'summary': ''},
            '技术': {'articles': [], 'summary': ''},
            '金融科技': {'articles': [], 'summary': ''}
        }
        
        for article in articles:
            category = article.source.category
            if category in categories:
                # 获取摘要
                summary_obj = db.query(Summary).filter(
                    Summary.article_id == article.id
                ).first()
                
                article_data = {
                    'title': article.title,
                    'link': article.link,
                    'source': article.source.name,
                    'publish_time': article.publish_time.strftime('%Y-%m-%d %H:%M') if article.publish_time else '',
                    'summary': summary_obj.summary if summary_obj else '',
                    'keywords': json.loads(summary_obj.keywords) if summary_obj and summary_obj.keywords else []
                }
                
                categories[category]['articles'].append(article_data)
        
        # 生成报告
        report_data = {'categories': categories}
        
        # 使用自定义提示词生成总结（如果提供）
        if config.report_prompt and ai_service:
            # TODO: 使用自定义提示词
            pass
        
        # 生成HTML
        html_content = report_generator.generate_html(
            report_data=report_data,
            report_date=config.report_date,
            overall_summary="个性化报告"
        )
        
        # 生成 PDF（后台生成，但前端暂不显示）
        pdf_path = ""
        try:
            report_data_with_summary = {
                'categories': report_data['categories'],
                'overall_summary': "个性化报告"
            }
            pdf_path = report_generator.generate_pdf(
                html_content=html_content,
                report_date=config.report_date,
                report_data=report_data_with_summary
            )
        except Exception as e:
            # PDF 生成失败不影响主流程
            pass
        
        return CustomReportResponse(
            success=True,
            message="个性化报告生成成功",
            html_content=html_content,
            pdf_path=""  # 前端暂不显示 PDF 路径
        )
        
    except Exception as e:
        return CustomReportResponse(
            success=False,
            message=f"报告生成失败: {str(e)}"
        )
