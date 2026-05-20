"""
TVR Backend Scraper — Startup/Funding focused RSS + Entrackr sitemap

══════════════════════════════════════════════════════════════════════
SCRAPING RULES (enforced in code — do NOT bypass):
══════════════════════════════════════════════════════════════════════
RULE 1 — REPHRASE ALWAYS:
  Every article's title AND summary MUST be rephrased by Gemini before
  saving. The original source text must never appear verbatim in the DB.
  The save function will NOT proceed without calling gemini_rephrase().

RULE 2 — WATERMARK / LOGO REJECTION:
  Every image is checked via Gemini Vision before saving. If the image
  contains ANY visible watermark, logo, or branding from another website
  or publication (YourStory, Economic Times, Entrackr, Mint, Getty,
  Shutterstock, Dreamstime, Moneycontrol, Reuters, etc.), the article is
  SILENTLY DROPPED and NOT saved to the database.

RULE 3 — STARTUP RELEVANCE:
  Only articles passing the India + startup/funding signal filters are
  accepted.
══════════════════════════════════════════════════════════════════════
"""
from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import asyncio, uuid, os, re, base64
import feedparser
import httpx
from bs4 import BeautifulSoup
from database import db, logger, CATEGORIES

router = APIRouter(prefix="/api")

scraper_status = {"running": False, "last_run": None, "articles_added": 0, "error": None}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"

# ── Startup relevance filters ──────────────────────────────────────────────────

SKIP_TERMS = [
    "cricket", "ipl", "football", "sports", "bollywood", "film ", " movie",
    "actor", "actress", "entertainment", "crime", "murder", "election",
    "bjp", "congress", "parliament", "weather", "army", "military",
    "flood", "earthquake", "accident", "temple", "mosque",
    "pakistan", "russia", "ukraine",
    "petrol price", "diesel price", "crude oil price",
    "coal mine", "nuclear plant", "railway project",
    "highway project", "road project", "fertilizer plant",
    "power plant", "solar park", "wind farm",
    "residential project", "luxury project", "township project",
    "police arrest", "fir filed", "court order",
]

INDIA_SIGNALS = [
    "india", "indian", "bengaluru", "bangalore", "mumbai", "delhi",
    "hyderabad", "pune", "chennai", "kolkata", "inr", "crore", "lakh",
    "sebi", "rbi", "dpiit", "rupee", "₹",
    "flipkart", "zomato", "swiggy", "paytm", "razorpay", "groww",
    "zerodha", "nykaa", "meesho", "cred", "freshworks", "ola", "byju",
]

STARTUP_STRONG = [
    "startup", "series a", "series b", "series c", "series d", "series e",
    "seed round", "pre-seed", "angel round", "angel investment",
    "raises funding", "raised funding", "secures funding", "closes funding",
    "funding round", "venture capital", "vc fund",
    "unicorn", "soonicorn", "ipo filing", "ipo-bound", "co-founder", "founder",
    "fintech", "edtech", "healthtech", "agritech", "insurtech", "saas",
    "d2c brand", "bootstrapped", "incubator", "accelerator",
    "razorpay", "paytm", "phonepe", "groww", "zerodha", "cred",
    "zomato", "swiggy", "flipkart", "meesho", "nykaa", "ola", "byju",
    "moglix", "lenskart", "vedantu", "upgrad", "cars24", "oyo",
    "mamaearth", "nazara", "dream11", "mpl",
    "fund of funds", "startup india", "dpiit",
    "raises $", "raises rs", "raises ₹",
    "secures $", "secures rs", "secures ₹",
    "raised $", "raised rs", "raised ₹",
    "bags $", "bags rs", "bags ₹",
    "crore seed", "crore funding", "crore investment",
    "million funding", "million investment", "million raise",
    "pre-series", "series funding",
    "blackbuck", "oxyzo", "mapmyindia", "trackk", "damroo",
    "delhivery", "makemytrip", "bain capital", "lightspeed",
    "shadowfax", "rapido", "scripbox", "meesho",
]


