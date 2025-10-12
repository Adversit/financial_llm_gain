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
        generate_category_summaries: bool = True
    ) -> DailyReport:
        """
        生成每日报告
        
        Args:
            report_date: 报告日期
            generate_category_summaries: 是否生成层面总结
        
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
        
        # 生成PDF
        pdf_path = self.generate_pdf(html_content, report_date)
        
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
        self.logger.info(f"聚合 {report_date} 的数据")
        
        # 查询指定日期的所有文章
        articles = self.db.query(Article).filter(
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
    
    def generate_pdf(self, html_content: str, report_date: date) -> str:
        """
        将HTML转换为PDF
        
        Args:
            html_content: HTML内容
            report_date: 报告日期
        
        Returns:
            PDF文件路径
        """
        pdf_filename = f"report_{report_date}.pdf"
        pdf_path = self.output_dir / pdf_filename
        
        try:
            # 使用weasyprint生成PDF
            from weasyprint import HTML
            
            HTML(string=html_content).write_pdf(str(pdf_path))
            
            self.logger.info(f"PDF报告已生成: {pdf_path}")
            
            return str(pdf_path)
            
        except ImportError:
            self.logger.warning("weasyprint未安装，跳过PDF生成")
            return ""
        except Exception as e:
            self.logger.error(f"PDF生成失败: {e}")
            return ""
    
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
