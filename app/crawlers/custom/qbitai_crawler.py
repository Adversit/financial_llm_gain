"""量子位自定义爬虫"""
import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime, timedelta
from app.crawlers.base import BaseCrawler, Article
from app.utils.logger import crawler_logger


class QbitaiCrawler(BaseCrawler):
    """量子位（Qbitai）自定义爬虫"""
    
    def fetch(self) -> List[Article]:
        """
        爬取量子位的文章
        
        Returns:
            文章列表
        """
        articles = []
        
        try:
            # 量子位文章列表页
            url = "https://www.qbitai.com/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找文章列表
            article_items = soup.select('.picture_text')
            
            for item in article_items[:20]:  # 限制20篇
                try:
                    # 提取标题和链接
                    title_elem = item.select_one('h4 a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 处理相对链接
                    if link and not link.startswith('http'):
                        link = f"https://www.qbitai.com{link}"
                    
                    # 提取摘要
                    summary_elem = item.select_one('.text_box p')
                    content = summary_elem.get_text(strip=True) if summary_elem else title
                    
                    # 提取日期 - 量子位使用相对时间
                    date_elem = item.select_one('.time')
                    pub_date = datetime.now()  # 默认使用当前时间
                    if date_elem:
                        date_str = date_elem.get_text(strip=True)
                        # 处理相对时间（如"4小时前"）
                        try:
                            if '小时前' in date_str:
                                hours = int(date_str.replace('小时前', ''))
                                pub_date = datetime.now() - timedelta(hours=hours)
                            elif '天前' in date_str:
                                days = int(date_str.replace('天前', ''))
                                pub_date = datetime.now() - timedelta(days=days)
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
                    self.logger.warning(f"解析量子位条目失败: {e}")
                    continue
            
            self.logger.info(f"量子位爬取成功，获取 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"量子位爬取失败: {e}")
        
        return articles
