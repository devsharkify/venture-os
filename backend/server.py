from fastapi import FastAPI
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