def is_startup_relevant(title: str, text: str = "", trusted: bool = False) -> bool:
    combined = (title + " " + text[:2000]).lower()
    if any(k in combined for k in SKIP_TERMS):
        return False
    if not trusted and not any(k in combined for k in INDIA_SIGNALS):
        return False
    if any(k in combined for k in STARTUP_STRONG):
        return True
    if trusted:
        return any(k in combined for k in [
            "funding", "startup", "raise", "investor", "venture",
            "crore", "million", "ipo", "acquire", "fintech", "saas",
        ])
    medium = sum(1 for k in ["investment", "investor", "backed", "funded", "capital", "crore", "million", "venture", "equity"] if k in combined)
    return medium >= 2


CATEGORY_RULES = [
    ("ipo",     ["ipo", "initial public offering", "stock listing", "nse listing", "bse listing", "sme ipo", "mainboard ipo", "market debut"]),
    ("funding", ["funding round", "series a", "series b", "series c", "series d", "series e", "seed round", "pre-seed", "angel round", "raises ", "raised ", "capital raise", "equity funding", "backed by", "led by", "investment round", "fundraise", "secures funding", "closes funding", "secures $", "secures rs", "raises $", "raises rs", "secures ₹", "raises ₹", "bags $", "bags rs", "bags ₹"]),
    ("fintech", ["fintech", "payment", "neobank", "crypto", "blockchain", "insurtech", "lending", "nbfc", "upi", "digital wallet", "razorpay", "paytm", "phonepe", "zerodha", "groww", "cred", "policybazaar", "wealthtech", "bnpl"]),
    ("vc",      ["venture capital", "vc fund", "private equity", "pe fund", "limited partner", "vc firm", "sequoia", "accel", "lightspeed", "matrix partners", "blume ventures", "kalaari", "nexus", "elevation capital", "peak xv", "general catalyst", "tiger global", "softbank", "fund of funds"]),
    ("policy",  ["sebi", "rbi circular", "regulation", "regulatory", "dpiit", "startup india", "fdi", "ministry", "government scheme", "budget", "gst", "angel tax"]),
    ("tech",    ["saas", "artificial intelligence", "machine learning", "deep tech", "agritech", "edtech", "healthtech", "proptech", "cloud", "automation", "b2b", "ai startup", "tech startup", "d2c", "generative ai"]),
    ("startup", ["startup", "co-founder", "bootstrapped", "entrepreneur", "d2c", "founded", "incubator", "accelerator", "cohort", "pitch", "early-stage"]),
    ("business", ["merger", "acquisition", "partnership", "valuation", "unicorn", "profit", "quarterly", "revenue", "market share", "expansion", "ipo-bound"]),
]


def detect_category(title: str, text: str) -> str:
    c = (title + " " + text[:2000]).lower()
    for cat, kws in CATEGORY_RULES:
        if any(k in c for k in kws):
            return cat
    return "business"


# ── Gemini rephrase ────────────────────────────────────────────────────────────

TITLE_PROMPT = """You are an editor at Mint Street, a premium Indian startup magazine.
Rephrase this headline to be engaging and punchy. Keep all facts exact (company names, numbers, amounts).
Max 100 characters. No quotes. Write like Forbes/Bloomberg. Return ONLY the headline.

Original: {title}"""

SUMMARY_PROMPT = """You are a journalist at Mint Street, India's top startup magazine.
Rewrite this article summary to be engaging and original. Keep all facts accurate.
Write 3-4 paragraphs (~180 words). Start with the key fact. No filler phrases. Plain text only.

Original: {summary}

Return ONLY the rewritten summary."""


