from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime, timezone
from io import StringIO
import csv
from database import db, logger
from models import StartupApplication, StartupApplicationCreate
from helpers import prepare_for_mongo, parse_from_mongo
from auth_dep import require_admin

router = APIRouter(prefix="/api")


@router.post("/startup/apply", response_model=StartupApplication)
async def submit_startup_application(data: StartupApplicationCreate):
    existing = await db.startup_applications.find_one({"mobile": data.mobile}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="An application with this mobile number already exists")
    application = StartupApplication(**data.model_dump())
    doc = prepare_for_mongo(application.model_dump())
    await db.startup_applications.insert_one(doc)
    logger.info(f"New startup application: {application.name} ({application.mobile})")
    return application


@router.get("/startup/check/{mobile}")
async def check_startup_application(mobile: str):
    app = await db.startup_applications.find_one({"mobile": mobile}, {"_id": 0})
    if not app:
        return {"applied": False}
    return {"applied": True, "status": app.get("status"), "id": app.get("id"), "created_at": app.get("created_at")}


@router.get("/admin/startup-applications", response_model=List[StartupApplication])
async def get_all_startup_applications(status: Optional[str] = None, limit: int = Query(50, ge=1, le=200), skip: int = Query(0, ge=0), _: str = Depends(require_admin)):
    query = {}
    if status:
        query["status"] = status
    apps = await db.startup_applications.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [parse_from_mongo(a) for a in apps]


@router.post("/admin/startup-applications/{app_id}/update-status")
async def update_application_status(app_id: str, status: str, reason: str = "", _: str = Depends(require_admin)):
    if status not in ["submitted", "shortlisted", "interviewed", "selected", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    update = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if status == "rejected" and reason:
        update["rejection_reason"] = reason
    result = await db.startup_applications.find_one_and_update(
        {"id": app_id},
        {"$set": update},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Application not found")
    result.pop("_id", None)
    return {"message": f"Application marked as {status}", "application": parse_from_mongo(result)}


@router.get("/admin/startup-applications/export")
async def export_startup_applications_csv(status: Optional[str] = None, _: str = Depends(require_admin)):
    """Export all applications as CSV (Excel-compatible). Filter by status optional."""
    query = {}
    if status:
        query["status"] = status
    apps = await db.startup_applications.find(query, {"_id": 0}).sort("created_at", -1).to_list(10000)

    columns = [
        "id", "name", "mobile", "email", "age",
        "colony", "area", "city", "is_woman_founder",
        "idea", "status", "rejection_reason",
        "pitch_pdf_url", "pitch_video_url",
        "created_at", "updated_at",
    ]

    buf = StringIO()
    buf.write("\ufeff")  # UTF-8 BOM for Excel compatibility
    writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore", quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for app in apps:
        row = {col: app.get(col, "") for col in columns}
        writer.writerow(row)

    buf.seek(0)
    filename = f"startup-applications-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
