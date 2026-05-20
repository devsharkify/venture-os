"""SEO & Social Media Agent + Tech Performance Monitor Agent."""
from fastapi import APIRouter, Request
from database import db, logger, EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime, timezone, timedelta
from pathlib import Path
import uuid
import asyncio
import time
import os

BACKEND_DIR = Path(__file__).resolve().parent.parent
RUN_SEO_AGENT_SCRIPT = str(BACKEND_DIR / "run_seo_agent.py")
RUN_PERF_CHECK_SCRIPT = str(BACKEND_DIR / "run_perf_check.py")
BACKEND_CWD = str(BACKEND_DIR)

router = APIRouter(prefix="/api/seo")

BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "")


# ============================================================
# SEO & SOCIAL MEDIA AGENT
# ============================================================

async def _llm(system, user):
    """Quick LLM call."""
    if not EMERGENT_LLM_KEY:
        return ""
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"seo-{uuid.uuid4()}", system_message=system).with_model("gemini", "gemini-2.5-flash")
        r = await asyncio.wait_for(chat.send_message(UserMessage(text=user)), timeout=25)
        return r.strip() if r else ""
    except Exception as e:
        logger.warning(f"SEO LLM call failed: {e}")
        return ""


async def generate_seo_for_article(article):
    """Generate SEO metadata for a single article."""
    title = article.get("title", "")
    summary = article.get("summary", "")[:500]
    category = article.get("category", "")

    result = await _llm(
        """You are an SEO expert for an Indian news website called "Mint Street". Generate SEO metadata as JSON:
{"meta_title": "60 chars max, include 'Mint Street'", "meta_description": "155 chars max", "keywords": ["5-8 relevant keywords"], "og_title": "65 chars", "og_description": "200 chars", "focus_keyword": "main keyword"}
Return ONLY valid JSON.""",
        f"Title: {title}\nCategory: {category}\nSummary: {summary}"
    )

    import json
    try:
        seo = json.loads(result.replace("```json", "").replace("```", "").strip())
    except Exception:
        seo = {
            "meta_title": f"{title[:50]} | Mint Street",
            "meta_description": summary[:155],
            "keywords": [category, "kaizer news", "india news"],
            "og_title": title[:65],
            "og_description": summary[:200],
            "focus_keyword": category
        }
    return seo


async def generate_trending_tags():
    """Analyze recent articles and generate trending tags/topics."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    articles = await db.news.find(
        {"is_active": True, "created_at": {"$gte": cutoff}},
        {"_id": 0, "title": 1, "category": 1}
    ).to_list(50)

    titles = "\n".join([a.get("title", "") for a in articles[:30]])

    result = await _llm(
        """Analyze these news headlines and return JSON with:
{"trending_topics": ["top 10 trending topics/keywords"], "hashtags": ["#10 trending hashtags for social media"], "hot_categories": ["top 5 news categories by volume"]}
Focus on what would trend on Indian social media. Return ONLY valid JSON.""",
        f"Recent headlines:\n{titles}"
    )

    import json
    try:
        return json.loads(result.replace("```json", "").replace("```", "").strip())
    except Exception:
        return {"trending_topics": [], "hashtags": [], "hot_categories": []}


async def bulk_generate_seo():
    """Generate SEO metadata for articles that don't have it yet."""
    articles = await db.news.find(
        {"is_active": True, "seo_meta": {"$exists": False}},
        {"_id": 0, "id": 1, "title": 1, "summary": 1, "category": 1}
    ).sort("created_at", -1).limit(20).to_list(20)

    processed = 0
    for a in articles:
        if not a.get("title"):
            continue
        seo = await generate_seo_for_article(a)
        await db.news.update_one({"id": a["id"]}, {"$set": {"seo_meta": seo}})
        processed += 1
    return processed


