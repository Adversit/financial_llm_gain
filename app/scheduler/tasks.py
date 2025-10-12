"""任务调度器 - 定时执行数据采集和报告生成"""
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.crawler_service import CrawlerService
from app.services.ai_service import AIService
from app.services.report_service import ReportGenerator
from app.services.email_service import EmailSender
from app.models.email_subscription import EmailSubscription
from app.utils.logger import scheduler_logger


class TaskScheduler:
    """任务调度器 - 管理定时任务"""
    
    def __init__(
        self,
        rsshub_base_url: str,
        ai_config: dict,
        email_config: dict,
        schedule_time: str = "08:00",
        timezone: str = "Asia/Shanghai"
    ):
        """
        初始化任务调度器
        
        Args:
            rsshub_base_url: RSSHub基础URL
            ai_config: AI配置字典
            email_config: 邮件配置字典
            schedule_time: 每日执行时间（HH:MM格式）
            timezone: 时区
        """
        self.rsshub_base_url = rsshub_base_url
        self.ai_config = ai_config
        self.email_config = email_config
        self.schedule_time = schedule_time
        self.timezone = timezone
        self.logger = scheduler_logger
        
        # 创建调度器
        self.scheduler = BackgroundScheduler(timezone=timezone)
    
    def start(self):
        """启动调度器"""
        self.logger.info("启动任务调度器")
        
        # 解析时间
        hour, minute = map(int, self.schedule_time.split(':'))
        
        # 添加每日任务
        self.scheduler.add_job(
            func=self.run_daily_pipeline,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=self.timezone),
            id='daily_report',
            name='每日金融报告生成',
            replace_existing=True
        )
        
        self.logger.info(f"已添加每日任务: 每天 {self.schedule_time} 执行")
        
        # 启动调度器
        self.scheduler.start()
        self.logger.info("任务调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.logger.info("停止任务调度器")
        self.scheduler.shutdown()
    
    def run_daily_pipeline(self, target_date: date = None):
        """
        执行完整的每日流程
        
        Args:
            target_date: 目标日期，默认为昨天
        """
        if target_date is None:
            target_date = date.today() - timedelta(days=1)
        
        self.logger.info(f"=" * 60)
        self.logger.info(f"开始执行每日流程: {target_date}")
        self.logger.info(f"=" * 60)
        
        db = SessionLocal()
        
        try:
            # 1. 初始化服务
            self.logger.info("步骤 1/5: 初始化服务")
            ai_service = self._create_ai_service()
            crawler_service = CrawlerService(
                db=db,
                rsshub_base_url=self.rsshub_base_url,
                ai_service=ai_service
            )
            report_generator = ReportGenerator(
                db=db,
                ai_service=ai_service
            )
            email_sender = self._create_email_sender()
            
            # 2. 数据采集
            self.logger.info("步骤 2/5: 数据采集")
            grouped_articles = crawler_service.fetch_all_sources(
                target_date=target_date,
                generate_summaries=True
            )
            
            total_articles = sum(len(articles) for articles in grouped_articles.values())
            self.logger.info(f"数据采集完成，共 {total_articles} 篇文章")
            
            if total_articles == 0:
                self.logger.warning("没有采集到文章，跳过后续步骤")
                return
            
            # 3. 报告生成
            self.logger.info("步骤 3/5: 报告生成")
            report = report_generator.generate_daily_report(
                report_date=target_date,
                generate_category_summaries=True
            )
            self.logger.info(f"报告生成完成")
            
            # 4. 邮件发送
            self.logger.info("步骤 4/5: 邮件发送")
            recipients = self._get_active_recipients(db)
            
            if recipients:
                success = email_sender.send_report(
                    recipients=recipients,
                    report_date=target_date,
                    html_content=report.html_content,
                    pdf_path=report.pdf_path,
                    attach_pdf=False  # 暂不附加 PDF，后续可改为 True
                )
                
                if success:
                    self.logger.info(f"邮件发送成功，收件人: {len(recipients)} 个")
                else:
                    self.logger.error("邮件发送失败")
            else:
                self.logger.warning("没有活跃的邮件订阅者，跳过邮件发送")
            
            # 5. 完成
            self.logger.info("步骤 5/5: 流程完成")
            self.logger.info(f"=" * 60)
            self.logger.info(f"每日流程执行完成: {target_date}")
            self.logger.info(f"=" * 60)
            
        except Exception as e:
            self.logger.error(f"每日流程执行失败: {e}", exc_info=True)
            raise
        finally:
            db.close()
    
    def run_manual_pipeline(self, target_date: date = None):
        """
        手动执行流程（用于测试或补充执行）
        
        Args:
            target_date: 目标日期
        """
        self.logger.info("手动执行每日流程")
        self.run_daily_pipeline(target_date)
    
    def _create_ai_service(self) -> AIService:
        """创建AI服务实例"""
        return AIService(
            provider=self.ai_config.get('provider', 'deepseek'),
            api_key=self.ai_config['api_key'],
            base_url=self.ai_config['base_url'],
            model=self.ai_config['model'],
            temperature=self.ai_config.get('temperature', 0.7),
            max_tokens=self.ai_config.get('max_tokens', 2000),
            timeout=self.ai_config.get('timeout', 30),
            max_retries=self.ai_config.get('max_retries', 3)
        )
    
    def _create_email_sender(self) -> EmailSender:
        """创建邮件发送器实例"""
        return EmailSender(
            smtp_server=self.email_config['smtp_server'],
            smtp_port=self.email_config['smtp_port'],
            username=self.email_config['username'],
            password=self.email_config['password'],
            use_ssl=self.email_config.get('use_ssl', True),
            from_name=self.email_config.get('from_name', '金融日报系统')
        )
    
    def _get_active_recipients(self, db: Session) -> list:
        """
        获取活跃的邮件订阅者
        
        Args:
            db: 数据库会话
        
        Returns:
            邮箱地址列表
        """
        subscriptions = db.query(EmailSubscription).filter(
            EmailSubscription.enabled == True
        ).all()
        
        return [sub.email for sub in subscriptions]
    
    def add_custom_job(
        self,
        func,
        trigger,
        job_id: str,
        name: str = None,
        **trigger_args
    ):
        """
        添加自定义任务
        
        Args:
            func: 任务函数
            trigger: 触发器类型（'cron', 'interval', 'date'）
            job_id: 任务ID
            name: 任务名称
            **trigger_args: 触发器参数
        """
        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            name=name or job_id,
            replace_existing=True,
            **trigger_args
        )
        
        self.logger.info(f"已添加自定义任务: {name or job_id}")
    
    def remove_job(self, job_id: str):
        """
        移除任务
        
        Args:
            job_id: 任务ID
        """
        self.scheduler.remove_job(job_id)
        self.logger.info(f"已移除任务: {job_id}")
    
    def list_jobs(self):
        """列出所有任务"""
        jobs = self.scheduler.get_jobs()
        self.logger.info(f"当前任务列表 ({len(jobs)} 个):")
        for job in jobs:
            self.logger.info(f"  - {job.id}: {job.name} (下次执行: {job.next_run_time})")
        return jobs
