"""报告数据聚合模块"""
import json
from datetime import datetime, date
from typing import Dict
from sqlalchemy.orm import Session, joinedload

from app.models.article import Article
from app.models.summary import Summary
from app.utils.logger import app_logger


class ReportAggregator:
    """报告数据聚合器"""
    
    def __init__(self, db: Session):
        """
        初始化聚合器
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.logger = app_logger
    
    def aggregate_report_data(self, report_date: date) -> Dict:
        """
        聚合报告数据
        
        Args:
            report_date: 报告日期
        
        Returns:
            报告数据字典
        """
        self.logger.info(f"聚合 {report_date} 的数据")
        
        # 查询指定日期的所有文章，预加载关系
        articles = self.db.query(Article).options(
            joinedload(Article.source)
        ).filter(
            Article.publish_time >= datetime.combine(report_date, datetime.min.time()),
            Article.publish_time < datetime.combine(report_date, datetime.max.time())
        ).all()
        
        self.logger.info(f"找到 {len(articles)} 篇文章")
        
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
                summary_obj = self.db.query(Summary).filter(
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
        
        # 统计
        for category, data in categories.items():
            self.logger.info(f"{category}层面: {len(data['articles'])} 篇文章")
        
        return {'categories': categories}
