"""PDF 生成模块"""
from datetime import date
from pathlib import Path
from typing import Dict

from app.utils.logger import app_logger


class PDFGenerator:
    """PDF 生成器"""
    
    def __init__(self, output_dir: str = "data/reports"):
        """
        初始化 PDF 生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.logger = app_logger
    
    def generate_pdf(
        self,
        html_content: str,
        report_date: date,
        report_data: Dict = None,
        formatter=None
    ) -> str:
        """
        将HTML转换为PDF
        
        Args:
            html_content: HTML内容
            report_date: 报告日期
            report_data: 报告数据（用于生成简化的 PDF 模板）
            formatter: 格式转换器实例（用于生成 Markdown）
        
        Returns:
            PDF文件路径
        """
        pdf_filename = f"report_{report_date}.pdf"
        pdf_path = self.output_dir / pdf_filename
        
        # 方法1: 尝试使用 weasyprint（最佳质量，支持中文）
        if self._try_weasyprint(html_content, pdf_path):
            return str(pdf_path)
        
        # 方法2: 尝试使用 pdfkit（需要 wkhtmltopdf）
        if self._try_pdfkit(html_content, pdf_path):
            return str(pdf_path)
        
        # 方法3: 尝试使用 xhtml2pdf（使用简化模板）
        if report_data and self._try_xhtml2pdf(report_data, report_date, pdf_path):
            return str(pdf_path)
        
        # 方法4: 尝试从 Markdown 生成 PDF
        if report_data and formatter:
            try:
                self.logger.debug("尝试通过 Markdown 生成 PDF")
                return self._generate_from_markdown(report_data, report_date, formatter)
            except Exception as e:
                self.logger.debug(f"Markdown 转 PDF 失败: {e}")
        
        # 所有方法都失败
        self.logger.warning("PDF生成失败: 所有PDF库都不可用或失败。HTML报告已生成，可以手动转换为PDF。")
        return ""
    
    def _try_weasyprint(self, html_content: str, pdf_path: Path) -> bool:
        """尝试使用 weasyprint 生成 PDF"""
        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(str(pdf_path))
            self.logger.info(f"PDF报告已生成 (weasyprint): {pdf_path}")
            return True
        except ImportError:
            self.logger.debug("weasyprint未安装")
        except Exception as e:
            self.logger.debug(f"weasyprint生成失败: {e}")
        return False
    
    def _try_pdfkit(self, html_content: str, pdf_path: Path) -> bool:
        """尝试使用 pdfkit 生成 PDF"""
        try:
            import pdfkit
            options = {
                'encoding': 'UTF-8',
                'enable-local-file-access': None,
                'quiet': ''
            }
            pdfkit.from_string(html_content, str(pdf_path), options=options)
            self.logger.info(f"PDF报告已生成 (pdfkit): {pdf_path}")
            return True
        except ImportError:
            self.logger.debug("pdfkit未安装")
        except Exception as e:
            self.logger.debug(f"pdfkit生成失败: {e}")
        return False
    
    def _try_xhtml2pdf(self, report_data: Dict, report_date: date, pdf_path: Path) -> bool:
        """尝试使用 xhtml2pdf 生成 PDF"""
        try:
            from xhtml2pdf import pisa
            from jinja2 import Environment, FileSystemLoader
            from datetime import datetime
            
            # 使用简化的 PDF 模板
            jinja_env = Environment(
                loader=FileSystemLoader("templates"),
                autoescape=True
            )
            pdf_template = jinja_env.get_template('report_pdf.html')
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
                    return True
        except ImportError:
            self.logger.debug("xhtml2pdf未安装")
        except Exception as e:
            self.logger.debug(f"xhtml2pdf生成失败: {e}")
        return False
    
    def _generate_from_markdown(
        self,
        report_data: Dict,
        report_date: date,
        formatter
    ) -> str:
        """从 Markdown 生成 PDF"""
        # 生成 Markdown
        md_content = formatter.generate_markdown(report_data, report_date)
        md_path = self.output_dir / f"report_{report_date}.md"
        
        pdf_path = self.output_dir / f"report_{report_date}.pdf"
        
        # 尝试多种 Markdown 转 PDF 方法
        if self._try_pypandoc(md_path, pdf_path):
            return str(pdf_path)
        
        if self._try_markdown2_pdfkit(md_content, pdf_path):
            return str(pdf_path)
        
        raise Exception("所有 Markdown 转 PDF 方法都失败")
    
    def _try_pypandoc(self, md_path: Path, pdf_path: Path) -> bool:
        """尝试使用 pypandoc 转换"""
        try:
            import pypandoc
            
            extra_args = [
                '--pdf-engine=xelatex',
                '-V', 'CJKmainfont=SimSun',
                '-V', 'geometry:margin=2cm',
            ]
            
            pypandoc.convert_file(
                str(md_path),
                'pdf',
                outputfile=str(pdf_path),
                extra_args=extra_args
            )
            
            self.logger.info(f"PDF报告已生成 (pypandoc): {pdf_path}")
            return True
        except ImportError:
            self.logger.debug("pypandoc 未安装")
        except Exception as e:
            self.logger.debug(f"pypandoc 转换失败: {e}")
        return False
    
    def _try_markdown2_pdfkit(self, md_content: str, pdf_path: Path) -> bool:
        """尝试使用 markdown2 + pdfkit 转换"""
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
            return True
        except ImportError as e:
            self.logger.debug(f"markdown2 或 pdfkit 未安装: {e}")
        except Exception as e:
            self.logger.debug(f"markdown2+pdfkit 转换失败: {e}")
        return False
