"""邮件发送服务"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional
from datetime import date

from app.utils.logger import email_logger


class EmailSender:
    """邮件发送器 - 使用SMTP发送邮件"""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        use_ssl: bool = True,
        from_name: str = "金融日报系统"
    ):
        """
        初始化邮件发送器
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            username: 发件人邮箱
            password: 邮箱密码或授权码
            use_ssl: 是否使用SSL
            from_name: 发件人名称
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.from_name = from_name
        self.logger = email_logger
    
    def send_report(
        self,
        recipients: List[str],
        report_date: date,
        html_content: str = None,
        pdf_path: Optional[str] = None,
        attach_pdf: bool = False,  # 默认不附加 PDF
        report_data: dict = None,  # 报告数据字典（包含文章列表）
        max_retries: int = 3
    ) -> bool:
        """
        发送报告邮件
        
        Args:
            recipients: 收件人列表
            report_date: 报告日期
            html_content: HTML格式的报告内容（可选，如果提供 report_data 则忽略）
            pdf_path: PDF附件路径（可选）
            attach_pdf: 是否附加 PDF（默认 False）
            report_data: 报告数据字典（可选，用于渲染邮件模板）
            max_retries: 最大重试次数
        
        Returns:
            是否发送成功
        """
        if not recipients:
            self.logger.warning("收件人列表为空，跳过发送")
            return False
        
        self.logger.info(f"准备发送邮件给 {len(recipients)} 个收件人")
        
        # 如果提供了 report_data，使用完整模板渲染（包含文章列表）
        if report_data:
            html_content = self._render_full_email_template(report_data, report_date)
        
        # 如果没有 html_content，记录警告
        if not html_content:
            self.logger.warning("没有提供 HTML 内容或报告数据")
        
        # 构建邮件
        subject = f"金融日报 - {report_date.strftime('%Y年%m月%d日')}"
        
        for attempt in range(max_retries):
            try:
                msg = self._build_message(
                    recipients=recipients,
                    subject=subject,
                    html_content=html_content,
                    pdf_path=None  # 禁用 PDF 附件
                )
                
                # 发送邮件
                self._send_message(msg, recipients)
                
                self.logger.info(f"邮件发送成功: {', '.join(recipients)}")
                return True
                
            except Exception as e:
                self.logger.error(f"邮件发送失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    self.logger.error(f"邮件发送最终失败: {e}")
                    return False
    
    def _build_message(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        pdf_path: Optional[str] = None
    ) -> MIMEMultipart:
        """
        构建邮件消息
        
        Args:
            recipients: 收件人列表
            subject: 邮件主题
            html_content: HTML内容
            pdf_path: PDF附件路径
        
        Returns:
            邮件消息对象
        """
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.from_name} <{self.username}>"
        msg['To'] = ', '.join(recipients)
        
        # 优化 HTML 以适配邮件客户端
        html_content = self._optimize_html_for_email(html_content)
        
        # 添加HTML内容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 添加PDF附件
        if pdf_path and Path(pdf_path).exists():
            try:
                with open(pdf_path, 'rb') as f:
                    pdf_data = f.read()
                
                pdf_part = MIMEApplication(pdf_data, _subtype='pdf')
                pdf_filename = Path(pdf_path).name
                pdf_part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=('utf-8', '', pdf_filename)
                )
                msg.attach(pdf_part)
                
                self.logger.info(f"已添加PDF附件: {pdf_filename}")
                
            except Exception as e:
                self.logger.warning(f"添加PDF附件失败: {e}")
        
        return msg
    
    def _render_full_email_template(self, report_data: dict, report_date: date) -> str:
        """
        使用完整模板渲染邮件内容（包含所有文章）
        
        Args:
            report_data: 报告数据字典（包含 categories 和 articles）
            report_date: 报告日期
        
        Returns:
            渲染后的 HTML
        """
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime
        
        # 初始化 Jinja2 环境
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('email_full_report.html')
        
        # 准备层面数据（添加颜色、图标和 CSS 类名）
        # 使用更鲜艳的纯色，适配邮件客户端
        category_config = {
            '政治': {'color': '#dc2626', 'icon': '🏛️', 'css_class': 'political'},  # 粉红色
            '经济': {'color': '#2563eb', 'icon': '�',  'css_class': 'economic'},  # 蓝色
            '技术': {'color': '#059669', 'icon': '🔬', 'css_class': 'technical'},  # 绿色
            '金融科技': {'color': '#d97706', 'icon': '💳', 'css_class': 'fintech'}  # 橙色
        }
        
        # 导入 formatter 用于格式化层面总结
        from app.services.report.formatter import ReportFormatter
        formatter = ReportFormatter()
        
        categories = {}
        for category_name, config in category_config.items():
            if category_name in report_data.get('categories', {}):
                category_data = report_data['categories'][category_name]
                
                # 格式化层面总结为 HTML
                summary_text = category_data.get('summary', '')
                if summary_text:
                    summary_html = formatter.format_summary_to_html(summary_text)
                else:
                    summary_html = ''
                
                categories[category_name] = {
                    'articles': category_data.get('articles', []),
                    'summary': summary_html,
                    'color': config['color'],
                    'icon': config['icon'],
                    'css_class': config['css_class']
                }
        
        # 渲染模板
        html_content = template.render(
            report_date=report_date.strftime('%Y年%m月%d日'),
            overall_summary=report_data.get('overall_summary', ''),
            categories=categories,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return html_content
    
    def _render_email_template(self, report_data: dict, report_date: date) -> str:
        """
        使用 Jinja2 模板渲染邮件内容
        
        Args:
            report_data: 报告数据字典
            report_date: 报告日期
        
        Returns:
            渲染后的 HTML
        """
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime
        
        # 将纯文本总结转换为 HTML
        overall_summary = self._text_to_html(report_data.get('overall_summary', ''))
        political_summary = self._text_to_html(report_data.get('political_summary', ''))
        economic_summary = self._text_to_html(report_data.get('economic_summary', ''))
        technical_summary = self._text_to_html(report_data.get('technical_summary', ''))
        fintech_summary = self._text_to_html(report_data.get('fintech_summary', ''))
        
        # 初始化 Jinja2 环境
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('email_report.html')
        
        # 渲染模板
        html_content = template.render(
            report_date=report_date.strftime('%Y年%m月%d日'),
            overall_summary=overall_summary,
            political_summary=political_summary,
            economic_summary=economic_summary,
            technical_summary=technical_summary,
            fintech_summary=fintech_summary,
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return html_content
    
    def _text_to_html(self, text: str) -> str:
        """
        将纯文本或混合格式转换为 HTML
        
        Args:
            text: 纯文本或包含 HTML 标签的文本
        
        Returns:
            HTML 格式文本
        """
        if not text:
            return ''
        
        # 如果已经包含 HTML 标签，直接返回（添加内联样式）
        if '<p>' in text or '<h3>' in text or '<ul>' in text:
            return self._add_inline_styles(text)
        
        # 否则，将纯文本转换为 HTML
        import re
        
        lines = text.split('\n')
        html_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                continue
            
            # 标题（一、二、三、四）
            if re.match(r'^[一二三四]、', stripped):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h3 style="margin: 20px 0 15px 0; color: #2c3e50; font-size: 18px; font-weight: bold;">{stripped}</h3>')
            # 子标题（【xxx】）
            elif stripped.startswith('【') and '】' in stripped:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h4 style="margin: 15px 0 10px 0; color: #34495e; font-size: 16px; font-weight: bold;">{stripped}</h4>')
            # 列表项（- 开头）
            elif stripped.startswith('- '):
                if not in_list:
                    html_lines.append('<ul style="margin: 10px 0 20px 0; padding-left: 25px;">')
                    in_list = True
                html_lines.append(f'<li style="margin-bottom: 10px; line-height: 1.8; color: #333;">{stripped[2:]}</li>')
            # 数字列表项
            elif re.match(r'^\d+\.\s', stripped):
                if not in_list:
                    html_lines.append('<ol style="margin: 10px 0 20px 0; padding-left: 25px;">')
                    in_list = True
                content = re.sub(r'^\d+\.\s', '', stripped)
                html_lines.append(f'<li style="margin-bottom: 10px; line-height: 1.8; color: #333;">{content}</li>')
            # 普通段落
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<p style="margin: 0 0 15px 0; line-height: 1.8; color: #333;">{stripped}</p>')
        
        # 关闭未关闭的列表
        if in_list:
            html_lines.append('</ul>')
        
        return '\n'.join(html_lines)
    
    def _add_inline_styles(self, html_content: str) -> str:
        """
        为 HTML 内容添加内联样式
        
        Args:
            html_content: HTML 内容
        
        Returns:
            添加样式后的 HTML
        """
        # 为标签添加内联样式
        html_content = html_content.replace('<p>', '<p style="margin: 0 0 15px 0; line-height: 1.8; color: #333;">')
        html_content = html_content.replace('<h3>', '<h3 style="margin: 20px 0 15px 0; color: #2c3e50; font-size: 18px; font-weight: bold;">')
        html_content = html_content.replace('<h4>', '<h4 style="margin: 15px 0 10px 0; color: #34495e; font-size: 16px; font-weight: bold;">')
        html_content = html_content.replace('<ul>', '<ul style="margin: 10px 0 20px 0; padding-left: 25px;">')
        html_content = html_content.replace('<ol>', '<ol style="margin: 10px 0 20px 0; padding-left: 25px;">')
        html_content = html_content.replace('<li>', '<li style="margin-bottom: 10px; line-height: 1.8; color: #333;">')
        html_content = html_content.replace('<strong>', '<strong style="color: #2c3e50; font-weight: bold;">')
        html_content = html_content.replace('<hr>', '<hr style="margin: 20px 0; border: none; border-top: 1px solid #ecf0f1;">')
        
        return html_content
    
    def _optimize_html_for_email(self, html_content: str) -> str:
        """
        优化 HTML 以适配邮件客户端
        将复杂的 HTML 转换为邮件友好的格式
        
        Args:
            html_content: 原始 HTML
        
        Returns:
            优化后的 HTML
        """
        import re
        import html as html_module
        from bs4 import BeautifulSoup
        
        # 检查是否已经有完整的 HTML 结构
        has_html_tag = '<html' in html_content.lower()
        
        # 如果 HTML 包含我们的新模板标记（品牌条），直接返回，不做优化
        if '<!-- 顶部品牌条 -->' in html_content or 'bgcolor="#1a237e"' in html_content:
            self.logger.info("检测到新版邮件模板，跳过优化")
            return html_content
        
        if has_html_tag:
            # 提取 body 内容
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
            if body_match:
                html_content = body_match.group(1)
        
        # 解码 HTML 实体
        html_content = html_module.unescape(html_content)
        
        # 使用 BeautifulSoup 解析 HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除 <style> 标签（邮件客户端不支持）
            for style in soup.find_all('style'):
                style.decompose()
            
            # 移除 <script> 标签
            for script in soup.find_all('script'):
                script.decompose()
            
            # 转换渐变背景为纯色背景（使用 bgcolor 属性，邮件客户端支持更好）
            for element in soup.find_all(class_='category-header'):
                # 移除渐变，使用纯色
                if 'political' in element.get('class', []):
                    element['bgcolor'] = '#dc2626'
                    element['style'] = 'color: white; padding: 15px 20px; margin-bottom: 20px;'
                elif 'economic' in element.get('class', []):
                    element['bgcolor'] = '#00f2fe'
                    element['style'] = 'color: white; padding: 15px 20px; margin-bottom: 20px;'
                elif 'technical' in element.get('class', []):
                    element['bgcolor'] = '#38f9d7'
                    element['style'] = 'color: white; padding: 15px 20px; margin-bottom: 20px;'
                elif 'fintech' in element.get('class', []):
                    element['bgcolor'] = '#fee140'
                    element['style'] = 'color: white; padding: 15px 20px; margin-bottom: 20px;'
            
            # 为 header 添加内联样式
            for element in soup.find_all(class_='header'):
                element['style'] = 'text-align: center; padding-bottom: 20px; margin-bottom: 30px; border-bottom: 3px solid #2c3e50;'
            
            # 为 summary-section 添加内联样式（总体总结，使用 bgcolor）
            for element in soup.find_all(class_='summary-section'):
                element['bgcolor'] = '#ecf0f1'
                element['style'] = 'padding: 20px; margin-bottom: 30px;'
            
            # 为 category-section 添加间距
            for element in soup.find_all(class_='category-section'):
                element['style'] = 'margin-bottom: 40px;'
            
            # 为 category-summary 添加内联样式
            for element in soup.find_all(class_='category-summary'):
                element['bgcolor'] = '#f8f9fa'
                element['style'] = 'padding: 15px; border-left: 4px solid #667eea; margin-bottom: 20px;'
            
            # 为 article-list 添加样式
            for element in soup.find_all(class_='article-list'):
                element['style'] = 'margin-left: 0;'
            
            # 为 article-item 添加内联样式
            for element in soup.find_all(class_='article-item'):
                element['bgcolor'] = '#ffffff'
                element['style'] = 'margin-bottom: 25px; padding: 15px; border: 1px solid #e0e0e0;'
            
            # 为 article-title 添加内联样式
            for element in soup.find_all(class_='article-title'):
                element['style'] = 'font-size: 17px; font-weight: bold; color: #2c3e50; margin-bottom: 12px; line-height: 1.4;'
            
            # 为 article-meta 添加内联样式
            for element in soup.find_all(class_='article-meta'):
                element['style'] = 'font-size: 13px; color: #7f8c8d; margin-bottom: 12px;'
            
            # 为 article-summary 添加内联样式
            for element in soup.find_all(class_='article-summary'):
                element['style'] = 'font-size: 14px; line-height: 1.7; color: #555; margin-bottom: 12px; text-align: justify;'
            
            # 为 article-keywords 添加样式
            for element in soup.find_all(class_='article-keywords'):
                element['style'] = 'margin-top: 12px;'
            
            # 为 keyword 添加内联样式
            for element in soup.find_all(class_='keyword'):
                element['bgcolor'] = '#3498db'
                element['style'] = 'display: inline-block; color: white; padding: 4px 12px; font-size: 13px; margin-right: 8px; margin-bottom: 5px;'
            
            # 为链接添加样式
            for link in soup.find_all('a'):
                current_style = link.get('style', '')
                if 'color:' not in current_style:
                    link['style'] = current_style + ' color: #3498db; text-decoration: none;'
            
            # 为所有 h2 添加样式
            for h2 in soup.find_all('h2'):
                if not h2.get('style'):
                    h2['style'] = 'font-size: 22px; color: #2c3e50; margin: 0 0 15px 0; font-weight: bold;'
            
            # 为所有 h3 添加样式
            for h3 in soup.find_all('h3'):
                if not h3.get('style') or 'margin:' not in h3.get('style', ''):
                    h3['style'] = 'font-size: 18px; color: white; margin: 0; font-weight: bold;'
            
            html_content = str(soup)
            
        except Exception as e:
            self.logger.warning(f"HTML 优化失败，使用原始内容: {e}")
        
        # 为所有标签添加内联样式（邮件客户端需要）
        # 使用正则表达式处理已有样式的标签
        
        # 处理段落
        html_content = re.sub(
            r'<p(?:\s[^>]*)?>',
            '<p style="margin: 0 0 15px 0; line-height: 1.8; color: #333; font-size: 14px;">',
            html_content
        )
        
        # 处理标题
        html_content = re.sub(
            r'<h1(?:\s[^>]*)?>',
            '<h1 style="margin: 30px 0 20px 0; color: #2c3e50; font-size: 28px; font-weight: bold; line-height: 1.4;">',
            html_content
        )
        html_content = re.sub(
            r'<h2(?:\s[^>]*)?>',
            '<h2 style="margin: 25px 0 15px 0; color: #2c3e50; font-size: 24px; font-weight: bold; line-height: 1.4;">',
            html_content
        )
        html_content = re.sub(
            r'<h3(?:\s[^>]*)?>',
            '<h3 style="margin: 25px 0 15px 0; padding-bottom: 10px; border-bottom: 2px solid #ecf0f1; color: #2c3e50; font-size: 20px; font-weight: bold; line-height: 1.4;">',
            html_content
        )
        html_content = re.sub(
            r'<h4(?:\s[^>]*)?>',
            '<h4 style="margin: 20px 0 12px 0; color: #34495e; font-size: 18px; font-weight: bold; line-height: 1.4;">',
            html_content
        )
        html_content = re.sub(
            r'<h5(?:\s[^>]*)?>',
            '<h5 style="margin: 18px 0 10px 0; color: #34495e; font-size: 16px; font-weight: bold; line-height: 1.4;">',
            html_content
        )
        html_content = re.sub(
            r'<h6(?:\s[^>]*)?>',
            '<h6 style="margin: 15px 0 8px 0; color: #34495e; font-size: 14px; font-weight: bold; line-height: 1.4;">',
            html_content
        )
        
        # 处理列表
        html_content = re.sub(
            r'<ul(?:\s[^>]*)?>',
            '<ul style="margin: 15px 0 20px 0; padding-left: 25px; list-style-type: disc;">',
            html_content
        )
        html_content = re.sub(
            r'<ol(?:\s[^>]*)?>',
            '<ol style="margin: 15px 0 20px 0; padding-left: 25px;">',
            html_content
        )
        html_content = re.sub(
            r'<li(?:\s[^>]*)?>',
            '<li style="margin-bottom: 12px; line-height: 1.8; color: #333; font-size: 14px;">',
            html_content
        )
        
        # 处理其他元素
        html_content = re.sub(
            r'<hr(?:\s[^>]*)?/?>',
            '<hr style="margin: 30px 0; border: none; border-top: 2px solid #ecf0f1;">',
            html_content
        )
        html_content = re.sub(
            r'<strong(?:\s[^>]*)?>',
            '<strong style="color: #2c3e50; font-weight: bold;">',
            html_content
        )
        html_content = re.sub(
            r'<em(?:\s[^>]*)?>',
            '<em style="color: #7f8c8d; font-style: italic;">',
            html_content
        )
        
        # 处理 div 容器
        html_content = re.sub(
            r'<div(?:\s[^>]*)?>',
            '<div style="margin-bottom: 15px;">',
            html_content
        )
        
        # 处理表格（如果有）
        html_content = re.sub(
            r'<table(?:\s[^>]*)?>',
            '<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">',
            html_content
        )
        html_content = re.sub(
            r'<td(?:\s[^>]*)?>',
            '<td style="padding: 8px 12px; border: 1px solid #ddd; font-size: 14px;">',
            html_content
        )
        html_content = re.sub(
            r'<th(?:\s[^>]*)?>',
            '<th style="padding: 10px 12px; border: 1px solid #ddd; background-color: #f8f9fa; font-weight: bold; font-size: 14px;">',
            html_content
        )
        
        # 为 overall_summary 内容添加紫色背景容器（模仿前端样式）
        # 检查是否有 summary-section 或直接的内容
        if '<div class="summary-section">' in html_content or '<h2>📋 每日综述</h2>' in html_content:
            # 提取总结内容并添加样式
            html_content = html_content.replace(
                '<div class="summary-section">',
                '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 3rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
            )
            html_content = html_content.replace(
                '<h2>📋 每日综述</h2>',
                '<h2 style="margin-top: 0; margin-bottom: 1.5rem; font-size: 24px; border-bottom: 2px solid rgba(255,255,255,0.3); padding-bottom: 0.5rem; color: white;">📋 每日综述</h2>'
            )
        
        # 用邮件友好的模板包装（使用表格布局）
        email_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>金融日报</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Microsoft YaHei', 'SimHei', Arial, sans-serif; background-color: #f5f5f5;">
    <!-- 外层容器 -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f5f5f5; padding: 20px 0;">
        <tr>
            <td align="center">
                <!-- 主内容容器 -->
                <table width="700" cellpadding="0" cellspacing="0" border="0" style="max-width: 700px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- 头部 -->
                    <tr>
                        <td style="padding: 30px 30px 20px 30px; text-align: center; border-bottom: 3px solid #667eea;">
                            <h1 style="margin: 0; font-size: 28px; color: #2c3e50; font-weight: bold;">📊 金融日报</h1>
                        </td>
                    </tr>
                    <!-- 内容区域 -->
                    <tr>
                        <td style="padding: 30px; font-size: 14px; line-height: 1.8; color: #333;">
                            {html_content}
                        </td>
                    </tr>
                    <!-- 页脚 -->
                    <tr>
                        <td style="padding: 20px 30px; text-align: center; border-top: 1px solid #e0e0e0; background-color: #f8f9fa;">
                            <p style="margin: 0; font-size: 13px; color: #7f8c8d;">
                                金融日报系统 | 自动生成
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
        
        return email_html
    
    def _send_message(self, msg: MIMEMultipart, recipients: List[str]):
        """
        发送邮件消息
        
        Args:
            msg: 邮件消息对象
            recipients: 收件人列表
        """
        if self.use_ssl:
            # 使用SSL连接
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.login(self.username, self.password)
                server.send_message(msg, self.username, recipients)
        else:
            # 使用TLS连接
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg, self.username, recipients)
    
    def send_test_email(self, recipient: str) -> bool:
        """
        发送测试邮件
        
        Args:
            recipient: 收件人邮箱
        
        Returns:
            是否发送成功
        """
        self.logger.info(f"发送测试邮件到: {recipient}")
        
        subject = "金融日报系统 - 测试邮件"
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2c3e50;">📧 测试邮件</h2>
            <p>这是一封来自金融日报系统的测试邮件。</p>
            <p>如果您收到这封邮件，说明邮件配置正确。</p>
            <hr style="border: 1px solid #e0e0e0; margin: 20px 0;">
            <p style="color: #7f8c8d; font-size: 14px;">
                金融日报系统 | 自动发送
            </p>
        </body>
        </html>
        """
        
        try:
            msg = self._build_message(
                recipients=[recipient],
                subject=subject,
                html_content=html_content
            )
            
            self._send_message(msg, [recipient])
            
            self.logger.info("测试邮件发送成功")
            return True
            
        except Exception as e:
            self.logger.error(f"测试邮件发送失败: {e}")
            return False
    
    def send_custom_email(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        发送自定义邮件
        
        Args:
            recipients: 收件人列表
            subject: 邮件主题
            html_content: HTML内容
            attachments: 附件路径列表
        
        Returns:
            是否发送成功
        """
        self.logger.info(f"发送自定义邮件: {subject}")
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.username}>"
            msg['To'] = ', '.join(recipients)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加附件
            if attachments:
                for attachment_path in attachments:
                    if Path(attachment_path).exists():
                        try:
                            with open(attachment_path, 'rb') as f:
                                attachment_data = f.read()
                            
                            attachment_part = MIMEApplication(attachment_data)
                            filename = Path(attachment_path).name
                            attachment_part.add_header(
                                'Content-Disposition',
                                'attachment',
                                filename=('utf-8', '', filename)
                            )
                            msg.attach(attachment_part)
                            
                        except Exception as e:
                            self.logger.warning(f"添加附件失败 {attachment_path}: {e}")
            
            # 发送
            self._send_message(msg, recipients)
            
            self.logger.info("自定义邮件发送成功")
            return True
            
        except Exception as e:
            self.logger.error(f"自定义邮件发送失败: {e}")
            return False
