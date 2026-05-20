"""Autonomous SEO Engine — sitemap, robots.txt, RSS, IndexNow, server-rendered article pages, related articles."""
from fastapi import APIRouter, Request, Query
from fastapi.responses import Response, HTMLResponse
from typing import Optional
from datetime import datetime, timezone, timedelta
from database import db, logger, CATEGORIES, EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage
import httpx
import uuid
import asyncio
import os
import re

router = APIRouter(prefix="/api/seo-engine")

SITE_URL = os.environ.get("APP_URL", "")
SITE_NAME = "Mint Street"
INDEXNOW_KEY = "kaizernews-indexnow-key-2026"
LANGUAGES = ["en"]


# ============================================================
# SITEMAP.XML — Auto-generated from all active articles
# ============================================================

@router.get("/sitemap.xml")
async def sitemap_xml():
    """Generate dynamic sitemap.xml with Google News tags and hreflang support."""
    articles = await db.news.find(
        {"is_active": True},
        {"_id": 0, "id": 1, "updated_at": 1, "published_at": 1, "category": 1,
         "title": 1, "seo_title": 1}
    ).sort("published_at", -1).limit(5000).to_list(5000)

    # Cutoff for Google News sitemap (last 2 days only)
    news_cutoff = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

    urls = []
    # Main pages with hreflang
    for page, priority, freq in [
        ("", "1.0", "hourly"),
        ("/epaper", "0.9", "daily"),
        ("/videos", "0.7", "daily"),
    ]:
        urls.append(f"""  <url>
    <loc>{SITE_URL}{page}</loc>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
    <xhtml:link rel="alternate" hreflang="en" href="{SITE_URL}{page}" />
    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE_URL}{page}" />
  </url>""")

    # Category pages
    for cat in CATEGORIES:
        urls.append(f"""  <url>
    <loc>{SITE_URL}/?category={cat}</loc>
    <changefreq>hourly</changefreq>
    <priority>0.8</priority>
  </url>""")

    # Article pages with Google News tags + hreflang
    for a in articles:
        lastmod = a.get("updated_at") or a.get("published_at") or ""
        lastmod_tag = f"\n    <lastmod>{lastmod[:10]}</lastmod>" if lastmod else ""
        title = (a.get("seo_title") or a.get("title", ""))[:65]
        safe_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        pub_date = a.get("published_at", "")[:10]
        cat_label = CATEGORIES.get(a.get("category", ""), {}).get("en", "News")
        article_url = f"{SITE_URL}/news/{a['id']}"

        # Google News tags for articles published in last 2 days
        news_tag = ""
        if a.get("published_at", "") >= news_cutoff:
            news_tag = f"""
    <news:news>
      <news:publication>
        <news:name>{SITE_NAME}</news:name>
        <news:language>en</news:language>
      </news:publication>
      <news:publication_date>{pub_date}</news:publication_date>
      <news:title>{safe_title}</news:title>
      <news:keywords>{cat_label}</news:keywords>
    </news:news>"""

        # Hreflang
        hreflang_tags = f"""
    <xhtml:link rel="alternate" hreflang="en" href="{article_url}" />
    <xhtml:link rel="alternate" hreflang="x-default" href="{article_url}" />"""

        urls.append(f"""  <url>
    <loc>{article_url}</loc>{lastmod_tag}
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>{news_tag}{hreflang_tags}
  </url>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
{chr(10).join(urls)}
</urlset>"""
    return Response(content=xml, media_type="application/xml")


# ============================================================
# ROBOTS.TXT
# ============================================================

@router.get("/robots.txt")
async def robots_txt():
    content = f"""User-agent: *
Allow: /
Allow: /news/
Allow: /epaper
Allow: /videos
Disallow: /admin
Disallow: /api/
Disallow: /reporter-login
Disallow: /reporter/
Disallow: /agents

User-agent: Googlebot
Allow: /
Allow: /news/
Crawl-delay: 1

User-agent: Googlebot-News
Allow: /
Allow: /news/

Sitemap: {SITE_URL}/sitemap.xml
Sitemap: {SITE_URL}/rss.xml

# Mint Street - Indian News Platform
# Contact: admin@kaizernews.com"""
    return Response(content=content, media_type="text/plain")


# ============================================================
# RSS FEED — Google News compatible
# ============================================================

@router.get("/rss.xml")
async def rss_feed():
    """Generate Google News compatible RSS/Atom feed with enhanced metadata."""
    articles = await db.news.find(
        {"is_active": True, "title": {"$ne": ""}},
        {"_id": 0, "id": 1, "title": 1, "summary": 1, "image": 1, "category": 1,
         "published_at": 1, "source": 1, "link": 1, "seo_title": 1, "seo_description": 1, "seo_keywords": 1}
    ).sort("published_at", -1).limit(50).to_list(50)

    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for a in articles:
        title = a.get("seo_title") or a.get("title", "")
        desc = a.get("seo_description") or a.get("summary", "")[:300]
        pub_date = a.get("published_at", "")
        link = f"{SITE_URL}/news/{a['id']}"
        category = a.get("category", "")
        keywords = a.get("seo_keywords", [])
        image_tag = ""
        if a.get("image"):
            image_tag = f'\n      <enclosure url="{a["image"]}" type="image/jpeg" />'
        kw_tags = "".join([f"\n      <category>{kw}</category>" for kw in keywords[:5]]) if keywords else f"\n      <category>{category}</category>"

        items.append(f"""    <item>
      <title><![CDATA[{title}]]></title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <description><![CDATA[{desc}]]></description>{kw_tags}
      <pubDate>{pub_date}</pubDate>
      <source url="{SITE_URL}">{SITE_NAME}</source>{image_tag}
    </item>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>{SITE_NAME}</title>
    <link>{SITE_URL}</link>
    <description>Latest news from Mint Street - Hyderabad, Telangana, India &amp; World</description>
    <language>en-in</language>
    <copyright>Copyright {datetime.now(timezone.utc).year} {SITE_NAME}</copyright>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />
    <image>
      <url>{SITE_URL}/logo192.png</url>
      <title>{SITE_NAME}</title>
      <link>{SITE_URL}</link>
    </image>
{chr(10).join(items)}
  </channel>
</rss>"""
    return Response(content=xml, media_type="application/xml")


# ============================================================
# SERVER-RENDERED ARTICLE PAGE — Full meta tags for crawlers
# ============================================================

@router.get("/article/{article_id}")
async def article_page(article_id: str, request: Request):
    """Server-rendered article page with full SEO meta tags, JSON-LD, OG tags, BreadcrumbList, hreflang."""
    article = await db.news.find_one({"id": article_id}, {"_id": 0})
    if not article:
        return HTMLResponse("<html><body><h1>Article not found</h1></body></html>", status_code=404)

    title = article.get("seo_title") or article.get("title", "")
    description = (article.get("seo_description") or article.get("summary", ""))[:300]
    image = article.get("image", "")
    keywords = ", ".join(article.get("seo_keywords", [])) if article.get("seo_keywords") else article.get("category", "")
    published = article.get("published_at", "")
    category = article.get("category_label", article.get("category", ""))
    category_key = article.get("category", "")
    article_url = f"https://www.mintstreet.in/news/{article_id}"
    source = article.get("source", "")
    full_summary = article.get("summary", "")
    updated_at = article.get("updated_at", published)

    # Escape for HTML attributes
    safe_title = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    safe_desc = description.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

    # JSON-LD NewsArticle + BreadcrumbList
    import json
    json_ld_article = json.dumps({
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": title[:110],
        "description": description,
        "image": [image] if image else [],
        "datePublished": published,
        "dateModified": updated_at,
        "author": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
        "publisher": {
            "@type": "Organization", "name": SITE_NAME, "url": SITE_URL,
            "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/logo192.png", "width": 192, "height": 192}
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": article_url},
        "articleSection": category,
        "keywords": keywords,
        "inLanguage": ["en"],
        "isAccessibleForFree": True,
    }, ensure_ascii=False)

    json_ld_breadcrumb = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": category, "item": f"{SITE_URL}/?category={category_key}"},
            {"@type": "ListItem", "position": 3, "name": title[:60]}
        ]
    }, ensure_ascii=False)

    json_ld_website = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": SITE_URL,
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/?q={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }, ensure_ascii=False)

    img_tag = f'<img class="hero" src="{image}" alt="{safe_title[:50]}" />' if image else ""
    source_tag = f'<div class="source">Original source: <a href="{article.get("link", "")}">{source}</a></div>' if article.get("link") else ""
    pub_date = published[:10] if published else ""

    # Hreflang tags
    hreflang_tags = f'''
  <link rel="alternate" hreflang="en" href="{article_url}" />
  <link rel="alternate" hreflang="x-default" href="{article_url}" />'''

    # Get related articles for internal linking
    related = await db.news.find(
        {"is_active": True, "category": category_key, "id": {"$ne": article_id}},
        {"_id": 0, "id": 1, "title": 1, "image": 1, "category_label": 1, "published_at": 1}
    ).sort("published_at", -1).limit(4).to_list(4)

    related_html = ""
    if related:
        related_items = ""
        for r in related:
            r_title = r.get("title", "")[:80]
            r_img = f'<img src="{r["image"]}" alt="{r_title[:30]}" class="rel-img" />' if r.get("image") else ""
            related_items += f'''
          <a href="{SITE_URL}/news/{r["id"]}" class="rel-card">
            {r_img}
            <span class="rel-title">{r_title}</span>
          </a>'''
        related_html = f'''
  <div class="related">
    <h3>Related Stories</h3>
    <div class="rel-grid">{related_items}
    </div>
  </div>'''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe_title} - {SITE_NAME}</title>
  <meta name="description" content="{safe_desc}" />
  <meta name="keywords" content="{keywords}" />
  <meta name="author" content="{SITE_NAME}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <link rel="canonical" href="{article_url}" />
  {hreflang_tags}

  <!-- Open Graph -->
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{safe_title}" />
  <meta property="og:description" content="{safe_desc}" />
  <meta property="og:image" content="{image}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:url" content="{article_url}" />
  <meta property="og:site_name" content="{SITE_NAME}" />
  <meta property="og:locale" content="en_IN" />
  <meta property="article:published_time" content="{published}" />
  <meta property="article:modified_time" content="{updated_at}" />
  <meta property="article:section" content="{category}" />
  <meta property="article:tag" content="{keywords}" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{safe_title}" />
  <meta name="twitter:description" content="{safe_desc}" />
  <meta name="twitter:image" content="{image}" />
  <meta name="twitter:label1" content="Category" />
  <meta name="twitter:data1" content="{category}" />

  <script type="application/ld+json">{json_ld_article}</script>
  <script type="application/ld+json">{json_ld_breadcrumb}</script>
  <script type="application/ld+json">{json_ld_website}</script>

  <!-- Auto-redirect human browsers to the React SPA. Social bots (no JS) read the OG tags above and stay. -->
  <script>
    (function() {{
      try {{
        var ua = (navigator.userAgent || '').toLowerCase();
        var botPatterns = ['bot','crawl','spider','facebook','whatsapp','twitter','telegram','slack','linkedin','discord','preview','embed','snapchat','pinterest'];
        var isBot = botPatterns.some(function(p) {{ return ua.indexOf(p) !== -1; }});
        if (!isBot) {{
          window.location.replace('{SITE_URL}/news/{article_id}');
        }}
      }} catch (e) {{}}
    }})();
  </script>

  <link rel="alternate" type="application/rss+xml" title="{SITE_NAME} RSS" href="{SITE_URL}/rss.xml" />

  <style>
    body {{ font-family: 'Georgia', serif; max-width: 720px; margin: 0 auto; padding: 20px; color: #1a1a1a; }}
    .header {{ border-bottom: 3px double #c41e1e; padding-bottom: 12px; margin-bottom: 20px; }}
    .header h1 {{ color: #c41e1e; font-size: 28px; margin: 0; }}
    .breadcrumb {{ font-size: 12px; color: #888; margin-bottom: 12px; }}
    .breadcrumb a {{ color: #c41e1e; text-decoration: none; }}
    .breadcrumb a:hover {{ text-decoration: underline; }}
    .meta {{ font-size: 13px; color: #666; margin-bottom: 16px; }}
    img.hero {{ width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin-bottom: 16px; }}
    h2 {{ font-size: 24px; line-height: 1.3; margin-bottom: 12px; }}
    .content {{ font-size: 16px; line-height: 1.8; color: #333; }}
    .source {{ margin-top: 20px; padding: 12px; background: #f5f5f4; border-radius: 8px; font-size: 13px; }}
    .cta {{ margin-top: 24px; text-align: center; }}
    .cta a {{ display: inline-block; padding: 12px 24px; background: #ea580c; color: white; text-decoration: none; border-radius: 24px; font-weight: bold; }}
    .related {{ margin-top: 32px; padding-top: 20px; border-top: 1px solid #e5e5e5; }}
    .related h3 {{ font-size: 18px; margin-bottom: 12px; color: #333; }}
    .rel-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .rel-card {{ text-decoration: none; color: inherit; border: 1px solid #eee; border-radius: 8px; overflow: hidden; }}
    .rel-card:hover {{ box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    .rel-img {{ width: 100%; height: 100px; object-fit: cover; }}
    .rel-title {{ display: block; padding: 8px; font-size: 13px; line-height: 1.4; color: #333; }}
  </style>
</head>
<body>
  <div class="header">
    <h1><a href="{SITE_URL}" style="text-decoration:none;color:#c41e1e">{SITE_NAME}</a></h1>
  </div>

  <div class="breadcrumb">
    <a href="{SITE_URL}">Home</a> &rsaquo;
    <a href="{SITE_URL}/?category={category_key}">{category}</a> &rsaquo;
    <span>{safe_title[:50]}...</span>
  </div>

  {img_tag}
  <h2>{safe_title}</h2>
  <div class="meta">
    <time datetime="{published}">{pub_date}</time> &middot; {category} &middot; {source}
  </div>
  <div class="content">
    <p>{full_summary}</p>
  </div>

  {source_tag}
  {related_html}

  <div class="cta">
    <a href="{SITE_URL}">Read more on {SITE_NAME}</a>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


# ============================================================
# INDEXNOW — Auto-ping Bing/Yandex when new articles are published
# ============================================================

async def ping_indexnow(urls: list):
    """Submit new URLs to search engines via IndexNow protocol."""
    if not urls or not SITE_URL:
        return
    try:
        payload = {
            "host": SITE_URL.replace("https://", "").replace("http://", ""),
            "key": INDEXNOW_KEY,
            "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
            "urlList": urls[:100]
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Submit to Bing
            r = await client.post("https://api.indexnow.org/indexnow", json=payload)
            logger.info(f"IndexNow ping: {len(urls)} URLs, status={r.status_code}")
    except Exception as e:
        logger.warning(f"IndexNow ping failed: {e}")


# IndexNow verification key
@router.get("/indexnow-key.txt")
async def indexnow_key():
    return Response(content=INDEXNOW_KEY, media_type="text/plain")


# ============================================================
# AUTO-SEO META GENERATION — AI-optimized titles & descriptions
# ============================================================

async def generate_seo_meta(article_id: str):
    """Generate SEO-optimized title and meta description for an article using AI."""
    if not EMERGENT_LLM_KEY:
        return

    article = await db.news.find_one({"id": article_id}, {"_id": 0, "title": 1, "summary": 1, "category": 1, "seo_title": 1})
    if not article or article.get("seo_title"):
        return

    title = article.get("title", "")
    summary = article.get("summary", "")[:500]
    category = article.get("category", "")

    if not title:
        return

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"seo-meta-{uuid.uuid4()}",
            system_message="""You are an SEO specialist for "Mint Street", an Indian news platform. 
Generate SEO-optimized metadata for this article. Return JSON with:
- "seo_title": SEO-optimized headline (50-60 chars, include primary keyword, end with "| Mint Street")
- "seo_description": Meta description (140-155 chars, compelling, includes call-to-action)
- "seo_keywords": array of 5-8 relevant search keywords
Return ONLY valid JSON, no markdown."""
        ).with_model("gemini", "gemini-2.5-flash")
        import json
        result = await asyncio.wait_for(
            chat.send_message(UserMessage(text=f"Category: {category}\nTitle: {title}\nSummary: {summary[:300]}")),
            timeout=15
        )
        result = result.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(result)

        update = {}
        if data.get("seo_title"):
            update["seo_title"] = data["seo_title"][:70]
        if data.get("seo_description"):
            update["seo_description"] = data["seo_description"][:160]
        if data.get("seo_keywords"):
            update["seo_keywords"] = data["seo_keywords"][:10]

        if update:
            await db.news.update_one({"id": article_id}, {"$set": update})
            logger.info(f"SEO meta generated for article {article_id}")
    except Exception as e:
        logger.warning(f"SEO meta generation failed for {article_id}: {e}")


async def batch_generate_seo_meta(limit=20):
    """Generate SEO meta for articles that don't have it yet."""
    articles = await db.news.find(
        {"is_active": True, "title": {"$ne": ""}, "$or": [{"seo_title": {"$exists": False}}, {"seo_title": ""}]},
        {"_id": 0, "id": 1}
    ).sort("published_at", -1).limit(limit).to_list(limit)

    count = 0
    for a in articles:
        await generate_seo_meta(a["id"])
        count += 1
        await asyncio.sleep(1)  # Rate limit

    return count


# ============================================================
# SEO PROCESSING AFTER SCRAPE
# ============================================================

async def seo_after_scrape(new_article_ids: list):
    """Run after scraper: generate SEO meta + ping IndexNow + regenerate static files."""
    # Generate SEO meta for new articles
    for aid in new_article_ids[:20]:
        await generate_seo_meta(aid)
        await asyncio.sleep(0.5)

    # Ping IndexNow with new URLs
    if new_article_ids:
        urls = [f"{SITE_URL}/news/{aid}" for aid in new_article_ids]
        await ping_indexnow(urls)

    # Also ping sitemap and RSS
    await ping_indexnow([f"{SITE_URL}/sitemap.xml"])

    # Regenerate static SEO files
    await generate_static_seo_files()


# ============================================================
# API ENDPOINTS
# ============================================================

@router.post("/generate-meta")
async def api_generate_seo_meta():
    """Trigger SEO meta generation as a background subprocess."""
    import subprocess
    subprocess.Popen(
        ["/root/.venv/bin/python3", "-c",
         "import asyncio; import sys; sys.path.insert(0, '/app/backend'); "
         "from routes.seo_engine import batch_generate_seo_meta; "
         "asyncio.run(batch_generate_seo_meta(20))"],
        cwd="/app/backend",
        stdout=open("/tmp/seo_meta.log", "w"),
        stderr=subprocess.STDOUT
    )
    return {"status": "started", "message": "SEO meta generation started in background"}


@router.get("/stats")
async def seo_stats():
    """Get comprehensive SEO coverage statistics and health score."""
    total = await db.news.count_documents({"is_active": True, "title": {"$ne": ""}})
    with_seo = await db.news.count_documents({"is_active": True, "seo_title": {"$exists": True, "$ne": ""}})
    without_seo = total - with_seo
    coverage = round((with_seo / total * 100), 1) if total > 0 else 0

    # Count articles with images (important for SEO)
    with_images = await db.news.count_documents({"is_active": True, "image": {"$exists": True, "$ne": ""}})
    image_coverage = round((with_images / total * 100), 1) if total > 0 else 0

    # Count articles with source links (for canonical/attribution)
    with_links = await db.news.count_documents({"is_active": True, "link": {"$exists": True, "$ne": ""}})
    link_coverage = round((with_links / total * 100), 1) if total > 0 else 0

    # Recent articles (last 24h)
    yesterday = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    recent_count = await db.news.count_documents({"is_active": True, "published_at": {"$gte": yesterday}})
    recent_with_seo = await db.news.count_documents({"is_active": True, "published_at": {"$gte": yesterday}, "seo_title": {"$exists": True, "$ne": ""}})

    # Calculate overall SEO health score (0-100)
    health_score = round(
        (coverage * 0.5) +
        (image_coverage * 0.2) +
        (link_coverage * 0.1) +
        (min(100, recent_count * 5) * 0.2)  # freshness: 20 articles/day = 100%
    )

    return {
        "total_articles": total,
        "with_seo_meta": with_seo,
        "without_seo_meta": without_seo,
        "seo_coverage_percent": coverage,
        "with_images": with_images,
        "image_coverage_percent": image_coverage,
        "with_links": with_links,
        "link_coverage_percent": link_coverage,
        "recent_24h": recent_count,
        "recent_with_seo": recent_with_seo,
        "health_score": health_score,
        "sitemap_url": f"{SITE_URL}/sitemap.xml",
        "rss_url": f"{SITE_URL}/rss.xml",
        "robots_url": f"{SITE_URL}/robots.txt",
    }


# ============================================================
# RELATED ARTICLES — For internal linking
# ============================================================

@router.get("/related/{article_id}")
async def get_related_articles(article_id: str, limit: int = Query(5, ge=1, le=10)):
    """Get related articles for internal linking — same category, recent, with SEO keywords matching."""
    article = await db.news.find_one(
        {"id": article_id},
        {"_id": 0, "category": 1, "seo_keywords": 1, "published_at": 1}
    )
    if not article:
        return {"articles": []}

    category = article.get("category", "")
    keywords = article.get("seo_keywords", [])

    # Find articles in same category, excluding current
    query = {"is_active": True, "id": {"$ne": article_id}}
    if category:
        query["category"] = category

    related = await db.news.find(
        query,
        {"_id": 0, "id": 1, "title": 1, "image": 1, "category": 1,
         "category_label": 1, "published_at": 1, "seo_keywords": 1, "seo_title": 1}
    ).sort("published_at", -1).limit(limit * 3).to_list(limit * 3)

    # Score by keyword overlap if we have keywords
    if keywords:
        keyword_set = set(k.lower() for k in keywords)
        for r in related:
            r_keywords = set(k.lower() for k in (r.get("seo_keywords") or []))
            r["_score"] = len(keyword_set & r_keywords)
        related.sort(key=lambda x: (-x.get("_score", 0), x.get("published_at", "")))
        for r in related:
            r.pop("_score", None)

    # Remove seo_keywords from response
    for r in related[:limit]:
        r.pop("seo_keywords", None)

    return {"articles": related[:limit]}


# ============================================================
# STATIC FILE GENERATOR — writes sitemap.xml, robots.txt, rss.xml to frontend/public
# ============================================================

FRONTEND_PUBLIC = "/app/frontend/public"


async def generate_static_seo_files():
    """Generate sitemap.xml, robots.txt, rss.xml as static files in frontend public folder."""
    try:
        # Generate robots.txt
        robots_content = f"""User-agent: *
Allow: /
Allow: /news/
Allow: /epaper
Allow: /videos
Disallow: /admin
Disallow: /api/
Disallow: /reporter-login
Disallow: /reporter/
Disallow: /agents

User-agent: Googlebot
Allow: /
Allow: /news/
Crawl-delay: 1

User-agent: Googlebot-News
Allow: /
Allow: /news/

Sitemap: {SITE_URL}/sitemap.xml
Sitemap: {SITE_URL}/rss.xml

# Mint Street - Indian News Platform"""
        with open(f"{FRONTEND_PUBLIC}/robots.txt", "w") as f:
            f.write(robots_content)

        # Generate sitemap.xml with Google News + hreflang
        articles = await db.news.find(
            {"is_active": True},
            {"_id": 0, "id": 1, "updated_at": 1, "published_at": 1, "category": 1,
             "title": 1, "seo_title": 1}
        ).sort("published_at", -1).limit(5000).to_list(5000)

        news_cutoff = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        urls = []
        for page, priority, freq in [
            ("", "1.0", "hourly"), ("/epaper", "0.9", "daily"), ("/videos", "0.7", "daily"),
        ]:
            urls.append(f'  <url>\n    <loc>{SITE_URL}{page}</loc>\n    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n    <xhtml:link rel="alternate" hreflang="en" href="{SITE_URL}{page}" />\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE_URL}{page}" />\n  </url>')

        for cat in CATEGORIES:
            urls.append(f'  <url>\n    <loc>{SITE_URL}/?category={cat}</loc>\n    <changefreq>hourly</changefreq>\n    <priority>0.8</priority>\n  </url>')

        for a in articles:
            lastmod = a.get("updated_at") or a.get("published_at") or ""
            lastmod_tag = f"\n    <lastmod>{lastmod[:10]}</lastmod>" if lastmod else ""
            title = (a.get("seo_title") or a.get("title", ""))[:65]
            safe_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
            pub_date = a.get("published_at", "")[:10]
            cat_label = CATEGORIES.get(a.get("category", ""), {}).get("en", "News")
            article_url = f"{SITE_URL}/news/{a['id']}"

            news_tag = ""
            if a.get("published_at", "") >= news_cutoff:
                news_tag = f'\n    <news:news>\n      <news:publication>\n        <news:name>{SITE_NAME}</news:name>\n        <news:language>en</news:language>\n      </news:publication>\n      <news:publication_date>{pub_date}</news:publication_date>\n      <news:title>{safe_title}</news:title>\n      <news:keywords>{cat_label}</news:keywords>\n    </news:news>'

            hreflang_tags = f'\n    <xhtml:link rel="alternate" hreflang="en" href="{article_url}" />'
            hreflang_tags += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{article_url}" />'

            urls.append(f'  <url>\n    <loc>{article_url}</loc>{lastmod_tag}\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>{news_tag}{hreflang_tags}\n  </url>')

        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
{chr(10).join(urls)}
</urlset>"""
        with open(f"{FRONTEND_PUBLIC}/sitemap.xml", "w") as f:
            f.write(sitemap)

        # Generate rss.xml with enhanced metadata
        recent = await db.news.find(
            {"is_active": True, "title": {"$ne": ""}},
            {"_id": 0, "id": 1, "title": 1, "summary": 1, "image": 1, "category": 1,
             "published_at": 1, "source": 1, "seo_title": 1, "seo_description": 1, "seo_keywords": 1}
        ).sort("published_at", -1).limit(50).to_list(50)

        now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        items = []
        for a in recent:
            t = a.get("seo_title") or a.get("title", "")
            d = (a.get("seo_description") or a.get("summary", ""))[:300]
            link = f"{SITE_URL}/news/{a['id']}"
            category_name = a.get('category', '')
            enc = f'\n      <enclosure url="{a["image"]}" type="image/jpeg" />' if a.get("image") else ""
            keywords = a.get("seo_keywords", [])
            kw_tags = "".join([f"\n      <category>{kw}</category>" for kw in keywords[:5]]) if keywords else f"\n      <category>{category_name}</category>"
            items.append(f"""    <item>
      <title><![CDATA[{t}]]></title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <description><![CDATA[{d}]]></description>{kw_tags}
      <pubDate>{a.get('published_at', '')}</pubDate>
      <source url="{SITE_URL}">{SITE_NAME}</source>{enc}
    </item>""")

        rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>{SITE_NAME}</title>
    <link>{SITE_URL}</link>
    <description>Latest news from Mint Street - Hyderabad, Telangana, India and World</description>
    <language>en-in</language>
    <copyright>Copyright {datetime.now(timezone.utc).year} {SITE_NAME}</copyright>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />
    <image>
      <url>{SITE_URL}/logo192.png</url>
      <title>{SITE_NAME}</title>
      <link>{SITE_URL}</link>
    </image>
{chr(10).join(items)}
  </channel>
</rss>"""
        with open(f"{FRONTEND_PUBLIC}/rss.xml", "w") as f:
            f.write(rss)

        # IndexNow key file
        with open(f"{FRONTEND_PUBLIC}/{INDEXNOW_KEY}.txt", "w") as f:
            f.write(INDEXNOW_KEY)

        logger.info(f"Static SEO files generated: {len(articles)} articles in sitemap, {len(recent)} in RSS")
        return True
    except Exception as e:
        logger.error(f"Failed to generate static SEO files: {e}")
        return False


@router.post("/generate-static")
async def api_generate_static():
    """Generate static sitemap.xml, robots.txt, rss.xml files."""
    result = await generate_static_seo_files()
    return {"status": "ok" if result else "error"}