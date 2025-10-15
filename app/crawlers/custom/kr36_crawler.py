"""
36氪爬虫
"""
from typing import List, Dict
from datetime import datetime
import requests
from app.crawlers.base import BaseCrawler


class Kr36Crawler(BaseCrawler):
    """36氪新闻爬虫"""
    
    def __init__(self, source_name: str = None, source_url: str = None):
        super().__init__(source_name, source_url)
        self.base_url = "https://36kr.com"
        self.api_url = "https://www.36kr.com/api/feed"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch(self) -> List[Dict]:
        """爬取36氪新闻"""
        articles = []
        
        try:
            # 使用API获取最新文章
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=30
            )
            
            data = response.json()
            items = data.get('data', {}).get('items', [])[:10]
            
            for item in items:
                try:
                    title = item.get('title', '')
                    item_id = item.get('id', '')
                    link = f"{self.base_url}/p/{item_id}"
                    summary = item.get('summary', title)
                    
                    # 解析时间
                    pub_timestamp = item.get('published_at', 0)
                    pub_date = datetime.fromtimestamp(pub_timestamp) if pub_timestamp else datetime.now()
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'published': pub_date,
                        'summary': summary
                    })
                    
                except Exception as e:
                    self.logger.warning(f"解析文章失败: {e}")
                    continue
            
            self.logger.info(f"36氪爬取成功，获取 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"36氪爬取失败: {e}")
        
        return articles
