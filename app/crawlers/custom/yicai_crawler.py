"""第一财经爬虫 - 使用新的策略架构"""
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime, timedelta

from app.crawlers.base import BaseCrawler, Article
from app.crawlers.strategies import HTTPStrategy, StrategyManager


class YicaiHTTPParser(HTTPStrategy):
    """第一财经HTTP解析器"""
    
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        """解析第一财经页面"""
        articles = []
        
        # 查找文章列表
        article_items = soup.select('.m-list')
        
        for item in article_items[:20]:  # 限制20篇
            try:
                # 提取标题
                title_elem = item.select_one('h2')
                if not title_elem:
                    continue
                
                title = self.extract_text(title_elem)
                
                # 提取链接
                link_elem = item.find_parent('a')
                if not link_elem:
                    continue
                
                link = link_elem.get('href', '')
                if link and not link.startswith('http'):
                    link = f"https://www.yicai.com{link}"
                
                # 提取摘要
                summary_elem = item.select_one('p')
                content = self.extract_text(summary_elem) if summary_elem else title
                
                # 提取时间 - 第一财经使用相对时间
                time_elem = item.select_one('.author span:last-child')
                pub_date = self._parse_relative_time(time_elem)
                
                if title and link and self.validate_content(content):
                    articles.append(Article(
                        title=title,
                        link=link,
                        content=content,
                        publish_time=pub_date,
                        source_name=self.source_name
                    ))
                    
            except Exception as e:
                self.logger.warning(f"解析条目失败: {e}")
                continue
        
        return articles
    
    def _parse_relative_time(self, time_elem) -> datetime:
        """解析相对时间"""
        if not time_elem:
            return datetime.now()
        
        time_str = self.extract_text(time_elem)
        
        try:
            if '分钟前' in time_str:
                minutes = int(time_str.replace('分钟前', ''))
                return datetime.now() - timedelta(minutes=minutes)
            elif '小时前' in time_str:
                hours = int(time_str.replace('小时前', ''))
                return datetime.now() - timedelta(hours=hours)
            elif '天前' in time_str:
                days = int(time_str.replace('天前', ''))
                return datetime.now() - timedelta(days=days)
        except:
            pass
        
        return datetime.now()


class YicaiCrawler(BaseCrawler):
    """第一财经爬虫 - 使用策略模式"""
    
    def fetch(self) -> List[Article]:
        """使用HTTP策略获取文章"""
        manager = StrategyManager()
        
        # 添加HTTP策略
        manager.add_strategy(YicaiHTTPParser(
            source_name=self.source_name,
            source_url="https://www.yicai.com/news/"
        ))
        
        return manager.fetch_with_fallback()
