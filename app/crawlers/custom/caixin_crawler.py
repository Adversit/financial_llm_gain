"""财新网自定义爬虫"""
import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.crawlers.base import BaseCrawler, Article
from app.utils.logger import crawler_logger


class CaixinCrawler(BaseCrawler):
    """财新网（Caixin）自定义爬虫"""
    
    def fetch(self) -> List[Article]:
        """
        爬取财新网的文章
        
        Returns:
            文章列表
        """
        articles = []
        
        try:
            # 财新网金融频道
            url = "http://finance.caixin.com/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找文章列表 - 财新网使用 .boxa 类
            article_items = soup.select('.boxa')
            
            for item in article_items[:20]:  # 限制20篇
                try:
                    # 提取标题和链接
                    title_elem = item.select_one('h4 a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 确保链接是完整的
                    if link and not link.startswith('http'):
                        link = f"http://finance.caixin.com{link}"
                    
                    # 提取摘要
                    summary_elem = item.select_one('p')
                    content = summary_elem.get_text(strip=True) if summary_elem else title
                    
                    # 提取日期 - 财新网格式: "文｜财新 全月 2025年10月11日 15:50"
                    date_elem = item.select_one('span')
                    pub_date = None
                    if date_elem:
                        date_str = date_elem.get_text(strip=True)
                        try:
                            # 提取日期部分
                            import re
                            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{1,2}):(\d{2})', date_str)
                            if match:
                                year, month, day, hour, minute = match.groups()
                                pub_date = datetime(int(year), int(month), int(day), int(hour), int(minute))
                        except:
                            pass
                    
                    if title and link and content:
                        articles.append(Article(
                            title=title,
                            link=link,
                            content=content,
                            publish_time=pub_date or datetime.now(),
                            source_name=self.source_name
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"解析财新网条目失败: {e}")
                    continue
            
            self.logger.info(f"财新网爬取成功，获取 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"财新网爬取失败: {e}")
        
        return articles
