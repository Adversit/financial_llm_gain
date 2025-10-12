"""快速查看数据库状态"""
from app.database import SessionLocal
from app.models.article import Article
from app.models.summary import Summary
from app.models.daily_report import DailyReport
from app.models.source import Source
from app.models.email_subscription import EmailSubscription
from datetime import date, timedelta
from collections import defaultdict

def show_status():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("数据库状态")
        print("=" * 70)
        
        # 基本统计
        print("\n📊 数据统计:")
        tables = [
            ('信息源', Source),
            ('文章', Article),
            ('摘要', Summary),
            ('报告', DailyReport),
            ('邮件订阅', EmailSubscription),
        ]
        
        for name, model in tables:
            count = db.query(model).count()
            print(f"   {name:12} {count:6} 条")
        
        # 文章详情
        articles = db.query(Article).all()
        if articles:
            print("\n📅 文章日期分布:")
            by_date = defaultdict(int)
            no_date = 0
            
            for article in articles:
                if article.publish_time:
                    by_date[article.publish_time.date()] += 1
                else:
                    no_date += 1
            
            for d in sorted(by_date.keys(), reverse=True)[:5]:
                print(f"   {d}: {by_date[d]} 篇")
            
            if no_date > 0:
                print(f"   无日期: {no_date} 篇")
        
        # 报告详情
        reports = db.query(DailyReport).order_by(
            DailyReport.report_date.desc()
        ).all()
        
        if reports:
            print("\n📋 报告列表:")
            for report in reports:
                print(f"   {report.report_date} - 创建于 {report.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # 信息源状态
        sources = db.query(Source).all()
        if sources:
            print("\n📰 信息源状态:")
            enabled = sum(1 for s in sources if s.enabled)
            disabled = len(sources) - enabled
            print(f"   启用: {enabled} 个")
            print(f"   禁用: {disabled} 个")
        
        print("\n" + "=" * 70)
        
    finally:
        db.close()

if __name__ == "__main__":
    show_status()
