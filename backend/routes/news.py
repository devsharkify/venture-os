from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import os
from database import db, logger, CATEGORIES, EMERGENT_LLM_KEY
from models import NewsArticle, NewsCreate, NewsUpdate, ScrapeRequest, ScrapeResponse, StatusCheck, StatusCheckCreate
from helpers import prepare_for_mongo, parse_from_mongo, scrape_url, rephrase_with_ai, translate_to_telugu, translate_to_english
from auth_dep import require_admin
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter(prefix="/api")

# Projection for feed — only fields the frontend actually needs
FEED_PROJECTION = {
    "_id": 0, "id": 1, "title": 1, "title_te": 1, "summary": 1, "summary_te": 1,
    "category": 1, "category_label": 1, "category_label_te": 1, "image": 1,
    "video_url": 1, "content_type": 1, "link": 1, "is_pinned": 1, "source": 1,
    "published_at": 1, "created_at": 1,
}

# Simple in-memory cache with TTL
_cache = {}
import time as _time

def _cached(key, ttl=60):
    entry = _cache.get(key)
    if entry and (_time.time() - entry[1]) < ttl:
        return entry[0]
    return None

def _set_cache(key, value, ttl=60):
    _cache[key] = (value, _time.time())

@router.get("/")
async def root():
    return {"message": "NewsPulse API - Way2News Style News App"}

@router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.model_dump())
    doc = prepare_for_mongo(status_obj.model_dump())
    await db.status_checks.insert_one(doc)
    return status_obj

@router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    return [parse_from_mongo(c) for c in checks]

@router.get("/news/categories")
async def get_categories():
    return {"categories": CATEGORIES}

