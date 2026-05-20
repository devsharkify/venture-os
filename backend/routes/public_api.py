"""Public Content API - API key authenticated endpoints for content syndication."""
from fastapi import APIRouter, HTTPException, Header, Query, Request, Depends
from auth_dep import require_admin
from datetime import datetime, timezone, timedelta
from database import db, logger, CATEGORIES
import uuid
import hashlib
import secrets
import time as _time

router = APIRouter(prefix="/api/public/v1")
admin_router = APIRouter(prefix="/api/apikeys", dependencies=[Depends(require_admin)])

# In-memory rate limit tracking: {key_hash: {date: count}}
_rate_limits = {}
DAILY_LIMIT = 1000

# Feed projection - clean, lightweight response
PUBLIC_FIELDS = {
    "_id": 0, "id": 1, "title": 1, "summary": 1,
    "category": 1, "category_label": 1, "image": 1, "source": 1,
    "link": 1, "published_at": 1, "content_type": 1,
}


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


async def _validate_key(api_key: str) -> dict:
    """Validate API key, check rate limit, track usage."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key. Include X-API-Key header.")

    key_hash = _hash_key(api_key)
    key_doc = await db.api_keys.find_one({"key_hash": key_hash}, {"_id": 0})
    if not key_doc:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    if not key_doc.get("active", True):
        raise HTTPException(status_code=403, detail="API key has been revoked.")

    # Rate limiting
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    limit_key = f"{key_hash}:{today}"
    current = _rate_limits.get(limit_key, 0)
    daily_limit = key_doc.get("daily_limit", DAILY_LIMIT)
    if current >= daily_limit:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. {daily_limit} requests/day.")

    _rate_limits[limit_key] = current + 1

    # Track usage (async, don't block)
    await db.api_keys.update_one(
        {"key_hash": key_hash},
        {"$inc": {"total_requests": 1, f"daily_usage.{today}": 1},
         "$set": {"last_used": datetime.now(timezone.utc).isoformat()}}
    )

    return key_doc


# ============================================================
# PUBLIC API ENDPOINTS
# ============================================================

@router.get("/feed")
async def public_feed(
    x_api_key: str = Header(None, alias="X-API-Key"),
    category: str = Query(None),
    lang: str = Query("en", regex="^(en|te)$"),
    page: int = Query(1, ge=1, le=100),
    limit: int = Query(20, ge=1, le=50),
):
    """Get latest articles feed. Requires X-API-Key header."""
    await _validate_key(x_api_key)

    query = {"is_active": True}
    if category and category in CATEGORIES:
        query["category"] = category

    skip = (page - 1) * limit
    articles = await db.news.find(query, PUBLIC_FIELDS).sort(
        "published_at", -1
    ).skip(skip).limit(limit).to_list(limit)

    total = await db.news.count_documents(query)

    # Format based on language preference
    result = []
    for a in articles:
        item = {
            "id": a.get("id"),
            "title": a.get("title", ""),
            "summary": a.get("summary", ""),
            "category": a.get("category", ""),
            "category_label": a.get("category_label", ""),
            "image": a.get("image", ""),
            "source": a.get("source", ""),
            "link": a.get("link", ""),
            "published_at": a.get("published_at", ""),
            "content_type": a.get("content_type", "article"),
        }
        result.append(item)

    return {
        "status": "ok",
        "articles": result,
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": skip + limit < total,
    }


@router.get("/articles/{article_id}")
async def public_article(
    article_id: str,
    x_api_key: str = Header(None, alias="X-API-Key"),
    lang: str = Query("en", regex="^(en|te)$"),
):
    """Get a single article by ID."""
    await _validate_key(x_api_key)

    article = await db.news.find_one({"id": article_id, "is_active": True}, PUBLIC_FIELDS)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found.")

    return {
        "status": "ok",
        "article": {
            "id": article.get("id"),
            "title": article.get("title", ""),
            "summary": article.get("summary", ""),
            "category": article.get("category", ""),
            "category_label": article.get("category_label", ""),
            "image": article.get("image", ""),
            "source": article.get("source", ""),
            "link": article.get("link", ""),
            "published_at": article.get("published_at", ""),
            "content_type": article.get("content_type", "article"),
        }
    }


@router.get("/categories")
async def public_categories(
    x_api_key: str = Header(None, alias="X-API-Key"),
):
    """Get available news categories."""
    await _validate_key(x_api_key)
    cats = [{"id": k, "label_en": v["en"]} for k, v in CATEGORIES.items()]
    return {"status": "ok", "categories": cats}


@router.get("/search")
async def public_search(
    q: str = Query(..., min_length=2, max_length=200),
    x_api_key: str = Header(None, alias="X-API-Key"),
    lang: str = Query("en", regex="^(en|te)$"),
    page: int = Query(1, ge=1, le=50),
    limit: int = Query(20, ge=1, le=50),
):
    """Search articles by keyword."""
    await _validate_key(x_api_key)

    # Text search on title and summary
    query = {
        "is_active": True,
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"summary": {"$regex": q, "$options": "i"}},
        ]
    }
    skip = (page - 1) * limit
    articles = await db.news.find(query, PUBLIC_FIELDS).sort(
        "published_at", -1
    ).skip(skip).limit(limit).to_list(limit)

    total = await db.news.count_documents(query)

    result = []
    for a in articles:
        result.append({
            "id": a.get("id"),
            "title": a.get("title", ""),
            "summary": a.get("summary", ""),
            "category": a.get("category", ""),
            "image": a.get("image", ""),
            "source": a.get("source", ""),
            "published_at": a.get("published_at", ""),
        })

    return {
        "status": "ok",
        "query": q,
        "articles": result,
        "total": total,
        "page": page,
        "has_more": skip + limit < total,
    }


# ============================================================
# API KEY MANAGEMENT (Admin only)
# ============================================================

@admin_router.post("/create")
async def create_api_key(
    name: str = Query(..., min_length=1, max_length=100),
    daily_limit: int = Query(1000, ge=100, le=50000),
):
    """Create a new API key for a partner."""
    raw_key = f"kn_{secrets.token_hex(24)}"
    key_hash = _hash_key(raw_key)

    doc = {
        "id": str(uuid.uuid4()),
        "name": name,
        "key_hash": key_hash,
        "key_prefix": raw_key[:10] + "...",
        "active": True,
        "daily_limit": daily_limit,
        "total_requests": 0,
        "daily_usage": {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_used": None,
    }
    await db.api_keys.insert_one(doc)
    await db.api_keys.create_index("key_hash", unique=True)

    return {
        "status": "ok",
        "api_key": raw_key,
        "name": name,
        "daily_limit": daily_limit,
        "message": "Save this key securely. It won't be shown again.",
    }


@admin_router.get("/list")
async def list_api_keys():
    """List all API keys (without revealing full keys)."""
    keys = await db.api_keys.find({}, {"_id": 0, "key_hash": 0}).sort("created_at", -1).to_list(100)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for k in keys:
        usage = k.get("daily_usage", {})
        k["requests_today"] = usage.get(today, 0)
        # Keep only last 7 days of daily_usage
        k["daily_usage"] = {d: c for d, c in sorted(usage.items(), reverse=True)[:7]}

    return {"status": "ok", "keys": keys}


@admin_router.put("/{key_id}/toggle")
async def toggle_api_key(key_id: str):
    """Activate or deactivate an API key."""
    key_doc = await db.api_keys.find_one({"id": key_id}, {"_id": 0, "active": 1})
    if not key_doc:
        raise HTTPException(status_code=404, detail="Key not found.")

    new_status = not key_doc.get("active", True)
    await db.api_keys.update_one({"id": key_id}, {"$set": {"active": new_status}})
    return {"status": "ok", "active": new_status}


@admin_router.delete("/{key_id}")
async def delete_api_key(key_id: str):
    """Permanently delete an API key."""
    result = await db.api_keys.delete_one({"id": key_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Key not found.")
    return {"status": "ok", "deleted": True}


@admin_router.get("/{key_id}/usage")
async def get_key_usage(key_id: str):
    """Get detailed usage stats for an API key."""
    key_doc = await db.api_keys.find_one({"id": key_id}, {"_id": 0, "key_hash": 0})
    if not key_doc:
        raise HTTPException(status_code=404, detail="Key not found.")

    usage = key_doc.get("daily_usage", {})
    last_7_days = dict(sorted(usage.items(), reverse=True)[:7])

    return {
        "status": "ok",
        "name": key_doc.get("name"),
        "total_requests": key_doc.get("total_requests", 0),
        "daily_limit": key_doc.get("daily_limit", DAILY_LIMIT),
        "last_used": key_doc.get("last_used"),
        "daily_usage": last_7_days,
    }
