"""艾瑞咨询爬虫"""
import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.crawlers.base import BaseCrawler, Article
from app.utils.logger import crawler_logger


class iResearchCrawler(BaseCrawler):
    """
    艾瑞咨询（iResearch）自定义爬虫
    
    ⚠️ 当前状态: 无法爬取
    
    问题分析:
    1. 网站使用前后端分离架构
    2. 静态HTML中只有2个链接（版权信息）
    3. 所有内容通过JavaScript/API动态加载
    4. HTML大小仅10KB，没有文章数据
    5. RSS源存在但返回空内容
    
    解决方案:
    方案1: 分析API接口
        - 使用浏览器开发者工具查看Network请求
        - 找到文章列表的API端点
        - 直接调用API获取JSON数据
    
    方案2: 使用Selenium
        - 模拟浏览器访问，等待JavaScript执行
        - 获取渲染后的完整HTML
    
    方案3: 寻找特定的报告列表页
        - 艾瑞咨询可能有专门的报告列表页面
        - 尝试不同的URL路径
    
    临时方案: 返回空列表，不影响其他信息源
    """
    
    def fetch(self) -> List[Article]:
        """
        尝试爬取艾瑞咨询的文章
        
        Returns:
            文章列表（当前返回空列表）
        """
        articles = []
        
        try:
            url = "https://www.iresearch.com.cn/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试查找文章列表
            article_items = soup.select('div.m-cont-list li') or soup.select('ul.list li') or soup.select('li')
            
            # 过滤掉导航菜单等非文章项
            valid_items = []
            for item in article_items:
                link = item.select_one('a')
                if link and link.get('href', '').startswith('http'):
                    valid_items.append(item)
            
            if not valid_items:
                self.logger.warning(
                    "艾瑞咨询: 网站使用前后端分离架构，静态HTML中没有文章数据。"
                    "建议分析API接口或使用Selenium。"
                )
                return []
            
            # 如果找到了文章（理论上不会执行到这里）
            for item in valid_items[:20]:
                try:
                    title_elem = item.select_one('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get('title') or title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = f"https://www.iresearch.com.cn{link}"
                    
                    summary_elem = item.select_one('.desc') or item.select_one('p')
                    content = summary_elem.get_text(strip=True) if summary_elem else title
                    
                    date_elem = item.select_one('.date') or item.select_one('.time') or item.select_one('span')
                    pub_date = datetime.now()
                    if date_elem:
                        date_str = date_elem.get_text(strip=True)
                        try:
                            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%m-%d']:
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
                    self.logger.warning(f"解析艾瑞咨询条目失败: {e}")
                    continue
            
            self.logger.info(f"艾瑞咨询爬取成功，获取 {len(articles)} 篇文章")
            
        except Exception as e:
            self.logger.error(f"艾瑞咨询爬取失败: {e}")
        
        return articles
