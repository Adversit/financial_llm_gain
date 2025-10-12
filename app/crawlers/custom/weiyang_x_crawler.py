"""未央网爬虫 - 使用RSS源"""
import feedparser
from typing import List
from datetime import datetime
from app.crawlers.base import BaseCrawler, Article
from app.utils.logger import crawler_logger


class WeiyangXCrawler(BaseCrawler):
    """未央网（WeiyangX）自定义爬虫 - 使用RSS源"""
    
    def fetch(self) -> List[Article]:
        """
        爬取未央网的文章 - 通过RSS源
        
        网站分析:
        - 未央网首页使用JavaScript动态加载内容
        - 静态HTML中只有导航菜单，没有文章列表
        - 但网站提供了RSS源: https://www.weiyangx.com/rss
        
        Returns:
            文章列表
        """
        articles = []
        
        try:
            # 使用未央网的RSS源
            rss_url = "https://www.weiyangx.com/rss"
            
            self.logger.info(f"开始获取未央网RSS源: {rss_url}")
            
            # 解析RSS
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                self.logger.warning("未央网RSS源没有返回文章")
                return []
            
            # 处理每篇文章
            for entry in feed.entries[:20]:  # 限制20篇
                try:
                    title = entry.get('title', '').strip()
                    link = entry.get('link', '').strip()
                    
                    # 获取内容
                    content = entry.get('summary', '') or entry.get('description', '') or title
                    # 清理HTML标签
                    from bs4 import BeautifulSoup
                    content = BeautifulSoup(content, 'html.parser').get_text(strip=True)
                    
                    # 解析时间
                    pub_date = datetime.now()
                    if 'published_parsed' in entry and entry.published_parsed:
                        try:
                            import time
                            pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                        except:
                            pass
                    
                    if title and link and content:
                        articles.append(Article(
                            title=title,
                            link=link,
                            content=content,
                            publish_time=pub_date,
                            source_name=self.source_name
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"解析未央网RSS条目失败: {e}")
                    continue
            
            self.logger.info(f"未央网爬取成功，获取 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"未央网爬取失败: {e}")
        
        return articles
