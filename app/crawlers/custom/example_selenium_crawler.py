"""示例：使用Selenium策略的爬虫"""
from typing import List
from bs4 import BeautifulSoup
from datetime import datetime

from app.crawlers.base import BaseCrawler, Article
from app.crawlers.strategies import SeleniumStrategy, StrategyManager


class ExampleSeleniumParser(SeleniumStrategy):
    """示例Selenium解析器 - 用于需要JavaScript渲染的页面"""
    
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        """
        解析页面内容
        
        这里是示例代码，实际使用时需要根据目标网站的HTML结构修改
        """
        articles = []
        
        # 示例：查找所有文章容器
        article_elements = soup.select('.article-item')
        
        for element in article_elements:
            try:
                title = self.clean_text(element.select_one('.title').get_text())
                link = element.select_one('a')['href']
                content = self.clean_text(element.select_one('.content').get_text()) or title
                
                if title and link and self.validate_content(content):
                    articles.append(Article(
                        title=title,
                        link=link,
                        content=content,
                        publish_time=None,
                        source_name=self.source_name
                    ))
                    
            except Exception as e:
                self.logger.error(f"解析文章失败: {e}")
                continue
        
        return articles
    
    def fetch(self) -> List[Article]:
        """
        重写fetch方法以添加特殊的Selenium操作
        """
        articles = []
        
        try:
            self.logger.info(f"使用Selenium策略获取: {self.source_url}")
            
            # 初始化浏览器
            self._init_driver()
            
            # 加载页面
            self.driver.get(self.source_url)
            
            # 示例：滚动到底部加载更多内容
            self.scroll_to_bottom(pause_time=2.0)
            
            # 示例：点击"加载更多"按钮
            # self.click_load_more('.load-more-btn', max_clicks=3)
            
            # 示例：等待特定元素加载
            # from selenium.webdriver.common.by import By
            # self.wait_for_element(By.CLASS_NAME, 'article-list')
            
            # 获取页面源码
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 解析页面
            articles = self.parse_page(soup)
            
            self.log_success(len(articles))
            
        except Exception as e:
            self.log_error(e)
            raise
        finally:
            self._close_driver()
        
        return articles


class ExampleSeleniumCrawler(BaseCrawler):
    """
    示例Selenium爬虫
    
    用于需要JavaScript渲染的动态页面
    """
    
    def fetch(self) -> List[Article]:
        """使用Selenium策略获取文章"""
        # 创建策略管理器
        manager = StrategyManager()
        
        # 添加Selenium策略
        selenium_strategy = ExampleSeleniumParser(
            source_name=self.source_name,
            source_url=self.source_url,
            headless=True,  # 无头模式
            wait_time=5  # 等待5秒让JavaScript执行
        )
        manager.add_strategy(selenium_strategy)
        
        # 使用策略获取文章
        return manager.fetch_with_fallback()
