from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from pathlib import Path
import os
import asyncio
from database import client, db

# Import all route modules
from routes.auth import router as auth_router
from routes.news import router as news_router
from routes.upload import router as upload_router
from routes.reporter import router as reporter_router
from routes.analytics import router as analytics_router
from routes.media import router as media_router
from routes.epaper import router as epaper_router
from routes.scraper import router as scraper_router, scraper_loop
from routes.agents import router as agents_router, run_agents_after_scrape
from routes.telegram_bot import router as telegram_router
from routes.seo_agent import router as seo_router
from routes.tech_agent import router as tech_router, performance_middleware
from routes.seo_engine import router as seo_engine_router
from routes.public_api import router as public_api_router, admin_router as apikeys_admin_router
from routes.youtube import router as youtube_router
from routes.youtube_agents import router as youtube_agents_router
from routes.startup import router as startup_router
from routes.sitemap import router as sitemap_router

ROOT_DIR = Path(__file__).parent
REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_BUILD = REPO_ROOT / "frontend" / "build"

# Create the main app
app = FastAPI()

# Include all routers
app.include_router(auth_router)
app.include_router(news_router)
app.include_router(upload_router)
app.include_router(reporter_router)
app.include_router(analytics_router)
app.include_router(media_router)
app.include_router(epaper_router)
app.include_router(scraper_router)
app.include_router(agents_router)
app.include_router(telegram_router)
app.include_router(seo_router)
app.include_router(tech_router)
app.include_router(seo_engine_router)
app.include_router(public_api_router)
app.include_router(apikeys_admin_router)
app.include_router(youtube_router)
app.include_router(youtube_agents_router)
app.include_router(startup_router)
app.include_router(sitemap_router)

# GZip compression - compress responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

# Performance tracking middleware
app.middleware("http")(performance_middleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
uploads_dir = ROOT_DIR / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Serve the production frontend bundle (backend-serves-frontend pattern).
# Mounted AFTER all /api/* routers so API routes still match first.
if FRONTEND_BUILD.exists() and (FRONTEND_BUILD / "index.html").exists():
    # /static/* -> compiled JS/CSS from CRA
    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_BUILD / "static")),
        name="frontend-static",
    )

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str, request: Request):
        # Don't intercept API or uploads (defensive — routers already matched first).
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404)
        # Serve any top-level static asset (favicon, logo.svg, robots.txt, sitemap.xml, sw.js, …)
        candidate = FRONTEND_BUILD / full_path
        if full_path and candidate.is_file():
            return FileResponse(str(candidate))
        # SPA fallback: let React Router handle the route on the client.
        return FileResponse(str(FRONTEND_BUILD / "index.html"))
else:
    print(f"[mint-street] frontend build not found at {FRONTEND_BUILD}; skipping SPA mount")

# Startup: launch scraper background task + generate SEO files + create indexes
@app.on_event("startup")
async def start_scraper():
    # Create MongoDB indexes for fast queries
    try:
        await db.news.create_index([("is_active", 1), ("published_at", -1)])
        await db.news.create_index([("is_active", 1), ("category", 1), ("published_at", -1)])
        await db.news.create_index([("is_active", 1), ("is_pinned", -1), ("published_at", -1)])
        await db.news.create_index("id", unique=True)
        await db.news.create_index("title_hash")
        await db.news.create_index([("is_active", 1), ("seo_title", 1)])
        await db.perf_metrics.create_index("timestamp")
        await db.perf_metrics.create_index([("timestamp", -1), ("endpoint", 1)])
    except Exception as e:
        print(f"Index creation: {e}")

    # Seed the news collection from backend/seed_articles.py on first boot
    try:
        existing = await db.news.count_documents({})
        if existing == 0:
            from seed_articles import SEED_ARTICLES
            from datetime import datetime, timezone
            docs = []
            for a in SEED_ARTICLES:
                d = dict(a)
                d.setdefault("is_active", True)
                d.setdefault("content_type", "text")
                d.setdefault("created_at", datetime.now(timezone.utc).isoformat())
                d.setdefault("updated_at", datetime.now(timezone.utc).isoformat())
                docs.append(d)
            await db.news.insert_many(docs)
            print(f"Seeded {len(docs)} articles into db.news")
        else:
            print(f"db.news already has {existing} articles; skipping seed")
    except Exception as e:
        print(f"Seed-on-boot failed: {e}")

    asyncio.create_task(scraper_loop())
    try:
        from routes.seo_engine import generate_static_seo_files
        asyncio.create_task(generate_static_seo_files())
    except Exception as e:
        print(f"SEO static generation on startup failed: {e}")

# Shutdown: close DB
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
