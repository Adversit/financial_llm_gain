"""报告生成器主模块"""
from datetime import date
from pathlib import Path
from typing import Dict
from sqlalchemy.orm import Session

from app.models.daily_report import DailyReport
from app.utils.logger import app_logger
from .aggregator import ReportAggregator
from .formatter import ReportFormatter
from .pdf_generator import PDFGenerator


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
        self.output_dir = Path(output_dir)
        self.logger = app_logger
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化子模块
        self.aggregator = ReportAggregator(db)
        self.formatter = ReportFormatter(template_dir, output_dir)
        self.pdf_generator = PDFGenerator(output_dir)
    
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
            generate_pdf: 是否生成 PDF 文件
        
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
        report_data = self.aggregator.aggregate_report_data(report_date)
        
        # 生成层面总结
        if generate_category_summaries and self.ai_service:
            self._generate_category_summaries(report_data)
        
        # 生成总体总结
        overall_summary = ""
        if self.ai_service:
            overall_summary = self._generate_overall_summary(report_data)
        
        # 生成HTML
        html_content = self.formatter.generate_html(report_data, report_date, overall_summary)
        
        # 生成PDF
        pdf_path = ""
        if generate_pdf:
            report_data_with_summary = {
                'categories': report_data['categories'],
                'overall_summary': overall_summary
            }
            try:
                pdf_path = self.pdf_generator.generate_pdf(
                    html_content,
                    report_date,
                    report_data_with_summary,
                    self.formatter
                )
            except Exception as e:
                self.logger.warning(f"PDF 生成失败，继续处理: {e}")
                pdf_path = ""
        
        # 保存或更新报告
        report = self._save_report(
            existing_report,
            report_date,
            report_data,
            overall_summary,
            html_content,
            pdf_path
        )
        
        # 生成词云
        self._generate_wordclouds(report_date)
        
        self.logger.info(f"报告生成完成: {report_date}")
        
        return report
    
    def _generate_category_summaries(self, report_data: Dict):
        """生成各层面的总结"""
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
                try:
                    category_summary = self.ai_service.generate_daily_report(
                        {category: summaries}
                    )
                    data['summary'] = category_summary
                    self.logger.info(f"{category}层面总结生成成功")
                except Exception as e:
                    self.logger.error(f"{category}层面总结生成失败: {e}")
    
    def _generate_overall_summary(self, report_data: Dict) -> str:
        """生成总体总结"""
        self.logger.info("生成总体总结")
        
        # 收集各层面的摘要
        summaries_by_category = {}
        all_articles = []
        
        for category, data in report_data['categories'].items():
            summaries = [
                article['summary']
                for article in data['articles']
                if article['summary']
            ]
            if summaries:
                summaries_by_category[category] = summaries
            
            # 收集所有文章数据（包含关键词）
            for article in data['articles']:
                all_articles.append({
                    'title': article['title'],
                    'summary': article['summary'],
                    'keywords': article['keywords']
                })
        
        if not summaries_by_category:
            return "暂无内容"
        
        try:
            overall_summary = self.ai_service.generate_daily_report(
                summaries_by_category,
                articles_data=all_articles
            )
            
            # 将文本格式转换为 HTML
            overall_summary = self.formatter.format_summary_to_html(overall_summary)
            
            self.logger.info("总体总结生成成功")
            return overall_summary
        except Exception as e:
            self.logger.error(f"总体总结生成失败: {e}")
            return f"总结生成失败: {str(e)}"
    
    def _save_report(
        self,
        existing_report,
        report_date: date,
        report_data: Dict,
        overall_summary: str,
        html_content: str,
        pdf_path: str
    ) -> DailyReport:
        """保存或更新报告"""
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
        
        return report
    
    def _generate_wordclouds(self, report_date: date):
        """生成词云"""
        try:
            from app.services.wordcloud_service import wordcloud_service
            wordcloud_service.generate_daily_wordclouds(report_date)
            self.logger.info(f"词云生成完成: {report_date}")
        except Exception as e:
            self.logger.warning(f"词云生成失败: {e}")
