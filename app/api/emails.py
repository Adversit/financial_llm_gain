"""邮件相关的API路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.email_subscription import EmailSubscription
from app.schemas.email import (
    EmailSubscriptionCreate,
    EmailSubscriptionUpdate,
    EmailSubscriptionResponse,
    EmailTestRequest,
    EmailTestResponse
)
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("/", response_model=List[EmailSubscriptionResponse])
def list_emails(db: Session = Depends(get_db)):
    """获取邮件订阅列表"""
    subscriptions = db.query(EmailSubscription).all()
    return subscriptions


@router.post("/", response_model=EmailSubscriptionResponse)
def add_email(email: EmailSubscriptionCreate, db: Session = Depends(get_db)):
    """添加订阅邮箱"""
    # 检查邮箱是否已存在
    existing = db.query(EmailSubscription).filter(
        EmailSubscription.email == email.email
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    # 创建订阅
    subscription = EmailSubscription(email=email.email, enabled=True)
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.put("/{email_id}", response_model=EmailSubscriptionResponse)
def update_email(
    email_id: int,
    email_update: EmailSubscriptionUpdate,
    db: Session = Depends(get_db)
):
    """更新邮件订阅"""
    subscription = db.query(EmailSubscription).filter(
        EmailSubscription.id == email_id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="订阅不存在")
    
    subscription.enabled = email_update.enabled
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.delete("/{email_id}", response_model=SuccessResponse)
def delete_email(email_id: int, db: Session = Depends(get_db)):
    """删除订阅邮箱"""
    subscription = db.query(EmailSubscription).filter(
        EmailSubscription.id == email_id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="订阅不存在")
    
    db.delete(subscription)
    db.commit()
    
    return SuccessResponse(success=True, message="订阅已删除")


@router.post("/test", response_model=EmailTestResponse)
def test_email(request: EmailTestRequest):
    """发送测试邮件"""
    try:
        from app.services.email_service import EmailSender
        from app.config import get_config
        
        config = get_config()
        email_config = config['email']
        
        sender = EmailSender(
            smtp_server=email_config['smtp_server'],
            smtp_port=email_config['smtp_port'],
            username=email_config['username'],
            password=email_config['password'],
            use_ssl=email_config.get('use_ssl', True),
            from_name=email_config.get('from_name', '金融日报系统')
        )
        
        success = sender.send_test_email(request.email)
        
        if success:
            return EmailTestResponse(
                success=True,
                message="测试邮件发送成功"
            )
        else:
            return EmailTestResponse(
                success=False,
                message="测试邮件发送失败"
            )
            
    except Exception as e:
        return EmailTestResponse(
            success=False,
            message=f"发送失败: {str(e)}"
        )