async def gemini_rephrase(client: httpx.AsyncClient, title: str, summary: str) -> tuple[str, str]:
    """Returns (rephrased_title, rephrased_summary). Falls back to originals on failure."""
    new_title, new_summary = title, summary

    def make_body(prompt, max_tokens=150):
        return {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": max_tokens,
                "thinkingConfig": {"thinkingBudget": 0},
            }
        }

    try:
        r = await client.post(GEMINI_URL, json=make_body(TITLE_PROMPT.format(title=title)), timeout=25)
        if r.status_code == 200:
            d = r.json()
            t = d["candidates"][0]["content"]["parts"][0]["text"].strip()
            if t and len(t) < 200:
                new_title = t
    except Exception as e:
        logger.warning(f"Gemini title rephrase failed: {e}")

    if summary and len(summary) > 80:
        try:
            r2 = await client.post(GEMINI_URL, json=make_body(SUMMARY_PROMPT.format(summary=summary[:1500]), max_tokens=600), timeout=30)
            if r2.status_code == 200:
                d2 = r2.json()
                s = d2["candidates"][0]["content"]["parts"][0]["text"].strip()
                if s and len(s) > 50:
                    new_summary = s
        except Exception as e:
            logger.warning(f"Gemini summary rephrase failed: {e}")

    return new_title, new_summary


# ── Watermark / logo check (RULE 2) ───────────────────────────────────────────

WATERMARK_PROMPT = (
    "Does this image contain ANY visible watermark, logo, or branding text from "
    "another media/news website? Examples: YourStory (YS), Economic Times (ET Rise, "
    "ET Tech, ET Markets), Entrackr, Mint/LiveMint, Moneycontrol, Getty Images, "
    "Shutterstock, Dreamstime, Adobe Stock, Reuters, AFP, PTI, ANI, CarTrade, Digit, "
    "StartupTalky, SiliconRoad, or any other publication's name/logo overlaid on the image. "
    "Respond with ONLY valid JSON: "
    '{"has_watermark": true, "reason": "..."} or {"has_watermark": false, "reason": "clean"}'
)

WATERMARK_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent?key={key}"
)


