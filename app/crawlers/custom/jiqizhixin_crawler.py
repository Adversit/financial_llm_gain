"""机器之心自定义爬虫"""
import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime, timedelta
from app.crawlers.base import BaseCrawler, Article
from app.utils.logger import crawler_logger


class JiqizhixinCrawler(BaseCrawler):
    """
    机器之心（Jiqizhixin）自定义爬虫
    
    ⚠️ 当前状态: 无法爬取
    
    问题分析:
    1. 网站使用JavaScript动态加载内容（React/Vue等前端框架）
    2. 静态HTML中只有基本框架，没有文章数据
    3. 文章数据通过API异步加载
    4. HTML大小仅11KB，包含19个链接，但都是导航链接
    
    解决方案:
    方案1: 使用Selenium/Playwright模拟浏览器
        - 优点: 可以执行JavaScript，获取完整内容
        - 缺点: 需要安装浏览器驱动，速度较慢
    
    方案2: 分析并直接调用API
        - 优点: 速度快，稳定
        - 缺点: 需要逆向工程找到API接口
        - 建议: 使用浏览器开发者工具查看Network请求
    
    方案3: 使用RSSHub
        - 检查是否有机器之心的RSSHub路由
        - 如果没有，可以贡献一个新路由
    
    临时方案: 返回空列表，不影响其他信息源
    """
    
    def fetch(self) -> List[Article]:
        """
        尝试爬取机器之心的文章
        
        Returns:
            文章列表（当前返回空列表）
        """
        articles = []
        
        try:
            url = "https://www.jiqizhixin.com/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试查找文章列表
            article_items = soup.select('div.article-item') or soup.select('div[class*="article"]')
            
            if not article_items:
                self.logger.warning(
                    "机器之心: 网站使用JavaScript动态加载，静态HTML中没有文章数据。"
                    "建议使用Selenium或分析API接口。"
                )
                return []
            
            # 如果找到了文章（理论上不会执行到这里）
            for item in article_items[:20]:
                try:
                    title_elem = item.select_one('h3 a') or item.select_one('a.title') or item.select_one('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = f"https://www.jiqizhixin.com{link}"
                    
                    summary_elem = item.select_one('.article-desc') or item.select_one('.desc') or item.select_one('p')
                    content = summary_elem.get_text(strip=True) if summary_elem else title
                    
                    date_elem = item.select_one('.time') or item.select_one('.date') or item.select_one('time')
                    pub_date = datetime.now()
                    if date_elem:
                        date_str = date_elem.get_text(strip=True)
                        try:
                            if '小时前' in date_str:
                                hours = int(date_str.replace('小时前', '').strip())
                                pub_date = datetime.now() - timedelta(hours=hours)
                            elif '天前' in date_str:
                                days = int(date_str.replace('天前', '').strip())
                                pub_date = datetime.now() - timedelta(days=days)
                            elif '分钟前' in date_str:
                                minutes = int(date_str.replace('分钟前', '').strip())
                                pub_date = datetime.now() - timedelta(minutes=minutes)
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
                    self.logger.warning(f"解析机器之心条目失败: {e}")
                    continue
            
            self.logger.info(f"机器之心爬取成功，获取 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"机器之心爬取失败: {e}")
        
        return articles
