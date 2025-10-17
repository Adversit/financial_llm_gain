"""
测试报告生成和邮件发送功能
检查：
1. 前端报告是否被覆盖
2. 邮件读取的格式是否正确
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.article import Article
from app.models.summary import Summary
from app.models.daily_report import DailyReport
from app.services.report_service import ReportGenerator
from app.services.email_service import EmailSender
from app.config import get_config
from app.services.ai_service import AIService


class TestReportAndEmail:
    def __init__(self):
        self.db = SessionLocal()
        self.config = get_config()
        
        # 初始化 AI 服务
        ai_config = self.config.get('ai', {})
        self.ai_service = AIService(
            provider=ai_config.get('provider', 'deepseek'),
            api_key=ai_config.get('api_key', ''),
            base_url=ai_config.get('base_url', ''),
            model=ai_config.get('model', 'deepseek-chat'),
            timeout=ai_config.get('timeout', 180),  # 从配置读取超时时间，默认180秒
            max_retries=ai_config.get('max_retries', 3),
            temperature=ai_config.get('temperature', 0.7),
            max_tokens=ai_config.get('max_tokens', 2000)
        )
        
        self.report_generator = ReportGenerator(
            db=self.db,
            ai_service=self.ai_service
        )
        
        # 初始化邮件发送器
        email_config = self.config.get('email', {})
        self.email_sender = EmailSender(
            smtp_server=email_config.get('smtp_server', 'smtp.163.com'),
            smtp_port=email_config.get('smtp_port', 465),
            username=email_config.get('username', ''),
            password=email_config.get('password', ''),
            use_ssl=email_config.get('use_ssl', True)
        )
        self.test_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
    def cleanup(self):
        """清理资源"""
        self.db.close()
    
    def check_existing_report(self):
        """检查是否存在现有报告"""
        print("\n" + "="*60)
        print("📋 步骤 1: 检查现有报告")
        print("="*60)
        
        # 检查数据库中的报告
        from datetime import datetime
        report_date = datetime.strptime(self.test_date, '%Y-%m-%d').date()
        
        existing_report = self.db.query(DailyReport).filter(
            DailyReport.report_date == report_date
        ).first()
        
        if existing_report:
            print(f"✅ 找到现有报告:")
            print(f"   - 日期: {existing_report.report_date}")
            print(f"   - 创建时间: {existing_report.created_at}")
            print(f"   - PDF 路径: {existing_report.pdf_path}")
            print(f"   - HTML 内容长度: {len(existing_report.html_content) if existing_report.html_content else 0} 字符")
            
            # 检查文件是否存在
            if existing_report.pdf_path:
                pdf_exists = os.path.exists(existing_report.pdf_path)
                print(f"   - PDF 文件存在: {'✅ 是' if pdf_exists else '❌ 否'}")
                if pdf_exists:
                    file_size = os.path.getsize(existing_report.pdf_path)
                    print(f"   - PDF 文件大小: {file_size} 字节")
            
            return existing_report
        else:
            print(f"⚠️  未找到 {self.test_date} 的现有报告")
            return None
    
    def check_articles_and_summaries(self):
        """检查文章和摘要数据"""
        print("\n" + "="*60)
        print("📰 步骤 2: 检查文章和摘要数据")
        print("="*60)
        
        # 查询文章
        from datetime import datetime
        start_date = datetime.strptime(self.test_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=1)
        
        articles = self.db.query(Article).filter(
            Article.publish_time >= start_date,
            Article.publish_time < end_date
        ).all()
        
        print(f"📊 找到 {len(articles)} 篇文章")
        
        if len(articles) == 0:
            print("❌ 没有文章数据，无法生成报告")
            return False
        
        # 检查摘要
        articles_with_summary = 0
        articles_without_summary = []
        
        for article in articles:
            summary = self.db.query(Summary).filter(
                Summary.article_id == article.id
            ).first()
            
            if summary:
                articles_with_summary += 1
            else:
                articles_without_summary.append(article.id)
        
        print(f"✅ 有摘要的文章: {articles_with_summary}")
        print(f"⚠️  无摘要的文章: {len(articles_without_summary)}")
        
        if articles_without_summary:
            print(f"   无摘要的文章 ID: {articles_without_summary[:10]}")
            if len(articles_without_summary) > 10:
                print(f"   ... 还有 {len(articles_without_summary) - 10} 篇")
        
        # 按信息源统计
        from collections import defaultdict
        source_stats = defaultdict(int)
        for article in articles:
            source_stats[article.source.name if article.source else 'Unknown'] += 1
        
        print("\n📈 按信息源统计:")
        for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {source}: {count} 篇")
        
        return len(articles) > 0
    
    def generate_report(self, force=False):
        """生成报告"""
        print("\n" + "="*60)
        print("🔨 步骤 3: 生成报告")
        print("="*60)
        
        if force:
            print("⚠️  强制重新生成模式")
        
        try:
            print(f"⏳ 正在生成 {self.test_date} 的报告...")
            
            # 转换日期格式
            from datetime import datetime
            report_date = datetime.strptime(self.test_date, '%Y-%m-%d').date()
            
            # 生成报告
            report = self.report_generator.generate_daily_report(
                report_date=report_date,
                generate_category_summaries=True,
                generate_pdf=True
            )
            
            if report:
                print(f"✅ 报告生成成功!")
                print(f"   - 报告 ID: {report.id}")
                print(f"   - 日期: {report.report_date}")
                print(f"   - HTML 内容长度: {len(report.html_content) if report.html_content else 0} 字符")
                print(f"   - PDF 路径: {report.pdf_path}")
                
                # 检查 HTML 内容
                if report.html_content:
                    print(f"   - HTML 内容预览: {report.html_content[:200]}...")
                
                # 检查 PDF 文件
                if report.pdf_path and os.path.exists(report.pdf_path):
                    file_size = os.path.getsize(report.pdf_path)
                    print(f"   - PDF 文件大小: {file_size} 字节")
                
                return report
            else:
                print("❌ 报告生成失败")
                return None
                
        except Exception as e:
            print(f"❌ 生成报告时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def check_report_overwrite(self, old_report, new_report):
        """检查报告是否被覆盖"""
        print("\n" + "="*60)
        print("🔍 步骤 4: 检查报告覆盖情况")
        print("="*60)
        
        if not old_report:
            print("ℹ️  没有旧报告，这是新生成的报告")
            return
        
        if not new_report:
            print("❌ 新报告生成失败，无法比较")
            return
        
        print("📊 比较报告:")
        print(f"   旧报告 ID: {old_report.id}")
        print(f"   新报告 ID: {new_report.id}")
        
        if old_report.id == new_report.id:
            print("✅ 报告被更新（ID 相同）")
            print(f"   - 旧创建时间: {old_report.created_at}")
            print(f"   - 新创建时间: {new_report.created_at}")
        else:
            print("⚠️  生成了新的报告（ID 不同）")
        
        # 比较 HTML 内容
        if old_report.html_content and new_report.html_content:
            if len(old_report.html_content) == len(new_report.html_content):
                print("⚠️  HTML 内容长度相同（可能未更新）")
            else:
                print(f"✅ HTML 内容已更新")
                print(f"   旧长度: {len(old_report.html_content)} 字符")
                print(f"   新长度: {len(new_report.html_content)} 字符")
        
        # 比较 PDF 路径
        if old_report.pdf_path == new_report.pdf_path:
            print("✅ PDF 文件路径相同（文件被覆盖）")
        else:
            print("⚠️  PDF 文件路径不同")
            print(f"   旧路径: {old_report.pdf_path}")
            print(f"   新路径: {new_report.pdf_path}")
    
    def check_email_format(self, report):
        """检查邮件格式"""
        print("\n" + "="*60)
        print("📧 步骤 5: 检查邮件格式")
        print("="*60)
        
        if not report:
            print("❌ 没有报告，无法检查邮件格式")
            return False
        
        try:
            # 读取 HTML 报告内容
            if not report.html_content:
                print("❌ HTML 报告内容为空")
                return False
            
            html_content = report.html_content
            print(f"✅ 读取 HTML 报告成功 ({len(html_content)} 字符)")
            
            # 检查 HTML 结构
            checks = {
                '<!DOCTYPE html>': 'HTML 文档类型声明',
                '<html': 'HTML 根标签',
                '<head>': 'Head 标签',
                '<title>': 'Title 标签',
                '<body>': 'Body 标签',
                '金融日报': '报告标题',
                self.test_date: '报告日期',
                '政治层面': '政治层面内容',
                '经济层面': '经济层面内容',
                '技术层面': '技术层面内容',
                '金融科技层面': '金融科技层面内容',
            }
            
            print("\n📋 HTML 结构检查:")
            all_passed = True
            for check, description in checks.items():
                if check in html_content:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description} - 未找到")
                    all_passed = False
            
            # 检查邮件模板
            print("\n📧 邮件模板检查:")
            email_template_path = 'templates/email_template.html'
            if os.path.exists(email_template_path):
                print(f"   ✅ 邮件模板存在: {email_template_path}")
                
                with open(email_template_path, 'r', encoding='utf-8') as f:
                    email_template = f.read()
                
                email_checks = {
                    '<html': 'HTML 标签',
                    '<head>': 'Head 标签',
                    '<meta charset': '字符编码',
                    '<style>': '样式定义',
                    'email-container': '邮件容器',
                }
                
                for check, description in email_checks.items():
                    if check in email_template:
                        print(f"   ✅ {description}")
                    else:
                        print(f"   ⚠️  {description} - 未找到")
            else:
                print(f"   ❌ 邮件模板不存在: {email_template_path}")
            
            return all_passed
            
        except Exception as e:
            print(f"❌ 检查邮件格式时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_test_email(self, report, test_email=None):
        """发送测试邮件"""
        print("\n" + "="*60)
        print("📮 步骤 6: 发送测试邮件")
        print("="*60)
        
        if not report:
            print("❌ 没有报告，无法发送邮件")
            return False
        
        # 获取测试邮箱
        if not test_email:
            test_email = input("请输入测试邮箱地址（直接回车跳过发送）: ").strip()
            if not test_email:
                print("⏭️  跳过邮件发送")
                return False
        
        try:
            print(f"📧 准备发送邮件到: {test_email}")
            print(f"   - 报告日期: {report.report_date}")
            print(f"   - HTML 内容长度: {len(report.html_content) if report.html_content else 0} 字符")
            print(f"   - PDF 路径: {report.pdf_path}")
            
            # 发送邮件（使用报告数据渲染模板）
            report_data = {
                'overall_summary': report.overall_summary,
                'political_summary': report.political_summary,
                'economic_summary': report.economic_summary,
                'technical_summary': report.technical_summary,
                'fintech_summary': report.fintech_summary
            }
            
            success = self.email_sender.send_report(
                recipients=[test_email],
                report_date=report.report_date,
                report_data=report_data,
                attach_pdf=False  # 禁用 PDF 附件
            )
            
            if success:
                print(f"✅ 邮件发送成功!")
                print("\n📬 请检查邮箱:")
                print("   1. 邮件是否收到")
                print("   2. 邮件格式是否正确")
                print("   3. 邮件内容是否完整")
                print("   4. PDF 附件是否可以打开")
                print("   5. 邮件样式是否正常显示")
                print("   6. 中文是否显示正常")
                print("   7. 图表和样式是否正确")
                
                return True
            else:
                print(f"❌ 邮件发送失败")
                return False
                
        except Exception as e:
            print(f"❌ 发送邮件时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_test(self, force_regenerate=False, test_email=None):
        """运行完整测试"""
        print("\n" + "🚀"*30)
        print("开始测试报告生成和邮件发送功能")
        print("🚀"*30)
        print(f"\n测试日期: {self.test_date}")
        print(f"强制重新生成: {'是' if force_regenerate else '否'}")
        
        try:
            # 1. 检查现有报告
            old_report = self.check_existing_report()
            
            # 2. 检查文章和摘要数据
            has_data = self.check_articles_and_summaries()
            if not has_data:
                print("\n❌ 测试终止: 没有足够的数据生成报告")
                return
            
            # 3. 生成报告
            new_report = self.generate_report(force=force_regenerate)
            
            # 4. 检查报告覆盖情况
            self.check_report_overwrite(old_report, new_report)
            
            # 5. 检查邮件格式
            format_ok = self.check_email_format(new_report)
            
            # 6. 发送测试邮件
            if format_ok:
                self.send_test_email(new_report, test_email)
            else:
                print("\n⚠️  邮件格式检查未通过，建议修复后再发送")
            
            # 总结
            print("\n" + "="*60)
            print("📊 测试总结")
            print("="*60)
            print(f"✅ 报告生成: {'成功' if new_report else '失败'}")
            print(f"✅ 报告覆盖检查: 完成")
            print(f"✅ 邮件格式检查: {'通过' if format_ok else '未通过'}")
            print(f"✅ 邮件发送测试: {'已执行' if test_email else '已跳过'}")
            
        except Exception as e:
            print(f"\n❌ 测试过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试报告生成和邮件发送')
    parser.add_argument('--force', action='store_true', help='强制重新生成报告')
    parser.add_argument('--email', type=str, help='测试邮箱地址')
    parser.add_argument('--date', type=str, help='测试日期 (YYYY-MM-DD)，默认为昨天')
    
    args = parser.parse_args()
    
    # 创建测试实例
    tester = TestReportAndEmail()
    
    # 如果指定了日期，使用指定日期
    if args.date:
        tester.test_date = args.date
    
    # 运行测试
    tester.run_test(
        force_regenerate=args.force,
        test_email=args.email
    )


if __name__ == '__main__':
    main()
