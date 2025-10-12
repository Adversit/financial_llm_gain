"""第一财经自定义爬虫"""
import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime, timedelta
from app.crawlers.base import BaseCrawler, Article
from app.utils.logger import crawler_logger


class YicaiCrawler(BaseCrawler):
    """第一财经（Yicai）自定义爬虫"""
    
    def fetch(self) -> List[Article]:
        """
        爬取第一财经的文章
        
        Returns:
            文章列表
        """
        articles = []
        
        try:
            # 第一财经新闻列表页
            url = "https://www.yicai.com/news/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找文章列表 - 第一财经使用 .m-list 类
            article_items = soup.select('.m-list')
            
            for item in article_items[:20]:  # 限制20篇
                try:
                    # 提取标题
                    title_elem = item.select_one('h2')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # 提取链接 - 从父级 a 标签获取
                    link_elem = item.find_parent('a')
                    if not link_elem:
                        continue
                    
                    link = link_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = f"https://www.yicai.com{link}"
                    
                    # 提取摘要
                    summary_elem = item.select_one('p')
                    content = summary_elem.get_text(strip=True) if summary_elem else title
                    
                    # 提取时间 - 第一财经使用相对时间
                    time_elem = item.select_one('.author span:last-child')
                    pub_date = datetime.now()
                    if time_elem:
                        time_str = time_elem.get_text(strip=True)
                        try:
                            if '分钟前' in time_str:
                                minutes = int(time_str.replace('分钟前', ''))
                                pub_date = datetime.now() - timedelta(minutes=minutes)
                            elif '小时前' in time_str:
                                hours = int(time_str.replace('小时前', ''))
                                pub_date = datetime.now() - timedelta(hours=hours)
                            elif '天前' in time_str:
                                days = int(time_str.replace('天前', ''))
                                pub_date = datetime.now() - timedelta(days=days)
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
                    self.logger.warning(f"解析第一财经条目失败: {e}")
                    continue
            
            self.logger.info(f"第一财经爬取成功，获取 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"第一财经爬取失败: {e}")
        
        return articles
