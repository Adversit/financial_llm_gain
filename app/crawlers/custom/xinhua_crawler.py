"""
新华社爬虫
"""
from typing import List, Dict
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from app.crawlers.base import BaseCrawler


class XinhuaCrawler(BaseCrawler):
    """新华社新闻爬虫"""
    
    def __init__(self, source_name: str = None, source_url: str = None):
        super().__init__(source_name, source_url)
        self.base_url = "http://www.news.cn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch(self) -> List[Dict]:
        """爬取新华社新闻"""
        articles = []
        
        try:
            # 爬取财经频道
            url = f"{self.base_url}/fortune/index.htm"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找新闻列表
            news_items = soup.select('.news-list li')[:10]
            
            for item in news_items:
                try:
                    link_tag = item.select_one('a')
                    if not link_tag:
                        continue
                    
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')
                    
                    if not link.startswith('http'):
                        link = self.base_url + link
                    
                    # 获取时间
                    time_tag = item.select_one('.time')
                    pub_date = datetime.now()
                    if time_tag:
                        time_str = time_tag.get_text(strip=True)
                        try:
                            pub_date = datetime.strptime(time_str, '%Y-%m-%d')
                        except:
                            pass
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'published': pub_date,
                        'summary': title
                    })
                    
                except Exception as e:
                    self.logger.warning(f"解析新闻项失败: {e}")
                    continue
            
            self.logger.info(f"新华社爬取成功，获取 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"新华社爬取失败: {e}")
        
        return articles
