"""数据清洗服务"""
from datetime import datetime, date, timedelta
from typing import List
from app.crawlers.base import Article
from app.utils.logger import app_logger


class DataCleaner:
    """数据清洗器 - 负责过滤和清洗文章数据"""
    
    # 金融相关关键词（用于内容相关性过滤）
    FINANCE_KEYWORDS = [
        '金融', '经济', '投资', '股票', '证券', '基金', '银行', '保险',
        '财经', '市场', '交易', '资本', '融资', '上市', '债券', '期货',
        '货币', '汇率', '利率', '通货', '财政', '税收', '贸易', '产业',
        '企业', '公司', '商业', '消费', '价格', '成本', '利润', '营收',
        '科技', '技术', '创新', '数字', '互联网', '人工智能', 'AI',
        '区块链', '大数据', '云计算', '金融科技', 'fintech', '支付',
        '监管', '政策', '法规', '改革', '发展', '增长', '指数', 'GDP'
    ]
    
    def __init__(self):
        self.logger = app_logger
    
    def filter_by_date(
        self,
        articles: List[Article],
        target_date: date = None
    ) -> List[Article]:
        """
        按日期过滤文章（仅保留指定日期的文章）
        
        Args:
            articles: 文章列表
            target_date: 目标日期，默认为昨天
        
        Returns:
            过滤后的文章列表
        """
        if target_date is None:
            target_date = date.today() - timedelta(days=1)
        
        filtered = []
        
        for article in articles:
            if article.publish_time is None:
                # 如果没有发布时间，保留文章（假设是最新的）
                self.logger.warning(
                    f"文章缺少发布时间，保留: {article.title[:50]}"
                )
                filtered.append(article)
                continue
            
            # 检查发布日期是否匹配
            article_date = article.publish_time.date()
            if article_date == target_date:
                filtered.append(article)
        
        self.logger.info(
            f"日期过滤: {len(articles)} -> {len(filtered)} "
            f"(目标日期: {target_date})"
        )
        
        return filtered
    
    def filter_by_date_range(
        self,
        articles: List[Article],
        start_date: date = None,
        end_date: date = None
    ) -> List[Article]:
        """
        按日期范围过滤文章
        
        Args:
            articles: 文章列表
            start_date: 开始日期（包含），默认为昨天
            end_date: 结束日期（包含），默认为昨天
        
        Returns:
            过滤后的文章列表
        """
        if start_date is None:
            start_date = date.today() - timedelta(days=1)
        if end_date is None:
            end_date = start_date
        
        filtered = []
        
        for article in articles:
            if article.publish_time is None:
                filtered.append(article)
                continue
            
            article_date = article.publish_time.date()
            if start_date <= article_date <= end_date:
                filtered.append(article)
        
        self.logger.info(
            f"日期范围过滤: {len(articles)} -> {len(filtered)} "
            f"({start_date} 到 {end_date})"
        )
        
        return filtered
    
    def filter_by_relevance(self, articles: List[Article]) -> List[Article]:
        """
        过滤与金融无关的内容
        使用关键词匹配判断文章是否与金融相关
        
        Args:
            articles: 文章列表
        
        Returns:
            过滤后的文章列表
        """
        filtered = []
        
        for article in articles:
            if self._is_finance_related(article):
                filtered.append(article)
            else:
                self.logger.debug(
                    f"过滤非金融相关文章: {article.title[:50]}"
                )
        
        self.logger.info(
            f"相关性过滤: {len(articles)} -> {len(filtered)}"
        )
        
        return filtered
    
    def _is_finance_related(self, article: Article) -> bool:
        """
        判断文章是否与金融相关
        
        Args:
            article: 文章对象
        
        Returns:
            是否相关
        """
        # 合并标题和内容进行检查
        text = f"{article.title} {article.content}".lower()
        
        # 检查是否包含金融关键词
        keyword_count = sum(
            1 for keyword in self.FINANCE_KEYWORDS
            if keyword.lower() in text
        )
        
        # 如果包含至少2个关键词，认为是相关的
        return keyword_count >= 2
    
    def remove_duplicates(self, articles: List[Article]) -> List[Article]:
        """
        去除重复文章（基于链接和标题）
        
        Args:
            articles: 文章列表
        
        Returns:
            去重后的文章列表
        """
        seen_links = set()
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # 标准化链接和标题
            link = article.link.strip().lower()
            title = article.title.strip().lower()
            
            # 检查是否重复
            if link in seen_links:
                self.logger.debug(f"重复链接: {article.link}")
                continue
            
            if title in seen_titles:
                self.logger.debug(f"重复标题: {article.title[:50]}")
                continue
            
            # 添加到结果
            seen_links.add(link)
            seen_titles.add(title)
            unique_articles.append(article)
        
        removed_count = len(articles) - len(unique_articles)
        if removed_count > 0:
            self.logger.info(f"去重: 移除 {removed_count} 篇重复文章")
        
        return unique_articles
    
    def clean_all(
        self,
        articles: List[Article],
        target_date: date = None,
        filter_relevance: bool = True
    ) -> List[Article]:
        """
        执行完整的清洗流程
        
        Args:
            articles: 文章列表
            target_date: 目标日期，默认为昨天
            filter_relevance: 是否过滤相关性
        
        Returns:
            清洗后的文章列表
        """
        self.logger.info(f"开始数据清洗，原始文章数: {len(articles)}")
        
        # 1. 去重
        articles = self.remove_duplicates(articles)
        
        # 2. 按日期过滤
        articles = self.filter_by_date(articles, target_date)
        
        # 3. 按相关性过滤（可选）
        if filter_relevance:
            articles = self.filter_by_relevance(articles)
        
        self.logger.info(f"数据清洗完成，最终文章数: {len(articles)}")
        
        return articles
