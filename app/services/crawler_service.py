"""爬虫服务 - 协调爬虫执行和数据保存"""
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.crawlers.factory import CrawlerFactory
from app.crawlers.base import Article
from app.services.cleaner_service import DataCleaner
from app.models.source import Source
from app.models.article import Article as ArticleModel
from app.models.summary import Summary
from app.utils.logger import crawler_logger


class CrawlerService:
    """爬虫服务 - 管理所有信息源的爬取"""
    
    def __init__(self, db: Session, rsshub_base_url: str, ai_service=None):
        """
        初始化爬虫服务
        
        Args:
            db: 数据库会话
            rsshub_base_url: RSSHub基础URL
            ai_service: AI服务实例（可选）
        """
        self.db = db
        self.rsshub_base_url = rsshub_base_url
        self.ai_service = ai_service
        self.cleaner = DataCleaner()
        self.logger = crawler_logger
    
    def fetch_all_sources(
        self,
        target_date: date = None,
        max_workers: int = 5,
        filter_relevance: bool = True,
        generate_summaries: bool = True
    ) -> Dict[str, List[ArticleModel]]:
        """
        批量爬取所有启用的信息源
        
        Args:
            target_date: 目标日期，默认为昨天
            max_workers: 最大并发爬虫数
            filter_relevance: 是否过滤相关性
            generate_summaries: 是否生成AI摘要
        
        Returns:
            按层面分组的文章字典
        """
        self.logger.info("开始批量爬取所有信息源")
        
        # 获取所有启用的信息源
        sources = self.db.query(Source).filter(Source.enabled == True).all()
        
        if not sources:
            self.logger.warning("没有启用的信息源")
            return {}
        
        self.logger.info(f"找到 {len(sources)} 个启用的信息源")
        
        # 并发爬取
        all_articles = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_source = {
                executor.submit(self._fetch_single_source, source): source
                for source in sources
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                except Exception as e:
                    self.logger.error(f"爬取信息源 [{source.name}] 失败: {e}")
        
        self.logger.info(f"爬取完成，共获取 {len(all_articles)} 篇文章")
        
        # 数据清洗
        cleaned_articles = self.cleaner.clean_all(
            all_articles,
            target_date=target_date,
            filter_relevance=filter_relevance
        )
        
        # 保存到数据库
        saved_articles = self._save_articles(cleaned_articles)
        
        # 生成AI摘要
        if generate_summaries and self.ai_service:
            self._generate_summaries(saved_articles)
        
        # 按层面分组
        grouped = self._group_by_category(saved_articles)
        
        return grouped
    
    def fetch_single_source_by_id(self, source_id: int) -> List[ArticleModel]:
        """
        爬取单个信息源（通过ID）
        
        Args:
            source_id: 信息源ID
        
        Returns:
            文章列表
        """
        source = self.db.query(Source).filter(Source.id == source_id).first()
        
        if not source:
            raise ValueError(f"信息源不存在: {source_id}")
        
        if not source.enabled:
            self.logger.warning(f"信息源已禁用: {source.name}")
            return []
        
        articles = self._fetch_single_source(source)
        saved_articles = self._save_articles(articles)
        
        return saved_articles
    
    def _fetch_single_source(self, source: Source) -> List[Article]:
        """
        爬取单个信息源
        
        Args:
            source: 信息源对象
        
        Returns:
            文章列表
        """
        try:
            self.logger.info(f"开始爬取: [{source.name}] ({source.type})")
            
            # 创建爬虫实例
            crawler = CrawlerFactory.create_crawler(
                source_type=source.type,
                source_name=source.name,
                url=source.url,
                rsshub_base=self.rsshub_base_url,
                rsshub_route=source.rsshub_route,
                crawler_class=source.crawler_class
            )
            
            # 执行爬取
            articles = crawler.fetch()
            
            # 为每篇文章设置source_id
            for article in articles:
                article.source_name = source.name
            
            self.logger.info(f"[{source.name}] 爬取成功: {len(articles)} 篇")
            
            return articles
            
        except Exception as e:
            self.logger.error(f"[{source.name}] 爬取失败: {e}")
            return []
    
    def _save_articles(self, articles: List[Article]) -> List[ArticleModel]:
        """
        保存文章到数据库
        
        Args:
            articles: 文章列表
        
        Returns:
            保存的文章模型列表
        """
        saved_articles = []
        
        for article in articles:
            try:
                # 查找信息源
                source = self.db.query(Source).filter(
                    Source.name == article.source_name
                ).first()
                
                if not source:
                    self.logger.warning(f"找不到信息源: {article.source_name}")
                    continue
                
                # 检查文章是否已存在（通过链接）
                existing = self.db.query(ArticleModel).filter(
                    ArticleModel.link == article.link
                ).first()
                
                if existing:
                    self.logger.debug(f"文章已存在: {article.title[:50]}")
                    saved_articles.append(existing)
                    continue
                
                # 创建新文章
                article_model = ArticleModel(
                    source_id=source.id,
                    title=article.title,
                    link=article.link,
                    content=article.content,
                    publish_time=article.publish_time,
                    saved_at=datetime.utcnow()
                )
                
                self.db.add(article_model)
                self.db.commit()
                self.db.refresh(article_model)
                
                saved_articles.append(article_model)
                
            except IntegrityError as e:
                self.db.rollback()
                self.logger.debug(f"文章已存在（唯一约束）: {article.link}")
            except Exception as e:
                self.db.rollback()
                self.logger.error(f"保存文章失败: {e}")
        
        self.logger.info(f"成功保存 {len(saved_articles)} 篇文章到数据库")
        
        return saved_articles
    
    def _group_by_category(
        self,
        articles: List[ArticleModel]
    ) -> Dict[str, List[ArticleModel]]:
        """
        按层面分组文章
        
        Args:
            articles: 文章列表
        
        Returns:
            按层面分组的字典
        """
        grouped = {
            '政治': [],
            '经济': [],
            '技术': [],
            '金融科技': []
        }
        
        for article in articles:
            category = article.source.category
            if category in grouped:
                grouped[category].append(article)
        
        # 记录统计
        for category, items in grouped.items():
            self.logger.info(f"{category}层面: {len(items)} 篇文章")
        
        return grouped
    
    def test_source(
        self,
        source_type: str,
        url: Optional[str] = None,
        rsshub_route: Optional[str] = None,
        crawler_class: Optional[str] = None
    ) -> Dict[str, any]:
        """
        测试信息源是否可用
        
        Args:
            source_type: 爬虫类型
            url: URL地址
            rsshub_route: RSSHub路由
            crawler_class: 自定义爬虫类名
        
        Returns:
            测试结果字典
        """
        result = {
            'success': False,
            'message': '',
            'article_count': 0,
            'sample_titles': []
        }
        
        try:
            # 创建爬虫
            crawler = CrawlerFactory.create_crawler(
                source_type=source_type,
                source_name='测试',
                url=url,
                rsshub_base=self.rsshub_base_url,
                rsshub_route=rsshub_route,
                crawler_class=crawler_class
            )
            
            # 执行爬取
            articles = crawler.fetch()
            
            result['success'] = True
            result['article_count'] = len(articles)
            result['sample_titles'] = [
                article.title[:50] for article in articles[:3]
            ]
            result['message'] = f"测试成功，获取到 {len(articles)} 篇文章"
            
        except Exception as e:
            result['message'] = f"测试失败: {str(e)}"
        
        return result
    
    def _generate_summaries(self, articles: List[ArticleModel]):
        """
        为文章生成AI摘要
        
        Args:
            articles: 文章列表
        """
        self.logger.info(f"开始为 {len(articles)} 篇文章生成摘要")
        
        for article in articles:
            try:
                # 检查是否已有摘要
                existing_summary = self.db.query(Summary).filter(
                    Summary.article_id == article.id
                ).first()
                
                if existing_summary:
                    self.logger.debug(f"文章已有摘要: {article.title[:50]}")
                    continue
                
                # 生成摘要
                result = self.ai_service.summarize_article(
                    title=article.title,
                    content=article.content
                )
                
                # 保存摘要
                summary = Summary(
                    article_id=article.id,
                    summary=result['summary'],
                    keywords=json.dumps(result['keywords'], ensure_ascii=False)
                )
                
                self.db.add(summary)
                self.db.commit()
                
                self.logger.info(f"成功生成摘要: {article.title[:30]}...")
                
            except Exception as e:
                self.db.rollback()
                self.logger.error(f"生成摘要失败 [{article.title[:30]}]: {e}")
        
        self.logger.info("摘要生成完成")
