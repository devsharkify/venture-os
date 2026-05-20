"""Sitemap.xml generation for Mint Street."""
import os
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from fastapi import APIRouter, Response

from database import db

router = APIRouter(tags=["sitemap"])

SITE_BASE = os.environ.get("SITE_BASE_URL", "https://mintstreet.in").rstrip("/")

STATIC_ROUTES = [
    ("/", "daily", "1.0"),
    ("/about", "monthly", "0.5"),
    ("/contact", "monthly", "0.4"),
    ("/advertise", "monthly", "0.4"),
    ("/write-for-us", "monthly", "0.4"),
    ("/privacy-policy", "yearly", "0.2"),
    ("/terms", "yearly", "0.2"),
    ("/cookie-policy", "yearly", "0.2"),
    ("/disclaimer", "yearly", "0.2"),
]


def _iso(value) -> str:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, str):
        return value
    return datetime.now(timezone.utc).isoformat()


@router.get("/sitemap.xml")
async def sitemap_xml():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    now = datetime.now(timezone.utc).isoformat()

    for path, freq, prio in STATIC_ROUTES:
        parts.append("<url>")
        parts.append(f"<loc>{escape(SITE_BASE + path)}</loc>")
        parts.append(f"<lastmod>{now}</lastmod>")
        parts.append(f"<changefreq>{freq}</changefreq>")
        parts.append(f"<priority>{prio}</priority>")
        parts.append("</url>")

    try:
        cursor = (
            db.news.find(
                {"is_active": True},
                {"_id": 0, "id": 1, "published_at": 1, "updated_at": 1},
            )
            .sort("published_at", -1)
            .limit(5000)
        )
        async for art in cursor:
            aid = art.get("id")
            if not aid:
                continue
            lastmod = _iso(art.get("updated_at") or art.get("published_at") or now)
            parts.append("<url>")
            parts.append(f"<loc>{escape(f'{SITE_BASE}/news/{aid}')}</loc>")
            parts.append(f"<lastmod>{escape(lastmod)}</lastmod>")
            parts.append("<changefreq>weekly</changefreq>")
            parts.append("<priority>0.7</priority>")
            parts.append("</url>")
    except Exception as e:
        # If DB is unavailable, emit a comment but keep the static sitemap valid.
        parts.append(f"<!-- article enumeration skipped: {escape(str(e))} -->")

    parts.append("</urlset>")
    return Response(content="".join(parts), media_type="application/xml")