@router.get("/sitemap.xml")
async def get_sitemap():
    """Generate XML sitemap for search engines."""
    from fastapi.responses import Response

    articles = await db.news.find(
        {"is_active": True, "link": {"$exists": True, "$ne": ""}},
        {"_id": 0, "id": 1, "link": 1, "created_at": 1, "category": 1}
    ).sort("created_at", -1).limit(5000).to_list(5000)

    base_url = BACKEND_URL or "https://mintstreet.in"
    urls = [f'''  <url>
    <loc>{base_url}/article/{a["id"]}</loc>
    <lastmod>{a.get("created_at","")[:10]}</lastmod>
    <changefreq>daily</changefreq>
    <priority>{"0.9" if i < 10 else "0.7" if i < 50 else "0.5"}</priority>
  </url>''' for i, a in enumerate(articles)]

    # Add static pages
    static = [
        f'  <url><loc>{base_url}</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{base_url}/epaper</loc><changefreq>daily</changefreq><priority>0.9</priority></url>',
        f'  <url><loc>{base_url}/agents</loc><changefreq>daily</changefreq><priority>0.6</priority></url>',
    ]

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(static)}
{chr(10).join(urls)}
</urlset>'''
    return Response(content=xml, media_type="application/xml")


@router.get("/robots.txt")
async def get_robots():
    """Serve robots.txt."""
    from fastapi.responses import PlainTextResponse
    base_url = BACKEND_URL or "https://mintstreet.in"
    return PlainTextResponse(f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/

Sitemap: {base_url}/api/seo/sitemap.xml
""")


@router.post("/generate")
async def run_seo_generation():
    """Run SEO generation for recent articles."""
    import subprocess
    subprocess.Popen(
        ["/root/.venv/bin/python3", RUN_SEO_AGENT_SCRIPT],
        cwd=BACKEND_CWD,
        stdout=open("/tmp/seo_agent.log", "w"),
        stderr=subprocess.STDOUT
    )
    return {"status": "started", "message": "SEO Agent running in background."}


@router.get("/trending")
async def get_trending():
    """Get current trending topics and hashtags."""
    cached = await db.seo_cache.find_one({"key": "trending"}, {"_id": 0})
    if cached and cached.get("updated_at", "") > (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat():
        return cached.get("data", {})
    return {"trending_topics": [], "hashtags": [], "hot_categories": [], "stale": True}


@router.get("/report")
async def get_seo_report():
    """Get latest SEO performance report."""
    report = await db.seo_reports.find_one({}, {"_id": 0}, sort=[("created_at", -1)])
    return {"report": report}


@router.get("/schema/{article_id}")
async def get_article_schema(article_id: str):
    """Get JSON-LD schema for an article (for search engine rich results)."""
    article = await db.news.find_one({"id": article_id}, {"_id": 0})
    if not article:
        return {"error": "Article not found"}

    base_url = BACKEND_URL or "https://mintstreet.in"
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": article.get("title", ""),
        "description": article.get("summary", "")[:200],
        "image": article.get("image", ""),
        "datePublished": article.get("published_at", ""),
        "dateModified": article.get("created_at", ""),
        "author": {"@type": "Organization", "name": "Mint Street"},
        "publisher": {
            "@type": "Organization", "name": "Mint Street",
            "logo": {"@type": "ImageObject", "url": f"{base_url}/logo192.png"}
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{base_url}/article/{article_id}"},
        "keywords": article.get("seo_meta", {}).get("keywords", [])
    }
    return schema


# ============================================================
# TECH PERFORMANCE MONITOR AGENT
# ============================================================

perf_router = APIRouter(prefix="/api/perf")

# Store request timings
REQUEST_TIMINGS = []
MAX_TIMINGS = 500


@perf_router.get("/health-detailed")
async def detailed_health():
    """Detailed health check with response times."""
    start = time.time()

    # Test DB
    db_start = time.time()
    await db.news.count_documents({"is_active": True})
    db_time = (time.time() - db_start) * 1000

    # Test news feed
    feed_start = time.time()
    await db.news.find({"is_active": True}, {"_id": 0, "id": 1}).limit(10).to_list(10)
    feed_time = (time.time() - feed_start) * 1000

    total_time = (time.time() - start) * 1000

    return {
        "status": "ok",
        "response_time_ms": round(total_time, 1),
        "db_query_ms": round(db_time, 1),
        "feed_query_ms": round(feed_time, 1),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@perf_router.get("/metrics")
async def get_performance_metrics():
    """Get performance metrics and history."""
    # Current metrics
    current = await detailed_health()

    # Historical from DB
    recent = await db.perf_metrics.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).limit(100).to_list(100)

    # Averages
    if recent:
        avg_response = sum(m.get("response_time_ms", 0) for m in recent) / len(recent)
        avg_db = sum(m.get("db_query_ms", 0) for m in recent) / len(recent)
        max_response = max(m.get("response_time_ms", 0) for m in recent)
        slow_requests = sum(1 for m in recent if m.get("response_time_ms", 0) > 2000)
    else:
        avg_response = avg_db = max_response = slow_requests = 0

    return {
        "current": current,
        "averages": {
            "avg_response_ms": round(avg_response, 1),
            "avg_db_ms": round(avg_db, 1),
            "max_response_ms": round(max_response, 1),
            "slow_requests_count": slow_requests,
            "total_measurements": len(recent)
        },
        "recent": recent[:20]
    }


@perf_router.post("/check")
async def run_performance_check():
    """Run a full performance check and store results."""
    import subprocess
    subprocess.Popen(
        ["/root/.venv/bin/python3", RUN_PERF_CHECK_SCRIPT],
        cwd=BACKEND_CWD,
        stdout=open("/tmp/perf_check.log", "w"),
        stderr=subprocess.STDOUT
    )
    return {"status": "started"}


@perf_router.get("/report")
async def get_perf_report():
    """Get the latest performance report."""
    report = await db.perf_reports.find_one({}, {"_id": 0}, sort=[("created_at", -1)])
    return {"report": report}
