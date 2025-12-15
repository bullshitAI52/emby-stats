"""
Emby Stats - 播放统计分析应用
主入口文件
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from routers import (
    stats_router,
    media_router,
    auth_router,
    servers_router,
    files_router,
    report_router,
    tg_bot_router
)
from routers.auth import get_current_session
from services.session import session_service
from services.servers import server_service
from scheduler import setup_scheduler

# 创建应用实例
app = FastAPI(title="Emby Stats")

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 不需要认证的路径
PUBLIC_PATHS = {
    "/api/auth/login",
    "/api/auth/check",
    "/api/auth/logout",
    "/api/debug/scheduler",  # 调试端点
    "/manifest.json",
    "/sw.js",
}

# 不需要认证的路径前缀
PUBLIC_PREFIXES = [
    "/api/servers",      # 服务器列表（登录页需要）
    "/icons/",
    "/static/",
]


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """认证中间件：保护 API 端点"""
    path = request.url.path

    # 静态资源和认证接口不需要验证
    if path in PUBLIC_PATHS:
        return await call_next(request)

    for prefix in PUBLIC_PREFIXES:
        if path.startswith(prefix):
            return await call_next(request)

    # 前端页面（非 API）不在这里拦截，由前端处理
    if not path.startswith("/api/"):
        return await call_next(request)

    # API 请求需要验证
    session = await get_current_session(request)
    if not session:
        return JSONResponse(
            status_code=401,
            content={"detail": "未登录"}
        )

    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行的初始化操作"""
    import logging
    logger = logging.getLogger("uvicorn")

    # 初始化会话数据库
    await session_service.init_db()
    logger.info("✓ 会话数据库初始化完成")

    # 初始化服务器配置数据库
    await server_service.init_servers_table()
    logger.info("✓ 服务器配置数据库初始化完成")

    # 清理过期会话
    cleaned = await session_service.clean_expired_sessions()
    if cleaned > 0:
        logger.info(f"✓ 清理了 {cleaned} 个过期会话")

    # 启动定时任务调度器
    setup_scheduler()
    logger.info("✓ 定时任务调度器已启动")


# 注册路由
app.include_router(auth_router)
app.include_router(stats_router)
app.include_router(media_router)
app.include_router(servers_router)
app.include_router(files_router)
app.include_router(report_router)
app.include_router(tg_bot_router)


# 调试用：查看调度器状态
@app.get("/api/debug/scheduler")
async def debug_scheduler_status():
    """查看调度器状态（调试用）"""
    from scheduler import scheduler

    jobs_info = []
    for job in scheduler.get_jobs():
        jobs_info.append({
            "id": job.id,
            "next_run_time": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger)
        })

    return {
        "running": scheduler.running,
        "job_count": len(scheduler.get_jobs()),
        "jobs": jobs_info
    }


# 静态文件服务
frontend_path = "/app/frontend"
if os.path.exists(frontend_path):
    # PWA 文件路由
    @app.get("/manifest.json")
    async def serve_manifest():
        return FileResponse(
            os.path.join(frontend_path, "manifest.json"),
            media_type="application/manifest+json"
        )

    @app.get("/sw.js")
    async def serve_sw():
        return FileResponse(
            os.path.join(frontend_path, "sw.js"),
            media_type="application/javascript"
        )

    # Icons 目录
    icons_path = os.path.join(frontend_path, "icons")
    if os.path.exists(icons_path):
        app.mount("/icons", StaticFiles(directory=icons_path), name="icons")

    # Static assets (JS, CSS from Vite build)
    static_path = os.path.join(frontend_path, "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    # Catch-all for SPA routing (in case using React Router in the future)
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        file_path = os.path.join(frontend_path, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))