@router.get("/news/article/{article_id}")
async def get_article_by_id(article_id: str):
    article = await db.news.find_one({"id": article_id, "is_active": True}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.get("/public/news")
async def public_news_api(limit: int = Query(20, ge=1, le=50), skip: int = Query(0, ge=0), category: Optional[str] = Query(None)):
    query = {"is_active": True}
    if category and category in CATEGORIES:
        query["category"] = category
    articles = await db.news.find(
        query,
        {"_id": 0, "id": 1, "title": 1, "image": 1, "link": 1, "category": 1, "category_label": 1, "published_at": 1,
         "seo_description": 1, "seo_keywords": 1, "og_title": 1, "og_description": 1, "og_image": 1, "article_published_time": 1}
    ).sort("published_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.news.count_documents(query)
    return {"total": total, "limit": limit, "skip": skip, "articles": articles, "categories": list(CATEGORIES.keys())}

@router.get("/news/search")
async def search_news(q: str = Query(..., min_length=2, max_length=200), limit: int = Query(20, ge=1, le=100), skip: int = Query(0, ge=0)):
    """Search articles by keyword in titles and summaries."""
    import re
    safe_q = re.escape(q)
    query = {
        "is_active": True,
        "$or": [
            {"title": {"$regex": safe_q, "$options": "i"}},
            {"summary": {"$regex": safe_q, "$options": "i"}},
            {"title_te": {"$regex": safe_q, "$options": "i"}},
            {"summary_te": {"$regex": safe_q, "$options": "i"}},
        ]
    }
    articles = await db.news.find(query, FEED_PROJECTION).sort("published_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.news.count_documents(query)
    return {"articles": articles, "total": total, "query": q}

@router.get("/news/feed")
async def get_all_news(limit: int = Query(20, ge=1, le=100), skip: int = Query(0, ge=0), sort: str = Query("newest", regex="^(newest|oldest)$"), time_filter: str = Query("all", regex="^(all|1d|1w|1m|1y)$")):
    cache_key = f"feed:{limit}:{skip}:{sort}:{time_filter}"
    cached = _cached(cache_key, ttl=30)
    if cached:
        return cached

    query = {"is_active": True}
    if time_filter != "all":
        now = datetime.now(timezone.utc)
        delta_map = {"1d": timedelta(days=1), "1w": timedelta(weeks=1), "1m": timedelta(days=30), "1y": timedelta(days=365)}
        query["published_at"] = {"$gte": (now - delta_map[time_filter]).isoformat()}
    sort_dir = -1 if sort == "newest" else 1
    articles = await db.news.find(query, FEED_PROJECTION).sort([("is_pinned", -1), ("published_at", sort_dir)]).skip(skip).limit(limit).to_list(limit)
    _set_cache(cache_key, articles, ttl=30)
    return articles

@router.get("/news/category/{category}")
async def get_news_by_category(category: str, limit: int = Query(20, ge=1, le=100), skip: int = Query(0, ge=0), sort: str = Query("newest", regex="^(newest|oldest)$"), time_filter: str = Query("all", regex="^(all|1d|1w|1m|1y)$")):
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    cache_key = f"cat:{category}:{limit}:{skip}:{sort}:{time_filter}"
    cached = _cached(cache_key, ttl=30)
    if cached:
        return cached

    query = {"category": category, "is_active": True}
    if time_filter != "all":
        now = datetime.now(timezone.utc)
        delta_map = {"1d": timedelta(days=1), "1w": timedelta(weeks=1), "1m": timedelta(days=30), "1y": timedelta(days=365)}
        query["published_at"] = {"$gte": (now - delta_map[time_filter]).isoformat()}
    sort_dir = -1 if sort == "newest" else 1
    articles = await db.news.find(query, FEED_PROJECTION).sort([("is_pinned", -1), ("published_at", sort_dir)]).skip(skip).limit(limit).to_list(limit)
    _set_cache(cache_key, articles, ttl=30)
    return articles

@router.get("/news/article/{article_id}", response_model=NewsArticle)
async def get_article(article_id: str):
    article = await db.news.find_one({"id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return parse_from_mongo(article)

@router.post("/news/translate-batch")
async def translate_batch(article_ids: List[str]):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="Translation service not configured")
    translated = []
    for aid in article_ids[:10]:
        article = await db.news.find_one({"id": aid}, {"_id": 0})
        if not article:
            continue
        if article.get("title_te") and len(article.get("title_te", "")) > 3:
            translated.append({"id": aid, "title_te": article["title_te"], "summary_te": article.get("summary_te", "")})
            continue
        try:
            chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"translate-{aid[:8]}",
                system_message="You are a senior Telugu news editor at a popular Telugu news channel. Rewrite the given English news into natural, everyday Telugu. Use simple spoken Telugu. Avoid literal translation. Use Telugu script. Keep names, places, numbers as-is. Output ONLY Telugu text."
            ).with_model("gemini", "gemini-2.5-flash")
            title_resp = await chat.send_message(UserMessage(text=f"Translate to Telugu:\n{article.get('title', '')}"))
            title_te = title_resp.strip() if title_resp else ""
            summary_te = ""
            summary_text = article.get('summary', '')[:500]
            if summary_text:
                chat2 = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"translate-{aid[:8]}-s",
                    system_message="You are a senior Telugu news editor at a popular Telugu news channel. Rewrite the given English news into natural, everyday Telugu. Use simple spoken Telugu. Avoid literal translation. Use Telugu script. Keep names, places, numbers as-is. Output ONLY Telugu text."
                ).with_model("gemini", "gemini-2.5-flash")
                summary_resp = await chat2.send_message(UserMessage(text=f"Translate to Telugu:\n{summary_text}"))
                summary_te = summary_resp.strip() if summary_resp else ""
            await db.news.update_one({"id": aid}, {"$set": {"title_te": title_te, "summary_te": summary_te}})
            translated.append({"id": aid, "title_te": title_te, "summary_te": summary_te})
        except Exception as e:
            logger.error(f"Translation error for {aid}: {e}")
            translated.append({"id": aid, "title_te": "", "summary_te": ""})
    return translated

MIN_SUMMARY_LINES = 4

@router.post("/news/admin/push", response_model=NewsArticle)
async def create_news(news: NewsCreate):
    summary_lines = [l.strip() for l in news.summary.strip().split("\n") if l.strip()]
    if len(summary_lines) < MIN_SUMMARY_LINES:
        raise HTTPException(status_code=400, detail=f"Description must have at least {MIN_SUMMARY_LINES} lines. Currently has {len(summary_lines)} line(s).")
    cat_info = CATEGORIES.get(news.category, {"en": news.category, "te": news.category})
    create_data = news.model_dump()
    custom_date = create_data.pop("published_at", None)
    article = NewsArticle(**create_data, category_label=cat_info["en"], category_label_te=cat_info["te"])
    doc = prepare_for_mongo(article.model_dump())
    if custom_date:
        doc["published_at"] = custom_date
        doc["created_at"] = custom_date
    await db.news.insert_one(doc)
    doc.pop("_id", None)
    # Auto-translate if Telugu fields missing
    try:
        if doc.get("title") and not doc.get("title_te"):
            te_title = await translate_to_telugu(doc["title"])
            te_summary = await translate_to_telugu(doc.get("summary", ""))
            if te_title:
                await db.news.update_one({"id": doc["id"]}, {"$set": {"title_te": te_title, "summary_te": te_summary or ""}})
                doc["title_te"] = te_title
                doc["summary_te"] = te_summary or ""
        elif doc.get("title_te") and not doc.get("title"):
            en_title = await translate_to_english(doc["title_te"])
            en_summary = await translate_to_english(doc.get("summary_te", ""))
            if en_title:
                await db.news.update_one({"id": doc["id"]}, {"$set": {"title": en_title, "summary": en_summary or ""}})
                doc["title"] = en_title
                doc["summary"] = en_summary or ""
    except Exception as e:
        logger.error(f"Auto-translate failed for admin push {doc['id']}: {e}")
    return doc

@router.get("/news/admin/all")
async def get_all_admin_news(
    q: Optional[str] = Query(None, max_length=200),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    _: str = Depends(require_admin),
):
    query = {}
    if q and len(q.strip()) >= 2:
        rx = {"$regex": q.strip(), "$options": "i"}
        query["$or"] = [{"title": rx}, {"title_te": rx}, {"summary": rx}, {"summary_te": rx}, {"source": rx}]
    if category:
        query["category"] = category
    total = await db.news.count_documents(query)
    cursor = db.news.find(query, {"_id": 0}).sort([("created_at", -1)]).skip(skip).limit(limit)
    articles = await cursor.to_list(limit)
    return {
        "total": total,
        "limit": limit,
        "skip": skip,
        "articles": [parse_from_mongo(a) for a in articles],
    }

@router.put("/news/admin/{article_id}", response_model=NewsArticle)
async def update_news(article_id: str, news: NewsUpdate):
    update_data = {k: v for k, v in news.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    if "category" in update_data:
        cat_info = CATEGORIES.get(update_data["category"], {"en": update_data["category"], "te": update_data["category"]})
        update_data["category_label"] = cat_info["en"]
        update_data["category_label_te"] = cat_info["te"]
    result = await db.news.find_one_and_update({"id": article_id}, {"$set": update_data}, return_document=True)
    if not result:
        raise HTTPException(status_code=404, detail="Article not found")
    result.pop("_id", None)
    return parse_from_mongo(result)

@router.post("/news/admin/{article_id}/pin", response_model=NewsArticle)
async def toggle_pin(article_id: str):
    article = await db.news.find_one({"id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    new_pin = not article.get("is_pinned", False)
    result = await db.news.find_one_and_update(
        {"id": article_id}, {"$set": {"is_pinned": new_pin, "updated_at": datetime.now(timezone.utc).isoformat()}}, return_document=True
    )
    result.pop("_id", None)
    return parse_from_mongo(result)

@router.delete("/news/admin/{article_id}")
async def delete_news(article_id: str):
    result = await db.news.delete_one({"id": article_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted successfully", "id": article_id}

@router.post("/news/scrape", response_model=ScrapeResponse)
async def scrape_and_rephrase(request: ScrapeRequest):
    scraped = await scrape_url(request.url)
    title = scraped['title']
    summary = scraped['summary']
    title_te = ""
    summary_te = ""
    if request.rephrase:
        title = await rephrase_with_ai(title, is_title=True)
        summary = await rephrase_with_ai(summary, is_title=False)
    # Enforce 4+ paragraph minimum
    from helpers import ensure_min_paragraphs
    summary = ensure_min_paragraphs(summary, min_paragraphs=MIN_SUMMARY_LINES)
    if request.translate_to_telugu:
        title_te = await translate_to_telugu(title)
        summary_te = await translate_to_telugu(summary)
    return ScrapeResponse(title=title, title_te=title_te, summary=summary, summary_te=summary_te, image=scraped['image'], source=request.url)


@router.post("/news/admin/backfill-summaries")
async def backfill_thin_summaries(limit: int = 200, use_ai: bool = True, _: str = Depends(require_admin)):
    """Repair existing articles whose summary has fewer than 4 paragraphs.
    First tries to reformat existing sentences (no AI); if still <4 paragraphs and use_ai=True,
    asks AI to expand the brief. Returns count of fixed rows."""
    from helpers import ensure_min_paragraphs, expand_summary_with_ai
    fixed = 0
    expanded_count = 0
    # Target only articles whose summary lacks paragraph breaks (no \n\n)
    cursor = db.news.find(
        {"is_active": True, "summary": {"$exists": True, "$ne": "", "$not": {"$regex": "\n\n"}}},
        {"_id": 0, "id": 1, "summary": 1, "summary_te": 1},
    ).sort("created_at", -1).limit(limit)
    async for art in cursor:
        s = (art.get("summary") or "").strip()
        if not s:
            continue
        paras = [p for p in s.split("\n\n") if p.strip()]
        if len(paras) >= 4:
            continue
        new_s = ensure_min_paragraphs(s, min_paragraphs=4)
        new_paras = [p for p in new_s.split("\n\n") if p.strip()]
        if len(new_paras) < 4 and use_ai:
            new_s = await expand_summary_with_ai(s, source_full_text="", min_paragraphs=4)
            expanded_count += 1
        if new_s == s:
            continue
        update = {"summary": new_s, "updated_at": datetime.now(timezone.utc).isoformat()}
        s_te = (art.get("summary_te") or "").strip()
        if s_te and len([p for p in s_te.split("\n\n") if p.strip()]) < 4:
            te_new = ensure_min_paragraphs(s_te, min_paragraphs=4)
            te_paras = [p for p in te_new.split("\n\n") if p.strip()]
            if len(te_paras) < 4 and use_ai:
                te_new = await expand_summary_with_ai(s_te, source_full_text="", min_paragraphs=4)
            update["summary_te"] = te_new
        await db.news.update_one({"id": art["id"]}, {"$set": update})
        fixed += 1
    return {"message": f"Backfilled {fixed} thin summaries (AI-expanded {expanded_count})", "fixed": fixed, "ai_expanded": expanded_count, "scanned_limit": limit}
