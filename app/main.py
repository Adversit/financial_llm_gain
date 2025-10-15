"""FastAPI应用主入口"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
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

# 导入并注册文章API和设置API
from app.api import articles, settings
app.include_router(articles.router)
app.include_router(settings.router)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/sources.html", response_class=HTMLResponse)
async def sources_page(request: Request):
    """信息源管理页面"""
    return templates.TemplateResponse("sources.html", {"request": request})


@app.get("/emails.html", response_class=HTMLResponse)
async def emails_page(request: Request):
    """邮件管理页面"""
    return templates.TemplateResponse("emails.html", {"request": request})


@app.get("/reports.html", response_class=HTMLResponse)
async def reports_page(request: Request):
    """报告查看页面"""
    return templates.TemplateResponse("report.html", {"request": request})


@app.get("/report-detail.html", response_class=HTMLResponse)
async def report_detail_page(request: Request):
    """报告详情页面"""
    return templates.TemplateResponse("report-detail.html", {"request": request})


@app.get("/articles.html", response_class=HTMLResponse)
async def articles_page(request: Request):
    """文章列表页面"""
    return templates.TemplateResponse("articles.html", {"request": request})


@app.get("/custom-report.html", response_class=HTMLResponse)
async def custom_report_page(request: Request):
    """个性化报告页面"""
    return templates.TemplateResponse("custom-report.html", {"request": request})


@app.get("/settings.html", response_class=HTMLResponse)
async def settings_page(request: Request):
    """系统设置页面"""
    return templates.TemplateResponse("settings.html", {"request": request})


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
