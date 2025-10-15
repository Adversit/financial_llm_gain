"""Selenium爬取策略 - 用于需要JavaScript渲染的页面"""
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup

from app.crawlers.strategies.base_strategy import CrawlerStrategy
from app.crawlers.base import Article


class SeleniumStrategy(CrawlerStrategy):
    """Selenium爬取策略 - 优先级第四"""
    
    def __init__(
        self,
        source_name: str,
        source_url: str,
        headless: bool = True,
        timeout: int = 30,
        wait_time: int = 5
    ):
        """
        初始化Selenium策略
        
        Args:
            source_name: 信息源名称
            source_url: 目标URL
            headless: 是否无头模式
            timeout: 页面加载超时时间
            wait_time: 等待JavaScript执行时间
        """
        super().__init__(source_name, source_url)
        self.headless = headless
        self.timeout = timeout
        self.wait_time = wait_time
        self.driver = None
    
    def get_priority(self) -> int:
        """Selenium策略优先级第四"""
        return self.PRIORITY_SELENIUM
    
    def can_handle(self) -> bool:
        """检查Selenium是否可用"""
        try:
            from selenium import webdriver
            return True
        except ImportError:
            self.log_warning("Selenium未安装，无法使用此策略")
            return False
    
    def fetch(self) -> List[Article]:
        """获取文章列表"""
        articles = []
        
        try:
            self.logger.info(f"使用Selenium策略获取: {self.source_url}")
            
            # 初始化浏览器
            self._init_driver()
            
            # 加载页面
            self.driver.get(self.source_url)
            
            # 等待JavaScript执行
            import time
            time.sleep(self.wait_time)
            
            # 获取页面源码
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 调用子类实现的解析方法
            articles = self.parse_page(soup)
            
            self.log_success(len(articles))
            
        except Exception as e:
            self.log_error(e)
            raise
        finally:
            self._close_driver()
        
        return articles
    
    def _init_driver(self):
        """初始化Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            
            if self.headless:
                options.add_argument('--headless')
            
            # 常用选项
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # 禁用图片加载（加速）
            prefs = {
                'profile.managed_default_content_settings.images': 2,
                'profile.default_content_setting_values': {'notifications': 2}
            }
            options.add_experimental_option('prefs', prefs)
            
            # 创建driver
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.timeout)
            
            self.logger.info("Selenium WebDriver初始化成功")
            
        except Exception as e:
            self.logger.error(f"Selenium WebDriver初始化失败: {e}")
            raise
    
    def _close_driver(self):
        """关闭WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Selenium WebDriver已关闭")
            except Exception as e:
                self.logger.error(f"关闭WebDriver失败: {e}")
    
    def parse_page(self, soup: BeautifulSoup) -> List[Article]:
        """
        解析页面内容
        
        子类必须实现此方法
        
        Args:
            soup: BeautifulSoup对象
        
        Returns:
            文章列表
        """
        raise NotImplementedError("子类必须实现parse_page方法")
    
    def wait_for_element(self, by, value, timeout: Optional[int] = None):
        """
        等待元素出现
        
        Args:
            by: 定位方式（如By.ID, By.CLASS_NAME等）
            value: 定位值
            timeout: 超时时间（秒）
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        timeout = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def scroll_to_bottom(self, pause_time: float = 1.0):
        """
        滚动到页面底部（用于加载动态内容）
        
        Args:
            pause_time: 每次滚动后的暂停时间
        """
        import time
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # 滚动到底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            
            # 计算新的高度
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
    
    def click_load_more(self, selector: str, max_clicks: int = 5):
        """
        点击"加载更多"按钮
        
        Args:
            selector: 按钮的CSS选择器
            max_clicks: 最大点击次数
        """
        import time
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        
        for i in range(max_clicks):
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                button.click()
                time.sleep(2)
                self.logger.info(f"点击加载更多按钮 ({i+1}/{max_clicks})")
            except NoSuchElementException:
                self.logger.info("没有找到加载更多按钮，停止点击")
                break
            except Exception as e:
                self.logger.warning(f"点击加载更多失败: {e}")
                break
