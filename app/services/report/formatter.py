"""报告格式转换模块"""
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict
from jinja2 import Environment, FileSystemLoader

from app.utils.logger import app_logger


class ReportFormatter:
    """报告格式转换器"""
    
    def __init__(self, template_dir: str = "templates", output_dir: str = "data/reports"):
        """
        初始化格式转换器
        
        Args:
            template_dir: 模板目录
            output_dir: 输出目录
        """
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.logger = app_logger
        
        # 初始化Jinja2环境
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False  # 关闭自动转义，因为 overall_summary 已经是 HTML 格式
        )
    
    def format_summary_to_html(self, text: str) -> str:
        """
        将 AI 生成的文本格式转换为带内联样式的美观 HTML
        这样生成的 HTML 可以：
        1. 在静态文件中直接美观显示
        2. 在邮件中正确显示（邮件客户端需要内联样式）
        3. 在前端页面中被 CSS 覆盖以实现更丰富的效果
        
        Args:
            text: 原始文本
        
        Returns:
            带内联样式的 HTML 格式文本
        """
        # 处理分隔线
        text = text.replace('---', '<hr style="margin: 30px 0; border: none; border-top: 2px solid #ecf0f1;">')
        text = text.replace('___', '<hr style="margin: 30px 0; border: none; border-top: 2px solid #ecf0f1;">')
        
        # 处理 Markdown 标题 (### 标题)
        text = re.sub(
            r'^###\s+(.+?)$',
            r'<h3 style="margin: 25px 0 15px 0; padding-bottom: 10px; border-bottom: 2px solid #ecf0f1; color: #2c3e50; font-size: 20px; font-weight: bold; line-height: 1.4;">\1</h3>',
            text,
            flags=re.MULTILINE
        )
        text = re.sub(
            r'^##\s+(.+?)$',
            r'<h2 style="margin: 25px 0 15px 0; color: #2c3e50; font-size: 24px; font-weight: bold; line-height: 1.4;">\1</h2>',
            text,
            flags=re.MULTILINE
        )
        text = re.sub(
            r'^#\s+(.+?)$',
            r'<h1 style="margin: 30px 0 20px 0; color: #2c3e50; font-size: 28px; font-weight: bold; line-height: 1.4;">\1</h1>',
            text,
            flags=re.MULTILINE
        )
        
        # 处理标题（一、二、三、四）- 先处理，避免被粗体标记影响
        text = re.sub(
            r'^\*\*(一、|二、|三、|四、)(.+?)\*\*\s*$',
            r'<h3 style="margin: 25px 0 15px 0; padding-bottom: 10px; border-bottom: 2px solid #ecf0f1; color: #2c3e50; font-size: 20px; font-weight: bold; line-height: 1.4;">\1\2</h3>',
            text,
            flags=re.MULTILINE
        )
        
        # 处理子标题（【xxx】）- 先处理
        text = re.sub(
            r'\*\*【(.+?)】\*\*',
            r'<h4 style="margin: 20px 0 12px 0; color: #34495e; font-size: 18px; font-weight: bold; line-height: 1.4;">【\1】</h4>',
            text
        )
        
        # 处理粗体（**文本**）
        text = re.sub(
            r'\*\*(.+?)\*\*',
            r'<strong style="color: #2c3e50; font-weight: bold;">\1</strong>',
            text
        )
        
        # 处理列表项（- 开头）
        lines = text.split('\n')
        in_list = False
        list_type = None  # 'ul' or 'ol'
        result_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # 无序列表项
            if stripped.startswith('- '):
                if not in_list or list_type != 'ul':
                    if in_list:
                        # 关闭之前的列表
                        result_lines.append(f'</{list_type}>')
                    result_lines.append('<ul style="margin: 15px 0 20px 0; padding-left: 25px; list-style-type: disc;">')
                    in_list = True
                    list_type = 'ul'
                result_lines.append(f'<li style="margin-bottom: 12px; line-height: 1.8; color: #333; font-size: 14px;">{stripped[2:]}</li>')
            # 有序列表项
            elif re.match(r'^\d+\.\s', stripped):
                if not in_list or list_type != 'ol':
                    if in_list:
                        # 关闭之前的列表
                        result_lines.append(f'</{list_type}>')
                    result_lines.append('<ol style="margin: 15px 0 20px 0; padding-left: 25px;">')
                    in_list = True
                    list_type = 'ol'
                content = re.sub(r'^\d+\.\s', '', stripped)
                result_lines.append(f'<li style="margin-bottom: 12px; line-height: 1.8; color: #333; font-size: 14px;">{content}</li>')
            else:
                if in_list:
                    result_lines.append(f'</{list_type}>')
                    in_list = False
                    list_type = None
                
                # 普通段落
                if stripped and not stripped.startswith('<'):
                    result_lines.append(f'<p style="margin: 0 0 15px 0; line-height: 1.8; color: #333; font-size: 14px;">{line}</p>')
                else:
                    result_lines.append(line)
        
        # 关闭未关闭的列表
        if in_list:
            result_lines.append(f'</{list_type}>')
        
        return '\n'.join(result_lines)
    
    def generate_html(
        self,
        report_data: Dict,
        report_date: date,
        overall_summary: str = ""
    ) -> str:
        """
        生成HTML格式报告
        
        Args:
            report_data: 报告数据
            report_date: 报告日期
            overall_summary: 总体总结
        
        Returns:
            HTML内容
        """
        template = self.jinja_env.get_template('report.html')
        
        html_content = template.render(
            report_date=report_date.strftime('%Y年%m月%d日'),
            categories=report_data['categories'],
            overall_summary=overall_summary,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # 保存HTML文件
        html_path = self.output_dir / f"report_{report_date}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML报告已保存: {html_path}")
        
        return html_content
    
    def generate_markdown(self, report_data: Dict, report_date: date) -> str:
        """
        生成 Markdown 格式报告
        
        Args:
            report_data: 报告数据
            report_date: 报告日期
        
        Returns:
            Markdown 内容
        """
        lines = []
        
        # 标题
        lines.append(f"# 金融日报 - {report_date.strftime('%Y年%m月%d日')}")
        lines.append("")
        lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 总体总结
        overall_summary = report_data.get('overall_summary', '')
        if overall_summary:
            lines.append("## 📋 每日综述")
            lines.append("")
            lines.append(overall_summary)
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # 各层面内容
        categories = report_data.get('categories', {})
        category_icons = {
            '政治': '🏛️',
            '经济': '💰',
            '技术': '🔬',
            '金融科技': '💳'
        }
        
        for category, icon in category_icons.items():
            data = categories.get(category, {})
            articles = data.get('articles', [])
            
            if not articles:
                continue
            
            lines.append(f"## {icon} {category}层面")
            lines.append("")
            
            # 层面总结
            if data.get('summary'):
                lines.append(f"**层面总结：** {data['summary']}")
                lines.append("")
            
            # 文章列表
            for i, article in enumerate(articles, 1):
                lines.append(f"### {i}. {article['title']}")
                lines.append("")
                
                # 元信息
                meta_parts = [f"**来源：** {article['source']}"]
                if article.get('publish_time'):
                    meta_parts.append(f"**发布时间：** {article['publish_time']}")
                if article.get('link'):
                    meta_parts.append(f"**链接：** [{article['link']}]({article['link']})")
                
                lines.append(" | ".join(meta_parts))
                lines.append("")
                
                # 摘要
                if article.get('summary'):
                    lines.append(f"**摘要：** {article['summary']}")
                    lines.append("")
                
                # 关键词
                if article.get('keywords'):
                    keywords_str = " | ".join([f"`{kw}`" for kw in article['keywords']])
                    lines.append(f"**关键词：** {keywords_str}")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        # 页脚
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*本报告由金融日报系统自动生成*")
        
        markdown_content = "\n".join(lines)
        
        # 保存Markdown文件
        md_path = self.output_dir / f"report_{report_date}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.logger.info(f"Markdown报告已保存: {md_path}")
        
        return markdown_content
