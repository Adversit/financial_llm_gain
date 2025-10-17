"""
词云生成服务
"""
import os
import json
from datetime import datetime, date
from typing import List, Dict, Optional
from collections import Counter
from pathlib import Path

from wordcloud import WordCloud
import jieba
from PIL import Image
import numpy as np

from app.database import get_db
from app.models.article import Article
from app.models.summary import Summary
from app.utils.logger import app_logger


class WordCloudService:
    """词云生成服务"""
    
    def __init__(self, output_dir: str = "static/wordclouds"):
        """
        初始化词云服务
        
        Args:
            output_dir: 词云图片输出目录
        """
        self.output_dir = output_dir
        self.ensure_output_dir()
        
        # 词云配置
        self.wordcloud_config = {
            'width': 1200,
            'height': 600,
            'background_color': 'white',
            'max_words': 100,
            'relative_scaling': 0.5,
            'min_font_size': 10,
            'max_font_size': 100,
            'font_path': self._get_font_path(),
            'colormap': 'viridis',
            'prefer_horizontal': 0.7,
        }
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def _get_font_path(self) -> Optional[str]:
        """
        获取中文字体路径
        
        Returns:
            字体文件路径，如果找不到则返回None
        """
        # 常见的中文字体路径
        font_paths = [
            # Windows
            'C:/Windows/Fonts/simhei.ttf',  # 黑体
            'C:/Windows/Fonts/msyh.ttc',    # 微软雅黑
            'C:/Windows/Fonts/simsun.ttc',  # 宋体
            # Linux
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
            # macOS
            '/System/Library/Fonts/PingFang.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        
        app_logger.warning("未找到中文字体，词云可能无法正确显示中文")
        return None
    
    def generate_wordcloud_from_keywords(
        self,
        target_date: date,
        keyword_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> str:
        """
        从关键词生成词云
        
        Args:
            target_date: 目标日期
            keyword_type: 关键词类型筛选（可选）
            category: 文章类别筛选（可选）
        
        Returns:
            生成的词云图片路径
        """
        app_logger.info(f"开始生成词云: date={target_date}, type={keyword_type}, category={category}")
        
        # 获取关键词数据
        keywords_data = self._get_keywords_data(target_date, keyword_type, category)
        
        if not keywords_data:
            app_logger.warning(f"没有找到关键词数据: {target_date}")
            return None
        
        # 生成词云
        filename = self._generate_filename(target_date, keyword_type, category)
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            # 创建词云对象
            wc = WordCloud(**self.wordcloud_config)
            
            # 生成词云
            wc.generate_from_frequencies(keywords_data)
            
            # 保存图片
            wc.to_file(output_path)
            
            app_logger.info(f"词云生成成功: {output_path}")
            return output_path
            
        except Exception as e:
            app_logger.error(f"词云生成失败: {e}")
            return None
    
    def generate_wordcloud_from_text(
        self,
        target_date: date,
        category: Optional[str] = None
    ) -> str:
        """
        从文章文本生成词云
        
        Args:
            target_date: 目标日期
            category: 文章类别筛选（可选）
        
        Returns:
            生成的词云图片路径
        """
        app_logger.info(f"从文本生成词云: date={target_date}, category={category}")
        
        # 获取文章文本
        text = self._get_articles_text(target_date, category)
        
        if not text:
            app_logger.warning(f"没有找到文章文本: {target_date}")
            return None
        
        # 中文分词
        words = jieba.cut(text)
        filtered_words = [w for w in words if len(w) > 1]  # 过滤单字
        text_processed = ' '.join(filtered_words)
        
        # 生成词云
        filename = self._generate_filename(target_date, None, category, suffix='_text')
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            wc = WordCloud(**self.wordcloud_config)
            wc.generate(text_processed)
            wc.to_file(output_path)
            
            app_logger.info(f"文本词云生成成功: {output_path}")
            return output_path
            
        except Exception as e:
            app_logger.error(f"文本词云生成失败: {e}")
            return None
    
    def _get_keywords_data(
        self,
        target_date: date,
        keyword_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, int]:
        """
        获取关键词数据
        
        Returns:
            关键词频率字典 {word: count}
        """
        db = next(get_db())
        
        try:
            # 构建查询
            query = db.query(Summary).join(Summary.article)
            
            # 日期筛选
            query = query.filter(
                Article.publish_time >= datetime.combine(target_date, datetime.min.time()),
                Article.publish_time < datetime.combine(target_date, datetime.max.time())
            )
            
            # 类别筛选
            if category:
                query = query.join(Article.source).filter(Article.source.has(category=category))
            
            summaries = query.all()
            
            # 统计关键词
            keyword_counter = Counter()
            
            for summary in summaries:
                if summary.keywords:
                    try:
                        keywords = json.loads(summary.keywords)
                        for kw in keywords:
                            word = kw.get('word', '')
                            kw_type = kw.get('type', '')
                            
                            # 类型筛选
                            if keyword_type and kw_type != keyword_type:
                                continue
                            
                            if word:
                                keyword_counter[word] += 1
                    except:
                        pass
            
            return dict(keyword_counter)
            
        finally:
            db.close()
    
    def _get_articles_text(
        self,
        target_date: date,
        category: Optional[str] = None
    ) -> str:
        """
        获取文章文本
        
        Returns:
            合并的文章文本
        """
        db = next(get_db())
        
        try:
            query = db.query(Article)
            
            # 日期筛选
            query = query.filter(
                Article.publish_time >= datetime.combine(target_date, datetime.min.time()),
                Article.publish_time < datetime.combine(target_date, datetime.max.time())
            )
            
            # 类别筛选
            if category:
                query = query.join(Article.source).filter(Article.source.has(category=category))
            
            articles = query.all()
            
            # 合并标题和摘要
            texts = []
            for article in articles:
                if article.title:
                    texts.append(article.title)
                
                # 获取摘要
                if article.summaries:
                    summary = article.summaries[0]
                    if summary.summary:
                        texts.append(summary.summary)
            
            return ' '.join(texts)
            
        finally:
            db.close()
    
    def _generate_filename(
        self,
        target_date: date,
        keyword_type: Optional[str] = None,
        category: Optional[str] = None,
        suffix: str = ''
    ) -> str:
        """
        生成文件名
        
        Returns:
            文件名
        """
        parts = [target_date.strftime('%Y%m%d')]
        
        if category:
            parts.append(category)
        
        if keyword_type:
            parts.append(keyword_type)
        
        if suffix:
            parts.append(suffix)
        
        return '_'.join(parts) + '.png'
    
    def get_wordcloud_path(
        self,
        target_date: date,
        keyword_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[str]:
        """
        获取词云图片路径（如果存在）
        
        Returns:
            词云图片路径，如果不存在则返回None
        """
        filename = self._generate_filename(target_date, keyword_type, category)
        filepath = os.path.join(self.output_dir, filename)
        
        if os.path.exists(filepath):
            return filepath
        
        return None
    
    def generate_daily_wordclouds(self, target_date: date) -> List[str]:
        """
        生成每日的所有词云（总体 + 各类别）
        
        Args:
            target_date: 目标日期
        
        Returns:
            生成的词云图片路径列表
        """
        app_logger.info(f"开始生成每日词云: {target_date}")
        
        wordclouds = []
        
        # 1. 生成总体词云
        overall_wc = self.generate_wordcloud_from_keywords(target_date)
        if overall_wc:
            wordclouds.append(overall_wc)
        
        # 2. 生成各类别词云
        categories = ['政治', '经济', '技术', '金融科技']
        for category in categories:
            category_wc = self.generate_wordcloud_from_keywords(target_date, category=category)
            if category_wc:
                wordclouds.append(category_wc)
        
        # 3. 生成各关键词类型的词云（可选）
        keyword_types = ['公司', '行业', '经济指标', '市场动态']
        for kw_type in keyword_types:
            type_wc = self.generate_wordcloud_from_keywords(target_date, keyword_type=kw_type)
            if type_wc:
                wordclouds.append(type_wc)
        
        app_logger.info(f"每日词云生成完成，共 {len(wordclouds)} 个")
        return wordclouds
    
    def cleanup_old_wordclouds(self, days: int = 30):
        """
        清理旧的词云图片
        
        Args:
            days: 保留最近多少天的词云
        """
        app_logger.info(f"开始清理 {days} 天前的词云")
        
        cutoff_date = datetime.now().date()
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        cleaned = 0
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.png'):
                try:
                    # 从文件名提取日期
                    date_str = filename.split('_')[0]
                    file_date = datetime.strptime(date_str, '%Y%m%d').date()
                    
                    if file_date < cutoff_date:
                        filepath = os.path.join(self.output_dir, filename)
                        os.remove(filepath)
                        cleaned += 1
                except:
                    pass
        
        app_logger.info(f"清理完成，删除了 {cleaned} 个旧词云")


# 全局实例
wordcloud_service = WordCloudService()
