"""系统设置API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date
import yaml
from pathlib import Path

from app.config import get_config, reload_config
from app.services.email_service import EmailSender
from app.database import get_db
from app.models.daily_report import DailyReport
from app.utils.logger import app_logger

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SendEmailRequest(BaseModel):
    """发送邮件请求"""
    report_date: str
    recipients: List[EmailStr]
    attach_pdf: bool = False


class ScheduleTimeRequest(BaseModel):
    """定时时间设置请求"""
    schedule_time: str  # 格式: "HH:MM"


@router.post("/send-email")
async def send_email_to_recipients(request: SendEmailRequest):
    """
    发送报告到指定邮箱
    
    Args:
        request: 包含报告日期和收件人列表的请求
    
    Returns:
        发送结果
    """
    try:
        app_logger.info(f"手动发送报告: {request.report_date} -> {request.recipients}")
        
        # 加载配置
        config = get_config()
        email_config = config['email']
        
        # 创建邮件发送器
        email_sender = EmailSender(
            smtp_server=email_config['smtp_server'],
            smtp_port=email_config['smtp_port'],
            username=email_config['username'],
            password=email_config['password'],
            use_ssl=email_config.get('use_ssl', True),
            from_name=email_config.get('from_name', '金融日报系统')
        )
        
        # 获取报告
        db = next(get_db())
        try:
            report = db.query(DailyReport).filter(
                DailyReport.report_date == request.report_date
            ).first()
            
            if not report:
                raise HTTPException(status_code=404, detail="报告不存在")
            
            if not report.html_content:
                raise HTTPException(status_code=404, detail="报告内容不存在")
            
            # 直接使用 html_content（和静态 HTML 文件内容相同）
            report_date_obj = date.fromisoformat(request.report_date)
            
            # 发送邮件
            success = email_sender.send_report(
                recipients=request.recipients,
                report_date=report_date_obj,
                html_content=report.html_content,
                pdf_path=report.pdf_path if request.attach_pdf else None,
                attach_pdf=request.attach_pdf
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"报告已成功发送到 {len(request.recipients)} 个邮箱"
                }
            else:
                raise HTTPException(status_code=500, detail="邮件发送失败")
                
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"发送邮件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule-time")
async def get_schedule_time():
    """
    获取当前定时时间
    
    Returns:
        定时时间配置
    """
    try:
        config = get_config()
        return {
            "schedule_time": config['scheduler']['daily_report_time'],
            "timezone": config['scheduler']['timezone']
        }
    except Exception as e:
        app_logger.error(f"获取定时时间失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule-time")
async def update_schedule_time(request: ScheduleTimeRequest):
    """
    更新定时时间
    
    Args:
        request: 包含新定时时间的请求
    
    Returns:
        更新结果
    """
    try:
        # 验证时间格式
        import re
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', request.schedule_time):
            raise HTTPException(status_code=400, detail="时间格式错误，应为 HH:MM")
        
        app_logger.info(f"更新定时时间: {request.schedule_time}")
        
        # 读取配置文件
        config_path = Path("config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 更新定时时间
        config['scheduler']['daily_report_time'] = request.schedule_time
        
        # 写回配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        # 重新加载配置
        reload_config()
        
        app_logger.info(f"定时时间已更新为: {request.schedule_time}")
        
        return {
            "success": True,
            "message": f"定时时间已更新为 {request.schedule_time}",
            "note": "需要重启服务才能生效"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"更新定时时间失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
