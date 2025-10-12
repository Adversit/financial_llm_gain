"""FastAPI应用主入口"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_config
from app.database import init_db
from app.scheduler.tasks import TaskScheduler
from app.api import reports, sources, emails, custom_reports
from app.utils.logger import app_logger

# 全局调度器实例
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global scheduler
    
    # 启动时执行
    app_logger.info("应用启动中...")
    
    # 初始化数据库
    try:
        init_db()
        app_logger.info("数据库初始化完成")
    except Exception as e:
        app_logger.error(f"数据库初始化失败: {e}")
    
    # 启动任务调度器
    try:
        config = get_config()
        scheduler = TaskScheduler(
            rsshub_base_url=config['rsshub']['base_url'],
            ai_config=config['ai'],
            email_config=config['email'],
            schedule_time=config['scheduler']['daily_report_time'],
            timezone=config['scheduler']['timezone']
        )
        scheduler.start()
        app_logger.info("任务调度器启动完成")
    except Exception as e:
        app_logger.error(f"任务调度器启动失败: {e}")
    
    app_logger.info("应用启动完成")
    
    yield
    
    # 关闭时执行
    app_logger.info("应用关闭中...")
    
    if scheduler:
        scheduler.stop()
        app_logger.info("任务调度器已停止")
    
    app_logger.info("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="金融日报系统",
    description="自动化的金融信息聚合和分析平台",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(reports.router)
app.include_router(sources.router)
app.include_router(emails.router)
app.include_router(custom_reports.router)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "欢迎使用金融日报系统",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.get("/scheduler/status")
def scheduler_status():
    """调度器状态"""
    if scheduler:
        jobs = scheduler.list_jobs()
        return {
            "running": True,
            "jobs_count": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time)
                }
                for job in jobs
            ]
        }
    return {"running": False}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
