"""报告生成服务"""
import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.summary import Summary
from app.models.daily_report import DailyReport
from app.utils.logger import app_logger


class ReportGenerator:
    """报告生成器 - 生成HTML和PDF格式的报告"""
    
    def __init__(
        self,
        db: Session,
        ai_service=None,
        template_dir: str = "templates",
        output_dir: str = "data/reports"
    ):
        """
        初始化报告生成器
        
        Args:
            db: 数据库会话
            ai_service: AI服务实例（用于生成层面总结）
            template_dir: 模板目录
            output_dir: 输出目录
        """
        self.db = db
        self.ai_service = ai_service
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.logger = app_logger
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化Jinja2环境
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
    
    def generate_daily_report(
        self,
        report_date: date,
        generate_category_summaries: bool = True,
        generate_pdf: bool = True
    ) -> DailyReport:
        """
        生成每日报告
        
        Args:
            report_date: 报告日期
            generate_category_summaries: 是否生成层面总结
            generate_pdf: 是否生成 PDF 文件（默认 True，但不在前端显示）
        
        Returns:
            DailyReport对象
        """
        self.logger.info(f"开始生成 {report_date} 的每日报告")
        
        # 检查是否已存在报告
        existing_report = self.db.query(DailyReport).filter(
            DailyReport.report_date == report_date
        ).first()
        
        if existing_report:
            self.logger.info(f"报告已存在，将更新: {report_date}")
        
        # 聚合报告数据
        report_data = self._aggregate_report_data(report_date)
        
        # 生成层面总结
        if generate_category_summaries and self.ai_service:
            self._generate_category_summaries(report_data)
        
        # 生成总体总结
        overall_summary = ""
        if self.ai_service:
            overall_summary = self._generate_overall_summary(report_data)
        
        # 生成HTML
        html_content = self.generate_html(report_data, report_date, overall_summary)
        
        # 生成PDF（后台生成，但不在前端显示和邮件发送）
        pdf_path = ""
        if generate_pdf:
            report_data_with_summary = {
                'categories': report_data['categories'],
                'overall_summary': overall_summary
            }
            try:
                pdf_path = self.generate_pdf(html_content, report_date, report_data_with_summary)
            except Exception as e:
                self.logger.warning(f"PDF 生成失败，继续处理: {e}")
                pdf_path = ""
        
        # 保存或更新报告
        if existing_report:
            existing_report.political_summary = report_data['categories'].get('政治', {}).get('summary', '')
            existing_report.economic_summary = report_data['categories'].get('经济', {}).get('summary', '')
            existing_report.technical_summary = report_data['categories'].get('技术', {}).get('summary', '')
            existing_report.fintech_summary = report_data['categories'].get('金融科技', {}).get('summary', '')
            existing_report.overall_summary = overall_summary
            existing_report.html_content = html_content
            existing_report.pdf_path = pdf_path
            report = existing_report
        else:
            report = DailyReport(
                report_date=report_date,
                political_summary=report_data['categories'].get('政治', {}).get('summary', ''),
                economic_summary=report_data['categories'].get('经济', {}).get('summary', ''),
                technical_summary=report_data['categories'].get('技术', {}).get('summary', ''),
                fintech_summary=report_data['categories'].get('金融科技', {}).get('summary', ''),
                overall_summary=overall_summary,
                html_content=html_content,
                pdf_path=pdf_path
            )
            self.db.add(report)
        
        self.db.commit()
        self.db.refresh(report)
        
        self.logger.info(f"报告生成完成: {report_date}")
        
        return report
    
    def _aggregate_report_data(self, report_date: date) -> Dict:
        """
        聚合报告数据
        
        Args:
            report_date: 报告日期
        
        Returns:
            报告数据字典
        """
        from sqlalchemy.orm import joinedload
        
        self.logger.info(f"聚合 {report_date} 的数据")
        
        # 查询指定日期的所有文章，预加载关系
        articles = self.db.query(Article).options(
            joinedload(Article.source)
        ).filter(
            Article.publish_time >= datetime.combine(report_date, datetime.min.time()),
            Article.publish_time < datetime.combine(report_date, datetime.max.time())
        ).all()
        
        self.logger.info(f"找到 {len(articles)} 篇文章")
        
        # 按层面分组
        categories = {
            '政治': {'articles': [], 'summary': ''},
            '经济': {'articles': [], 'summary': ''},
            '技术': {'articles': [], 'summary': ''},
            '金融科技': {'articles': [], 'summary': ''}
        }
        
        for article in articles:
            category = article.source.category
            if category in categories:
                # 获取摘要
                summary_obj = self.db.query(Summary).filter(
                    Summary.article_id == article.id
                ).first()
                
                article_data = {
                    'title': article.title,
                    'link': article.link,
                    'source': article.source.name,
                    'publish_time': article.publish_time.strftime('%Y-%m-%d %H:%M') if article.publish_time else '',
                    'summary': summary_obj.summary if summary_obj else '',
                    'keywords': json.loads(summary_obj.keywords) if summary_obj and summary_obj.keywords else []
                }
                
                categories[category]['articles'].append(article_data)
        
        # 统计
        for category, data in categories.items():
            self.logger.info(f"{category}层面: {len(data['articles'])} 篇文章")
        
        return {'categories': categories}
    
    def _generate_category_summaries(self, report_data: Dict):
        """
        生成各层面的总结
        
        Args:
            report_data: 报告数据
        """
        self.logger.info("生成层面总结")
        
        for category, data in report_data['categories'].items():
            if not data['articles']:
                continue
            
            # 收集该层面的所有摘要
            summaries = [
                article['summary']
                for article in data['articles']
                if article['summary']
            ]
            
            if summaries:
                # 使用AI生成层面总结
                try:
                    category_summary = self.ai_service.generate_daily_report(
                        {category: summaries}
                    )
                    data['summary'] = category_summary
                    self.logger.info(f"{category}层面总结生成成功")
                except Exception as e:
                    self.logger.error(f"{category}层面总结生成失败: {e}")
    
    def _generate_overall_summary(self, report_data: Dict) -> str:
        """
        生成总体总结
        
        Args:
            report_data: 报告数据
        
        Returns:
            总体总结文本
        """
        self.logger.info("生成总体总结")
        
        # 收集各层面的摘要
        summaries_by_category = {}
        for category, data in report_data['categories'].items():
            summaries = [
                article['summary']
                for article in data['articles']
                if article['summary']
            ]
            if summaries:
                summaries_by_category[category] = summaries
        
        if not summaries_by_category:
            return "暂无内容"
        
        try:
            overall_summary = self.ai_service.generate_daily_report(
                summaries_by_category
            )
            self.logger.info("总体总结生成成功")
            return overall_summary
        except Exception as e:
            self.logger.error(f"总体总结生成失败: {e}")
            return f"总结生成失败: {str(e)}"
    
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
    
    def generate_pdf(self, html_content: str, report_date: date, report_data: Dict = None) -> str:
        """
        将HTML转换为PDF
        
        Args:
            html_content: HTML内容（用于 weasyprint 和 pdfkit）
            report_date: 报告日期
            report_data: 报告数据（用于生成简化的 PDF 模板）
        
        Returns:
            PDF文件路径
        """
        pdf_filename = f"report_{report_date}.pdf"
        pdf_path = self.output_dir / pdf_filename
        
        # 方法1: 尝试使用 weasyprint（最佳质量，支持中文）
        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(str(pdf_path))
            self.logger.info(f"PDF报告已生成 (weasyprint): {pdf_path}")
            return str(pdf_path)
        except ImportError:
            self.logger.debug("weasyprint未安装")
        except Exception as e:
            self.logger.debug(f"weasyprint生成失败: {e}")
        
        # 方法2: 尝试使用 pdfkit（需要 wkhtmltopdf）
        try:
            import pdfkit
            options = {
                'encoding': 'UTF-8',
                'enable-local-file-access': None,
                'quiet': ''
            }
            pdfkit.from_string(html_content, str(pdf_path), options=options)
            self.logger.info(f"PDF报告已生成 (pdfkit): {pdf_path}")
            return str(pdf_path)
        except ImportError:
            self.logger.debug("pdfkit未安装")
        except Exception as e:
            self.logger.debug(f"pdfkit生成失败: {e}")
        
        # 方法3: 尝试使用 xhtml2pdf（使用简化模板）
        if report_data:
            try:
                from xhtml2pdf import pisa
                
                # 使用简化的 PDF 模板
                pdf_template = self.jinja_env.get_template('report_pdf.html')
                pdf_html = pdf_template.render(
                    report_date=report_date.strftime('%Y年%m月%d日'),
                    categories=report_data.get('categories', {}),
                    overall_summary=report_data.get('overall_summary', ''),
                    generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                
                with open(pdf_path, "wb") as pdf_file:
                    pisa_status = pisa.CreatePDF(
                        pdf_html.encode('utf-8'),
                        dest=pdf_file,
                        encoding='utf-8'
                    )
                    if not pisa_status.err:
                        self.logger.info(f"PDF报告已生成 (xhtml2pdf): {pdf_path}")
                        self.logger.warning("注意: xhtml2pdf 对复杂样式支持有限，建议安装 weasyprint 获得更好效果")
                        return str(pdf_path)
            except ImportError:
                self.logger.debug("xhtml2pdf未安装")
            except Exception as e:
                self.logger.debug(f"xhtml2pdf生成失败: {e}")
        
        # 方法4: 尝试从 Markdown 生成 PDF
        if report_data:
            try:
                self.logger.debug("尝试通过 Markdown 生成 PDF")
                return self._generate_pdf_from_markdown(report_data, report_date)
            except Exception as e:
                self.logger.debug(f"Markdown 转 PDF 失败: {e}")
        
        # 所有方法都失败
        self.logger.warning("PDF生成失败: 所有PDF库都不可用或失败。HTML报告已生成，可以手动转换为PDF。")
        return ""
    
    def _generate_pdf_from_markdown(self, report_data: Dict, report_date: date) -> str:
        """
        通过 Markdown 生成 PDF
        
        Args:
            report_data: 报告数据
            report_date: 报告日期
        
        Returns:
            PDF文件路径
        """
        # 生成 Markdown
        md_content = self.generate_markdown(report_data, report_date)
        md_path = self.output_dir / f"report_{report_date}.md"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        self.logger.info(f"Markdown 报告已保存: {md_path}")
        
        pdf_path = self.output_dir / f"report_{report_date}.pdf"
        
        # 方法1: 使用 pypandoc
        try:
            import pypandoc
            
            # 配置 pandoc 选项
            extra_args = [
                '--pdf-engine=xelatex',  # 使用 xelatex 支持中文
                '-V', 'CJKmainfont=SimSun',  # 设置中文字体
                '-V', 'geometry:margin=2cm',  # 设置页边距
            ]
            
            pypandoc.convert_file(
                str(md_path),
                'pdf',
                outputfile=str(pdf_path),
                extra_args=extra_args
            )
            
            self.logger.info(f"PDF报告已生成 (pypandoc): {pdf_path}")
            return str(pdf_path)
            
        except ImportError:
            self.logger.debug("pypandoc 未安装")
        except Exception as e:
            self.logger.debug(f"pypandoc 转换失败: {e}")
        
        # 方法2: 使用 markdown2 + pdfkit
        try:
            import markdown2
            import pdfkit
            
            # 将 Markdown 转换为 HTML
            html_content = markdown2.markdown(
                md_content,
                extras=['tables', 'fenced-code-blocks', 'header-ids']
            )
            
            # 添加 CSS 样式
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'SimSun', 'Microsoft YaHei', sans-serif;
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 40px auto;
                        padding: 20px;
                    }}
                    h1, h2, h3 {{ color: #2c3e50; }}
                    h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                    h2 {{ border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; margin-top: 30px; }}
                    code {{ background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
                    pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                    blockquote {{ border-left: 4px solid #3498db; padding-left: 15px; color: #555; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #3498db; color: white; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            options = {
                'encoding': 'UTF-8',
                'enable-local-file-access': None,
                'quiet': ''
            }
            
            pdfkit.from_string(styled_html, str(pdf_path), options=options)
            self.logger.info(f"PDF报告已生成 (markdown2+pdfkit): {pdf_path}")
            return str(pdf_path)
            
        except ImportError as e:
            self.logger.debug(f"markdown2 或 pdfkit 未安装: {e}")
        except Exception as e:
            self.logger.debug(f"markdown2+pdfkit 转换失败: {e}")
        
        # 方法3: 使用 markdown + reportlab
        try:
            import markdown
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # 注册中文字体（如果可用）
            try:
                pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
                font_name = 'SimSun'
            except:
                font_name = 'Helvetica'
            
            # 创建 PDF
            doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # 自定义样式
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=font_name,
                fontSize=24,
                spaceAfter=30,
            )
            
            # 添加标题
            title = Paragraph(f"金融日报 - {report_date.strftime('%Y年%m月%d日')}", title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # 简化内容（reportlab 对复杂格式支持有限）
            for line in md_content.split('\n'):
                if line.strip():
                    try:
                        p = Paragraph(line, styles['Normal'])
                        story.append(p)
                        story.append(Spacer(1, 6))
                    except:
                        pass
            
            doc.build(story)
            self.logger.info(f"PDF报告已生成 (markdown+reportlab): {pdf_path}")
            return str(pdf_path)
            
        except ImportError:
            self.logger.debug("markdown 或 reportlab 未安装")
        except Exception as e:
            self.logger.debug(f"markdown+reportlab 转换失败: {e}")
        
        raise Exception("所有 Markdown 转 PDF 方法都失败")
    
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
        
        return "\n".join(lines)
    
    def _simplify_html_for_xhtml2pdf(self, html_content: str) -> str:
        """
        简化 HTML 以提高 xhtml2pdf 兼容性
        
        Args:
            html_content: 原始 HTML
        
        Returns:
            简化后的 HTML
        """
        # 移除复杂的 CSS（渐变等）
        import re
        
        # 移除渐变背景
        html_content = re.sub(
            r'background:\s*linear-gradient\([^)]+\);',
            'background-color: #667eea;',
            html_content
        )
        
        # 移除 box-shadow
        html_content = re.sub(
            r'box-shadow:[^;]+;',
            '',
            html_content
        )
        
        # 移除 transition
        html_content = re.sub(
            r'transition:[^;]+;',
            '',
            html_content
        )
        
        return html_content
    
    def generate_markdown(self, report_data: Dict, report_date: date) -> str:
        """
        生成Markdown格式报告
        
        Args:
            report_data: 报告数据
            report_date: 报告日期
        
        Returns:
            Markdown内容
        """
        lines = []
        
        # 标题
        lines.append(f"# 金融日报 - {report_date.strftime('%Y年%m月%d日')}")
        lines.append("")
        
        # 各层面内容
        for category, data in report_data['categories'].items():
            if not data['articles']:
                continue
            
            lines.append(f"## {category}层面")
            lines.append("")
            
            if data['summary']:
                lines.append(f"**层面总结：** {data['summary']}")
                lines.append("")
            
            for i, article in enumerate(data['articles'], 1):
                lines.append(f"### {i}. {article['title']}")
                lines.append("")
                lines.append(f"**来源：** {article['source']}")
                if article['publish_time']:
                    lines.append(f"**发布时间：** {article['publish_time']}")
                lines.append(f"**链接：** [{article['link']}]({article['link']})")
                lines.append("")
                
                if article['summary']:
                    lines.append(f"**摘要：** {article['summary']}")
                    lines.append("")
                
                if article['keywords']:
                    keywords_str = " | ".join([f"`{kw}`" for kw in article['keywords']])
                    lines.append(f"**关键词：** {keywords_str}")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        markdown_content = "\n".join(lines)
        
        # 保存Markdown文件
        md_path = self.output_dir / f"report_{report_date}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.logger.info(f"Markdown报告已保存: {md_path}")
        
        return markdown_content
