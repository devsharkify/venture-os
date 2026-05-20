from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timezone
from database import db, logger, CATEGORIES
from models import Reporter, ReporterRegister, ReporterNews, ReporterNewsSubmit, NewsArticle
from helpers import prepare_for_mongo, parse_from_mongo
from auth_dep import require_admin

router = APIRouter(prefix="/api")

async def generate_reporter_id() -> str:
    count = await db.reporters.count_documents({})
    return f"NP-{str(count + 1).zfill(4)}"

@router.post("/reporter/register", response_model=Reporter)
async def register_reporter(data: ReporterRegister):
    existing = await db.reporters.find_one({"phone": data.phone}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    reporter_id = await generate_reporter_id()
    reporter = Reporter(**data.model_dump(), reporter_id=reporter_id)
    doc = prepare_for_mongo(reporter.model_dump())
    await db.reporters.insert_one(doc)
    return reporter

@router.get("/reporter/check/{phone}")
async def check_reporter_status(phone: str):
    reporter = await db.reporters.find_one({"phone": phone}, {"_id": 0})
    if not reporter:
        return {"registered": False, "status": None}
    return {"registered": True, "status": reporter.get("status"), "reporter_id": reporter.get("reporter_id"), "name": reporter.get("name"), "id": reporter.get("id")}

@router.get("/reporter/{reporter_id}", response_model=Reporter)
async def get_reporter(reporter_id: str):
    reporter = await db.reporters.find_one({"$or": [{"id": reporter_id}, {"reporter_id": reporter_id}]}, {"_id": 0})
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")
    return parse_from_mongo(reporter)

@router.post("/reporter/{reporter_id}/submit-news", response_model=ReporterNews)
async def submit_reporter_news(reporter_id: str, data: ReporterNewsSubmit):
    reporter = await db.reporters.find_one({"$or": [{"id": reporter_id}, {"reporter_id": reporter_id}]}, {"_id": 0})
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")
    if reporter.get("status") != "approved":
        raise HTTPException(status_code=403, detail="Reporter not approved yet")
    news = ReporterNews(**data.model_dump(), reporter_id=reporter.get("reporter_id"), reporter_name=reporter.get("name"))
    doc = prepare_for_mongo(news.model_dump())
    await db.reporter_news.insert_one(doc)
    await db.reporters.update_one({"id": reporter.get("id")}, {"$inc": {"news_submitted": 1}})
    return news

@router.get("/reporter/{reporter_id}/news", response_model=List[ReporterNews])
async def get_reporter_news(reporter_id: str):
    reporter = await db.reporters.find_one({"$or": [{"id": reporter_id}, {"reporter_id": reporter_id}]}, {"_id": 0})
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")
    news_list = await db.reporter_news.find({"reporter_id": reporter.get("reporter_id")}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [parse_from_mongo(n) for n in news_list]

@router.get("/reporter/{reporter_id}/id-card")
async def get_reporter_id_card(reporter_id: str):
    reporter = await db.reporters.find_one({"$or": [{"id": reporter_id}, {"reporter_id": reporter_id}]}, {"_id": 0})
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")
    if reporter.get("status") != "approved":
        raise HTTPException(status_code=403, detail="ID card only available for approved reporters")
    return {"reporter_id": reporter.get("reporter_id"), "name": reporter.get("name"), "phone": reporter.get("phone"), "email": reporter.get("email"), "photo": reporter.get("photo"), "location": reporter.get("location"), "approved_at": reporter.get("approved_at"), "valid_until": "2026-12-31", "organization": "NewsPulse", "designation": "Citizen Reporter"}

# ===== ADMIN REPORTER ROUTES =====

@router.get("/admin/reporters", response_model=List[Reporter])
async def get_all_reporters(status: Optional[str] = None, limit: int = Query(50, ge=1, le=200), skip: int = Query(0, ge=0), _: str = Depends(require_admin)):
    query = {}
    if status:
        query["status"] = status
    reporters = await db.reporters.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [parse_from_mongo(r) for r in reporters]

@router.post("/admin/reporters/{reporter_id}/approve")
async def approve_reporter(reporter_id: str, _: str = Depends(require_admin)):
    result = await db.reporters.find_one_and_update(
        {"$or": [{"id": reporter_id}, {"reporter_id": reporter_id}]},
        {"$set": {"status": "approved", "approved_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat()}},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Reporter not found")
    result.pop("_id", None)
    return {"message": "Reporter approved", "reporter": parse_from_mongo(result)}

@router.post("/admin/reporters/{reporter_id}/reject")
async def reject_reporter(reporter_id: str, reason: str = "", _: str = Depends(require_admin)):
    result = await db.reporters.find_one_and_update(
        {"$or": [{"id": reporter_id}, {"reporter_id": reporter_id}]},
        {"$set": {"status": "rejected", "rejection_reason": reason, "updated_at": datetime.now(timezone.utc).isoformat()}},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Reporter not found")
    result.pop("_id", None)
    return {"message": "Reporter rejected", "reporter": parse_from_mongo(result)}

@router.get("/admin/reporter-news", response_model=List[ReporterNews])
async def get_all_reporter_news(status: Optional[str] = None, limit: int = Query(50, ge=1, le=200), skip: int = Query(0, ge=0), _: str = Depends(require_admin)):
    query = {}
    if status:
        query["status"] = status
    news_list = await db.reporter_news.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [parse_from_mongo(n) for n in news_list]

@router.post("/admin/reporter-news/{news_id}/approve")
async def approve_reporter_news(news_id: str, _: str = Depends(require_admin)):
    news = await db.reporter_news.find_one({"id": news_id}, {"_id": 0})
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    await db.reporter_news.update_one({"id": news_id}, {"$set": {"status": "approved", "approved_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat()}})
    cat_info = CATEGORIES.get(news.get("category"), {"en": news.get("category"), "te": news.get("category")})
    content_type = "text"
    video_url = ""
    if news.get("news_type") == "video_url":
        content_type = "video"
        video_url = news.get("video_url", "")
    elif news.get("news_type") == "reporter_video":
        content_type = "video"
        video_url = news.get("reporter_video_url", "")
    article = NewsArticle(title=news.get("title"), summary=news.get("summary"), category=news.get("category"), category_label=cat_info["en"], image=news.get("image", ""), video_url=video_url, content_type=content_type, source=f"Reporter: {news.get('reporter_name')} ({news.get('reporter_id')})")
    doc = prepare_for_mongo(article.model_dump())
    await db.news.insert_one(doc)
    await db.reporters.update_one({"reporter_id": news.get("reporter_id")}, {"$inc": {"news_approved": 1}})
    return {"message": "News approved and published", "article_id": article.id}

@router.post("/admin/reporter-news/{news_id}/reject")
async def reject_reporter_news(news_id: str, reason: str = "", _: str = Depends(require_admin)):
    result = await db.reporter_news.find_one_and_update({"id": news_id}, {"$set": {"status": "rejected", "rejection_reason": reason, "updated_at": datetime.now(timezone.utc).isoformat()}}, return_document=True)
    if not result:
        raise HTTPException(status_code=404, detail="News not found")
    result.pop("_id", None)
    return {"message": "News rejected", "news": parse_from_mongo(result)}
