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
        html_content: str,
        pdf_path: Optional[str] = None,
        attach_pdf: bool = False,
        max_retries: int = 3
    ) -> bool:
        """
        发送报告邮件
        
        Args:
            recipients: 收件人列表
            report_date: 报告日期
            html_content: HTML格式的报告内容
            pdf_path: PDF附件路径（可选）
            attach_pdf: 是否附加 PDF（默认 False，暂不发送）
            max_retries: 最大重试次数
        
        Returns:
            是否发送成功
        """
        if not recipients:
            self.logger.warning("收件人列表为空，跳过发送")
            return False
        
        self.logger.info(f"准备发送邮件给 {len(recipients)} 个收件人")
        
        # 构建邮件
        subject = f"金融日报 - {report_date.strftime('%Y年%m月%d日')}"
        
        for attempt in range(max_retries):
            try:
                msg = self._build_message(
                    recipients=recipients,
                    subject=subject,
                    html_content=html_content,
                    pdf_path=pdf_path if attach_pdf else None  # 根据参数决定是否附加 PDF
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
    
    def _optimize_html_for_email(self, html_content: str) -> str:
        """
        优化 HTML 以适配邮件客户端
        
        Args:
            html_content: 原始 HTML
        
        Returns:
            优化后的 HTML
        """
        # 为段落添加间距
        html_content = html_content.replace('<p>', '<p style="margin-bottom: 15px; line-height: 1.8;">')
        
        # 为标题添加间距和样式
        html_content = html_content.replace(
            '<h3>',
            '<h3 style="margin-top: 25px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #ecf0f1; color: #2c3e50;">'
        )
        html_content = html_content.replace(
            '<h4>',
            '<h4 style="margin-top: 20px; margin-bottom: 12px; color: #34495e;">'
        )
        
        # 为列表添加间距
        html_content = html_content.replace('<ul>', '<ul style="margin-top: 10px; margin-bottom: 20px; margin-left: 25px;">')
        html_content = html_content.replace('<ol>', '<ol style="margin-top: 10px; margin-bottom: 20px; margin-left: 25px;">')
        html_content = html_content.replace('<li>', '<li style="margin-bottom: 12px; line-height: 1.8;">')
        
        # 为分隔线添加间距
        html_content = html_content.replace('<hr>', '<hr style="margin: 30px 0; border: none; border-top: 2px solid #ecf0f1;">')
        
        # 为 strong 标签添加样式
        html_content = html_content.replace('<strong>', '<strong style="color: #2c3e50; font-weight: bold;">')
        
        return html_content
    
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
