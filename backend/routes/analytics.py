from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone, timedelta
import io
import csv
from database import db, logger
from helpers import prepare_for_mongo, parse_from_mongo

router = APIRouter(prefix="/api")

@router.post("/news/{article_id}/view")
async def record_view(article_id: str, user_phone: str = "", duration: int = 0, source: str = "app"):
    import uuid
    view = {"id": str(uuid.uuid4()), "article_id": article_id, "user_phone": user_phone, "viewed_at": datetime.now(timezone.utc).isoformat(), "view_duration": duration, "source": source}
    await db.article_views.insert_one(view)
    await db.news.update_one({"id": article_id}, {"$inc": {"view_count": 1}})
    return {"status": "recorded"}

@router.get("/news/{article_id}/stats")
async def get_article_stats(article_id: str):
    article = await db.news.find_one({"id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    view_count = await db.article_views.count_documents({"article_id": article_id})
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    pipeline = [
        {"$match": {"article_id": article_id, "viewed_at": {"$gte": seven_days_ago.isoformat()}}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": {"$toDate": "$viewed_at"}}}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    daily_views = await db.article_views.aggregate(pipeline).to_list(100)
    return {"article_id": article_id, "title": article.get("title"), "total_views": view_count, "daily_views": daily_views}

@router.get("/analytics/overview")
async def get_analytics_overview():
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    total_articles = await db.news.count_documents({"is_active": True})
    total_reporters = await db.reporters.count_documents({})
    approved_reporters = await db.reporters.count_documents({"status": "approved"})
    total_users = await db.users.count_documents({})
    views_today = await db.article_views.count_documents({"viewed_at": {"$gte": today.isoformat()}})
    views_week = await db.article_views.count_documents({"viewed_at": {"$gte": week_ago.isoformat()}})
    views_month = await db.article_views.count_documents({"viewed_at": {"$gte": month_ago.isoformat()}})
    top_articles_pipeline = [{"$group": {"_id": "$article_id", "views": {"$sum": 1}}}, {"$sort": {"views": -1}}, {"$limit": 10}]
    top_article_ids = await db.article_views.aggregate(top_articles_pipeline).to_list(10)
    top_articles = []
    for item in top_article_ids:
        article = await db.news.find_one({"id": item["_id"]}, {"_id": 0, "id": 1, "title": 1, "category": 1})
        if article:
            top_articles.append({**article, "views": item["views"]})
    category_pipeline = [
        {"$lookup": {"from": "news", "localField": "article_id", "foreignField": "id", "as": "article"}},
        {"$unwind": "$article"},
        {"$group": {"_id": "$article.category", "views": {"$sum": 1}}},
        {"$sort": {"views": -1}}
    ]
    views_by_category = await db.article_views.aggregate(category_pipeline).to_list(20)
    daily_pipeline = [
        {"$match": {"viewed_at": {"$gte": week_ago.isoformat()}}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": {"$toDate": "$viewed_at"}}}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    daily_trend = await db.article_views.aggregate(daily_pipeline).to_list(10)
    return {
        "summary": {"total_articles": total_articles, "total_reporters": total_reporters, "approved_reporters": approved_reporters, "total_users": total_users, "views_today": views_today, "views_week": views_week, "views_month": views_month},
        "top_articles": top_articles, "views_by_category": views_by_category, "daily_trend": daily_trend
    }

@router.get("/analytics/report/csv")
async def download_analytics_csv(start_date: str = None, end_date: str = None):
    query = {}
    if start_date:
        query["viewed_at"] = {"$gte": start_date}
    if end_date:
        if "viewed_at" in query:
            query["viewed_at"]["$lte"] = end_date
        else:
            query["viewed_at"] = {"$lte": end_date}
    views = await db.article_views.find(query, {"_id": 0}).to_list(10000)
    articles = {}
    for view in views:
        aid = view.get("article_id")
        if aid and aid not in articles:
            article = await db.news.find_one({"id": aid}, {"_id": 0, "title": 1, "category": 1})
            articles[aid] = article or {}
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Article ID", "Title", "Category", "User Phone", "Duration (sec)", "Source"])
    for view in views:
        aid = view.get("article_id", "")
        article = articles.get(aid, {})
        writer.writerow([view.get("viewed_at", ""), aid, article.get("title", ""), article.get("category", ""), view.get("user_phone", ""), view.get("view_duration", 0), view.get("source", "")])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=analytics_report_{datetime.now().strftime('%Y%m%d')}.csv"})

@router.get("/analytics/articles")
async def get_articles_analytics(limit: int = Query(50, ge=1, le=200), skip: int = Query(0, ge=0)):
    pipeline = [{"$group": {"_id": "$article_id", "view_count": {"$sum": 1}}}]
    view_counts = await db.article_views.aggregate(pipeline).to_list(1000)
    view_map = {v["_id"]: v["view_count"] for v in view_counts}
    articles = await db.news.find({"is_active": True}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for article in articles:
        article["view_count"] = view_map.get(article.get("id"), 0)
    articles.sort(key=lambda x: x.get("view_count", 0), reverse=True)
    return articles