async def image_has_watermark(client: httpx.AsyncClient, image_url: str) -> bool:
    """
    RULE 2: Check image for third-party watermarks via Gemini Vision.
    Returns True if watermark detected (article should be DROPPED).
    Returns False if clean (article may be saved).
    On any error, returns False (benefit of doubt — don't block on API issues).
    """
    if not image_url or not GEMINI_KEY:
        return False
    try:
        r = await client.get(image_url, headers=HEADERS, timeout=12, follow_redirects=True)
        if r.status_code != 200 or len(r.content) < 500:
            return False
        ct = r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
        if ct not in ("image/jpeg", "image/png", "image/webp"):
            ct = "image/jpeg"
        img_b64 = base64.b64encode(r.content).decode("utf-8")
    except Exception as e:
        logger.debug(f"Watermark check download failed for {image_url}: {e}")
        return False

    payload = {
        "contents": [{"parts": [
            {"text": WATERMARK_PROMPT},
            {"inline_data": {"mime_type": ct, "data": img_b64}},
        ]}],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 120,
            "responseMimeType": "application/json",
        },
    }
    try:
        api_url = WATERMARK_GEMINI_URL.format(key=GEMINI_KEY)
        resp = await client.post(api_url, json=payload, timeout=25)
        raw = resp.json()
        if "error" in raw:
            logger.debug(f"Watermark API error: {raw['error'].get('message','?')}")
            return False
        text = raw["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        import json as _json
        result = _json.loads(text)
        if result.get("has_watermark"):
            logger.info(f"[WATERMARK DROP] {image_url[:60]} — {result.get('reason','')}")
            return True
        return False
    except Exception as e:
        logger.debug(f"Watermark check parse error for {image_url}: {e}")
        return False


# ── Article page extractor ─────────────────────────────────────────────────────

async def extract_article_page(client: httpx.AsyncClient, url: str) -> dict:
    """Fetch article page and extract image, text, published_at."""
    result = {"image": "", "text": "", "published_at": None}
    try:
        r = await client.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
        if r.status_code != 200:
            return result
        soup = BeautifulSoup(r.text, "html.parser")

        # Image
        for m in soup.find_all("meta"):
            prop = m.get("property", "") or m.get("name", "")
            if "og:image" in prop or "twitter:image" in prop:
                c = m.get("content", "").strip()
                if c.startswith("http"):
                    result["image"] = c
                    break

        # Text
        text = ""
        for cls in ["entry-content", "artText", "article-body", "Normal", "story-content",
                    "article-content", "post-content", "storyContent", "article__content"]:
            tag = soup.find(attrs={"class": cls})
            if tag:
                t = " ".join(p.get_text(strip=True) for p in tag.find_all("p") if len(p.get_text(strip=True)) > 40)
                if len(t) > 200:
                    text = t
                    break
        if not text:
            art = soup.find("article")
            if art:
                text = " ".join(p.get_text(strip=True) for p in art.find_all("p") if len(p.get_text(strip=True)) > 40)
        if not text:
            text = " ".join(p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 50)
        result["text"] = text[:3000]

        # Published date
        pub_tag = (soup.find("meta", property="article:published_time")
                   or soup.find("meta", attrs={"name": "date"})
                   or soup.find("meta", attrs={"name": "pubdate"}))
        if pub_tag and pub_tag.get("content"):
            try:
                from dateutil import parser as dp
                result["published_at"] = dp.parse(pub_tag["content"]).replace(tzinfo=timezone.utc).isoformat()
            except Exception:
                pass
    except Exception as e:
        logger.debug(f"extract_article_page error for {url}: {e}")
    return result


# ── Core save function ─────────────────────────────────────────────────────────

async def save_startup_article(
    client: httpx.AsyncClient,
    title: str,
    url: str,
    image: str,
    text: str,
    published_at: str,
    source: str,
    trusted: bool = False,
) -> bool:
    """Validate, rephrase, and save a startup article. Returns True if saved."""
    # Dedup check
    existing = await db.news.find_one(
        {"$or": [{"link": url}, {"source_url": url}]},
        {"_id": 0, "id": 1}
    )
    if existing:
        return False

    if not title or not url:
        return False
    if not image:
        return False
    if not is_startup_relevant(title, text, trusted=trusted):
        return False

    # ── RULE 2: Reject articles whose image has a third-party watermark/logo ──
    if await image_has_watermark(client, image):
        return False

    cat = detect_category(title, text)
    if cat not in CATEGORIES:
        cat = "business"

    # ── RULE 1: Always rephrase title and summary via Gemini ─────────────────
    new_title, new_summary = await gemini_rephrase(client, title, text or title)

    doc = {
        "id": str(uuid.uuid4()),
        "title": new_title[:200],
        "title_orig": title[:200],
        "summary": new_summary,
        "summary_orig": text or title,
        "category": cat,
        "category_label": CATEGORIES.get(cat, {}).get("en", cat),
        "image": image,
        "video_url": "", "content_type": "text",
        "link": url,
        "source_url": url,
        "is_pinned": False, "priority": 5, "is_active": True,
        "source": source,
        "seo_description": "",
        "seo_keywords": [],
        "og_title": new_title[:200],
        "og_description": new_summary[:300] if new_summary else "",
        "og_image": image,
        "article_published_time": published_at,
        "published_at": published_at or datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "views": 0,
        "language": "en",
    }
    try:
        await db.news.insert_one(doc)
        logger.info(f"[{cat}] Saved: {new_title[:60]}")
        return True
    except Exception as e:
        if "duplicate" not in str(e).lower():
            logger.error(f"Save error for {url}: {e}")
        return False


# ── RSS scraper ────────────────────────────────────────────────────────────────

RSS_FEEDS = [
    {"url": "https://yourstory.com/category/funding/feed", "source": "YourStory", "trusted": True},
    {"url": "https://yourstory.com/feed",                  "source": "YourStory", "trusted": True},
    {"url": "https://economictimes.indiatimes.com/small-biz/startups/rssfeeds/5575607.cms", "source": "ET Startups", "trusted": True},
    {"url": "https://economictimes.indiatimes.com/tech/funding-and-deals/rssfeeds/90005264.cms", "source": "ET Startups", "trusted": True},
    {"url": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms", "source": "ET Tech", "trusted": True},
    {"url": "https://www.livemint.com/rss/startups",      "source": "Mint", "trusted": True},
    {"url": "https://www.livemint.com/rss/technology",    "source": "Mint", "trusted": True},
    {"url": "https://www.moneycontrol.com/rss/business.xml", "source": "Moneycontrol", "trusted": False},
    {"url": "https://startuptalky.com/feed/",             "source": "StartupTalky", "trusted": True},
    {"url": "https://thetechpanda.com/feed/",             "source": "The Tech Panda", "trusted": True},
    {"url": "https://techcrunch.com/tag/india/feed/",     "source": "TechCrunch", "trusted": False},
    {"url": "https://www.ndtvprofit.com/business/feed",   "source": "NDTV Profit", "trusted": False},
]


async def scrape_rss_feeds(client: httpx.AsyncClient) -> int:
    added = 0
    for feed_cfg in RSS_FEEDS:
        try:
            r = await client.get(feed_cfg["url"], headers=HEADERS, timeout=15, follow_redirects=True)
            if r.status_code != 200:
                continue
            feed = feedparser.parse(r.text)
            for entry in feed.entries[:30]:
                url = getattr(entry, "link", "")
                if not url:
                    continue
                title = getattr(entry, "title", "").strip()
                if not title:
                    continue
                # Quick relevance pre-check on title
                if not is_startup_relevant(title, trusted=feed_cfg["trusted"]):
                    continue

                # Fetch article page
                page = await extract_article_page(client, url)
                if not page["image"]:
                    continue
                if not is_startup_relevant(title, page["text"], trusted=feed_cfg["trusted"]):
                    continue

                ok = await save_startup_article(
                    client=client,
                    title=title,
                    url=url,
                    image=page["image"],
                    text=page["text"],
                    published_at=page["published_at"] or datetime.now(timezone.utc).isoformat(),
                    source=feed_cfg["source"],
                    trusted=feed_cfg["trusted"],
                )
                if ok:
                    added += 1
                await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"RSS feed error [{feed_cfg['source']}]: {e}")
    return added


# ── Entrackr sitemap scraper ───────────────────────────────────────────────────

async def scrape_entrackr_sitemap(client: httpx.AsyncClient, max_days: int = 7) -> int:
    """Scrape Entrackr daily sitemaps for last N days."""
    added = 0
    try:
        r = await client.get("https://entrackr.com/sitemap.xml", headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return 0
        soup = BeautifulSoup(r.text, "html.parser")
        sitemap_locs = [loc.get_text(strip=True) for loc in soup.find_all("loc")][:max_days]

        for sm_url in sitemap_locs:
            try:
                r2 = await client.get(sm_url, headers=HEADERS, timeout=15)
                if r2.status_code != 200:
                    continue
                soup2 = BeautifulSoup(r2.text, "html.parser")
                locs = [loc.get_text(strip=True) for loc in soup2.find_all("loc")]

                # Alternate: article_url, image_url, article_url, image_url...
                for i in range(0, len(locs) - 1, 2):
                    art_url = locs[i]
                    img_url = locs[i + 1] if i + 1 < len(locs) else ""

                    if "entrackr.com" not in art_url or art_url.endswith(".xml"):
                        continue

                    page = await extract_article_page(client, art_url)
                    img = page["image"] or img_url
                    if not img:
                        continue

                    # Get title from article page h1
                    title = ""
                    try:
                        rp = await client.get(art_url, headers=HEADERS, timeout=18, follow_redirects=True)
                        if rp.status_code == 200:
                            sp = BeautifulSoup(rp.text, "html.parser")
                            h1 = sp.find("h1")
                            if h1:
                                title = h1.get_text(strip=True)
                    except Exception:
                        pass
                    if not title:
                        title = art_url.split("/")[-1].replace("-", " ").title()

                    if not is_startup_relevant(title, page["text"], trusted=True):
                        continue

                    ok = await save_startup_article(
                        client=client,
                        title=title,
                        url=art_url,
                        image=img,
                        text=page["text"],
                        published_at=page["published_at"] or datetime.now(timezone.utc).isoformat(),
                        source="Entrackr",
                        trusted=True,
                    )
                    if ok:
                        added += 1
                    await asyncio.sleep(0.3)
            except Exception as e:
                logger.error(f"Entrackr sitemap entry error: {e}")
    except Exception as e:
        logger.error(f"Entrackr sitemap error: {e}")
    return added


# ── Main scraper loop ──────────────────────────────────────────────────────────

async def scraper_loop():
    await asyncio.sleep(10)  # Let server fully start
    while True:
        global scraper_status
        scraper_status["running"] = True
        scraper_status["error"] = None
        total = 0
        try:
            async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
                # RSS feeds first
                rss_added = await scrape_rss_feeds(client)
                total += rss_added
                logger.info(f"RSS scrapers: +{rss_added}")

                # Entrackr sitemap (last 3 days)
                et_added = await scrape_entrackr_sitemap(client, max_days=3)
                total += et_added
                logger.info(f"Entrackr sitemap: +{et_added}")

            scraper_status["last_run"] = datetime.now(timezone.utc).isoformat()
            scraper_status["articles_added"] = total
            logger.info(f"Scraper cycle done: {total} new articles")

            if total > 0:
                # Fire SEO processing
                try:
                    from routes.seo_engine import seo_after_scrape
                    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
                    recent = await db.news.find(
                        {"created_at": {"$gte": cutoff}}, {"_id": 0, "id": 1}
                    ).to_list(100)
                    ids = [a["id"] for a in recent]
                    if ids:
                        asyncio.create_task(seo_after_scrape(ids))
                except Exception as se:
                    logger.error(f"SEO after scrape error: {se}")

        except Exception as e:
            scraper_status["error"] = str(e)
            logger.error(f"Scraper loop error: {e}")
        finally:
            scraper_status["running"] = False

        await asyncio.sleep(3600)  # Run every 60 minutes


# ── API endpoints ──────────────────────────────────────────────────────────────

@router.post("/scraper/trigger")
async def trigger_scraper():
    if scraper_status["running"]:
        return {"status": "already_running"}
    scraper_status["running"] = True
    total = 0
    try:
        async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
            rss = await scrape_rss_feeds(client)
            et = await scrape_entrackr_sitemap(client, max_days=3)
            total = rss + et
    except Exception as e:
        scraper_status["error"] = str(e)
    finally:
        scraper_status["running"] = False
        scraper_status["articles_added"] = total
        scraper_status["last_run"] = datetime.now(timezone.utc).isoformat()
    return {"status": "completed", "articles_added": total}


@router.get("/scraper/status")
async def get_scraper_status():
    return scraper_status


@router.get("/notifications/breaking")
async def get_breaking_news():
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=35)).isoformat()
    articles = await db.news.find(
        {"created_at": {"$gte": cutoff}, "is_active": True},
        {"_id": 0, "id": 1, "title": 1, "category": 1, "image": 1}
    ).sort("created_at", -1).limit(5).to_list(5)
    return {"breaking": articles, "count": len(articles)}


@router.get("/health")
async def health_check():
    return {"status": "ok"}
