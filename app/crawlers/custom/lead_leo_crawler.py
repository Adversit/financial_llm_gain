"""头豹研究院爬虫"""
import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.crawlers.base import BaseCrawler, Article
from app.utils.logger import crawler_logger


class LeadLeoCrawler(BaseCrawler):
    """
    头豹研究院（LeadLeo）自定义爬虫
    
    ⚠️ 当前状态: 无法爬取
    
    问题分析:
    1. 网站使用Cookie验证机制
    2. 首次访问返回极简HTML（仅168字符）
    3. HTML内容: 设置Cookie后自动刷新页面
    4. 需要Cookie才能访问实际内容
    5. 可能还有其他反爬虫机制
    
    HTML内容示例:
    <html><head><meta charset='utf-8'>
    <script>document.cookie='js_cookie=1;path=/';location.reload();</script>
    </head><body><noscript>请启用 JavaScript</noscript></body></html>
    
    解决方案:
    方案1: 使用Session保持Cookie
        - 创建requests.Session()
        - 第一次请求获取Cookie
        - 第二次请求使用Cookie访问
    
    方案2: 使用Selenium
        - 自动处理Cookie和JavaScript
        - 等待页面完全加载
    
    方案3: 分析API接口
        - 可能有移动端API或公开API
        - 使用开发者工具查找数据接口
    
    临时方案: 返回空列表，不影响其他信息源
    """
    
    def fetch(self) -> List[Article]:
        """
        尝试爬取头豹研究院的文章
        
        Returns:
            文章列表（当前返回空列表）
        """
        articles = []
        
        try:
            url = "https://www.leadleo.com/"
            
            # 使用Session保持Cookie
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # 第一次请求 - 获取Cookie
            response1 = session.get(url, timeout=30)
            
            # 第二次请求 - 使用Cookie
            response2 = session.get(url, timeout=30)
            response2.encoding = 'utf-8'
            
            soup = BeautifulSoup(response2.text, 'html.parser')
            
            # 检查是否成功获取内容
            if len(response2.text) < 500:
                self.logger.warning(
                    f"头豹研究院: 网站需要Cookie验证，返回内容过少（{len(response2.text)}字符）。"
                    "建议使用Selenium或分析API接口。"
                )
                return []
            
            # 尝试查找文章列表
            article_items = soup.select('div.report-item') or soup.select('div.item') or soup.select('li')
            
            if not article_items:
                self.logger.warning("头豹研究院: 未找到文章列表")
                return []
            
            # 如果找到了文章
            for item in article_items[:20]:
                try:
                    title_elem = item.select_one('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get('title') or title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = f"https://www.leadleo.com{link}"
                    
                    summary_elem = item.select_one('.summary') or item.select_one('.desc') or item.select_one('p')
                    content = summary_elem.get_text(strip=True) if summary_elem else title
                    
                    date_elem = item.select_one('.date') or item.select_one('.time')
                    pub_date = datetime.now()
                    if date_elem:
                        date_str = date_elem.get_text(strip=True)
                        try:
                            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d']:
                                try:
                                    pub_date = datetime.strptime(date_str, fmt)
                                    break
                                except:
                                    continue
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
                    self.logger.warning(f"解析头豹研究院条目失败: {e}")
                    continue
            
            self.logger.info(f"头豹研究院爬取成功，获取 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"头豹研究院爬取失败: {e}")
        
        return articles
