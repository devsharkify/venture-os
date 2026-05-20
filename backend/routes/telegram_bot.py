"""Telegram Bot for Mint Street - sends daily reports, ePaper PDFs, error alerts."""
from fastapi import APIRouter, Request
from database import db, logger
from datetime import datetime, timezone, timedelta
import os
import httpx
import asyncio

router = APIRouter(prefix="/api/telegram")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = None  # Set when admin sends /start
API_BASE = "https://api.telegram.org/bot" + BOT_TOKEN


async def tg_send(chat_id, text, parse_mode="HTML"):
    """Send a message via Telegram Bot API."""
    if not BOT_TOKEN or not chat_id:
        return False
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(f"{API_BASE}/sendMessage", json={
            "chat_id": chat_id, "text": text, "parse_mode": parse_mode
        })
        return r.status_code == 200


async def tg_send_document(chat_id, file_bytes, filename, caption=""):
    """Send a document (PDF) via Telegram Bot API."""
    if not BOT_TOKEN or not chat_id:
        return False
    async with httpx.AsyncClient(timeout=30.0) as client:
        files = {"document": (filename, file_bytes, "application/pdf")}
        data = {"chat_id": str(chat_id), "caption": caption}
        r = await client.post(f"{API_BASE}/sendDocument", data=data, files=files)
        return r.status_code == 200


def _ist_now():
    """Get current IST time."""
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)


async def _get_admin_chat_id():
    """Get admin chat ID from DB."""
    global ADMIN_CHAT_ID
    if ADMIN_CHAT_ID:
        return ADMIN_CHAT_ID
    doc = await db.telegram_config.find_one({"key": "admin_chat_id"})
    if doc:
        ADMIN_CHAT_ID = doc.get("value")
    return ADMIN_CHAT_ID


async def _set_admin_chat_id(chat_id):
    """Save admin chat ID to DB."""
    global ADMIN_CHAT_ID
    ADMIN_CHAT_ID = chat_id
    await db.telegram_config.update_one(
        {"key": "admin_chat_id"}, {"$set": {"value": chat_id}}, upsert=True
    )


async def generate_morning_report():
    """Generate morning report text."""
    now = _ist_now()
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    total_articles = await db.news.count_documents({"is_active": True})
    new_today = await db.news.count_documents({"created_at": {"$gte": f"{today}T00:00:00"}})
    new_yesterday = await db.news.count_documents({
        "created_at": {"$gte": f"{yesterday}T00:00:00", "$lt": f"{today}T00:00:00"}
    })

    # Source breakdown
    sources = await db.news.aggregate([
        {"$match": {"created_at": {"$gte": f"{today}T00:00:00"}}},
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(10)
    source_text = "\n".join([f"  {s['_id'] or 'unknown'}: {s['count']}" for s in sources]) or "  No new articles yet"

    # User visits
    visits_today = await db.visitor_log.count_documents({"date": today})

    # Editor report
    editor = await db.editor_reports.find_one({}, {"_id": 0}, sort=[("created_at", -1)])
    editor_text = ""
    if editor and editor.get("hero_articles"):
        heroes = editor["hero_articles"][:3]
        editor_text = "\n<b>Top Stories (Editor Agent):</b>\n" + "\n".join([
            f"  {i+1}. {h['title'][:60]} ({h.get('source','')})" for i, h in enumerate(heroes)
        ])

    return f"""<b>Good Morning! Mint Street Daily Report</b>
<b>Date:</b> {today} (IST)

<b>Article Stats:</b>
  Total articles: {total_articles}
  New today: {new_today}
  Yesterday: {new_yesterday}

<b>Sources Today:</b>
{source_text}

<b>User Visits Today:</b> {visits_today}
{editor_text}

<i>Report generated at {now.strftime('%I:%M %p IST')}</i>"""


async def generate_evening_report():
    """Generate evening report text."""
    now = _ist_now()
    today = now.strftime("%Y-%m-%d")

    new_today = await db.news.count_documents({"created_at": {"$gte": f"{today}T00:00:00"}})
    visits_today = await db.visitor_log.count_documents({"date": today})
    total = await db.news.count_documents({"is_active": True})

    # Investigation highlights
    inv_topics = await db.investigation_topics.find({}, {"_id": 0}).to_list(10)
    inv_text = ""
    if inv_topics:
        inv_text = "\n<b>Investigation Tracker:</b>\n" + "\n".join([
            f"  {t.get('name_en','')}: {t.get('event_count', 0)} events" for t in inv_topics
        ])

    # Category breakdown
    cats = await db.news.aggregate([
        {"$match": {"created_at": {"$gte": f"{today}T00:00:00"}}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]).to_list(5)
    cat_text = "\n".join([f"  {c['_id'] or 'other'}: {c['count']}" for c in cats]) or "  No data"

    return f"""<b>Good Evening! Mint Street Day Summary</b>
<b>Date:</b> {today}

<b>Today's Numbers:</b>
  New articles: {new_today}
  User visits: {visits_today}
  Total articles: {total}

<b>Categories Today:</b>
{cat_text}
{inv_text}

<i>Report generated at {now.strftime('%I:%M %p IST')}</i>"""


async def send_daily_report(report_type="morning"):
    """Send daily report to admin."""
    chat_id = await _get_admin_chat_id()
    if not chat_id:
        logger.warning("No admin chat ID set. User needs to /start the bot.")
        return False
    if report_type == "morning":
        text = await generate_morning_report()
    else:
        text = await generate_evening_report()
    return await tg_send(chat_id, text)


async def send_epaper_pdf(date, slot):
    """Generate and send ePaper PDF to admin via Telegram (English only)."""
    chat_id = await _get_admin_chat_id()
    if not chat_id:
        return False

    try:
        from weasyprint import HTML
        from routes.epaper import get_slot_utc_range, get_edition_label

        if slot:
            start, end = get_slot_utc_range(date, slot)
            query = {"is_active": True, "created_at": {"$gte": start, "$lte": end}}
        else:
            query = {"is_active": True, "published_at": {"$gte": f"{date}T00:00:00", "$lte": f"{date}T23:59:59"}}

        all_articles = await db.news.find(query, {"_id": 0}).sort("published_at", -1).to_list(50)
        all_articles = [a for a in all_articles if a.get("title", "")]

        if not all_articles:
            await tg_send(chat_id, f"No articles found for ePaper {date} {slot}")
            return False

        # Build simple PDF HTML (no images for speed)
        articles_html = ""
        for i, a in enumerate(all_articles[:24]):
            title = a.get("title", "")
            summary = a.get("summary", "")
            if i == 0:
                articles_html += f'<div style="border-bottom:2px solid #F26B1F;padding-bottom:12px;margin-bottom:12px"><h2 style="font-size:18pt;font-weight:800">{title}</h2><p style="font-size:10pt;color:#444;line-height:1.5">{summary[:600]}</p></div>'
            else:
                articles_html += f'<div style="break-inside:avoid;margin-bottom:10px;border-bottom:1px solid #eee;padding-bottom:8px"><h3 style="font-size:11pt;font-weight:700">{title}</h3><p style="font-size:9pt;color:#555;line-height:1.4">{summary[:300]}</p></div>'

        edition = get_edition_label(slot or "evening")
        html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
        @page {{ size: A3; margin: 15mm; }}
        body {{ font-family: 'Inter', Arial, sans-serif; color: #1a1a1a; }}
        .header {{ text-align: center; border-bottom: 4px double #F26B1F; padding-bottom: 10px; margin-bottom: 15px; }}
        .header h1 {{ font-size: 28pt; font-weight: 900; color: #F26B1F; }}
        .content {{ column-count: 2; column-gap: 20px; column-rule: 1px solid #ddd; }}
        </style></head><body>
        <div class="header"><h1>MINT STREET</h1><p>{date} - {edition}</p></div>
        <div class="content">{articles_html}</div>
        </body></html>'''

        pdf_bytes = HTML(string=html).write_pdf()
        filename = f"mint_street_{date}_{slot}.pdf"
        caption = f"Mint Street ePaper - {date} {edition}"

        return await tg_send_document(chat_id, pdf_bytes, filename, caption)
    except Exception as e:
        logger.error(f"PDF generation for Telegram failed: {e}")
        await tg_send(chat_id, f"Failed to generate ePaper PDF: {e}")
        return False


async def send_error_alert(error_msg):
    """Send error alert to admin."""
    chat_id = await _get_admin_chat_id()
    if not chat_id:
        return
    text = f"<b>ALERT: Mint Street Error</b>\n\n{error_msg}\n\n<i>{_ist_now().strftime('%I:%M %p IST')}</i>"
    await tg_send(chat_id, text)


# ============================================================
# Scheduled Tasks - run via subprocess scheduler
# ============================================================

async def scheduled_morning():
    """6 AM IST - Morning report + morning ePaper PDF."""
    today = _ist_now().strftime("%Y-%m-%d")
    await send_daily_report("morning")
    await asyncio.sleep(2)
    await send_epaper_pdf(today, "morning")


async def scheduled_evening():
    """6 PM IST - Evening report + evening ePaper PDF."""
    today = _ist_now().strftime("%Y-%m-%d")
    await send_daily_report("evening")
    await asyncio.sleep(2)
    await send_epaper_pdf(today, "evening")


# ============================================================
# API Endpoints
# ============================================================

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming messages from Telegram."""
    body = await request.json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id:
        return {"ok": True}

    if text == "/start":
        await _set_admin_chat_id(chat_id)
        logger.info(f"Telegram: Admin registered with chat_id={chat_id}")
        await tg_send(chat_id, "<b>Welcome to Mint Street Bot!</b>\n\nYou are now registered as admin.\nYou'll receive:\n- Morning report at 6 AM\n- Evening report at 6 PM\n- ePaper PDFs after each edition\n- Error alerts\n\nCommands: /report /status /pdf")
    elif text == "/report":
        await tg_send(chat_id, "Generating report...")
        text = await generate_morning_report()
        await tg_send(chat_id, text)
    elif text == "/status":
        total = await db.news.count_documents({"is_active": True})
        today = _ist_now().strftime("%Y-%m-%d")
        new_today = await db.news.count_documents({"created_at": {"$gte": f"{today}T00:00:00"}})
        visits = await db.visitor_log.count_documents({"date": today})
        await tg_send(chat_id, f"<b>Status:</b>\nTotal articles: {total}\nNew today: {new_today}\nVisitors today: {visits}")
    elif text == "/pdf":
        today = _ist_now().strftime("%Y-%m-%d")
        await tg_send(chat_id, "Generating ePaper PDF...")
        await send_epaper_pdf(today, "morning")
    elif text == "/help":
        await tg_send(chat_id, "<b>Commands:</b>\n/start - Register as admin\n/report - Get latest report\n/status - Quick status\n/pdf - Get today's ePaper PDFs\n/seo - SEO & Social Media report\n/perf - Tech Performance report\n/help - This message")
    elif text == "/seo":
        await tg_send(chat_id, "Generating SEO report...")
        from routes.seo_agent import generate_seo_telegram_report
        seo_text = await generate_seo_telegram_report()
        await tg_send(chat_id, seo_text)
    elif text == "/perf":
        await tg_send(chat_id, "Generating performance report...")
        from routes.tech_agent import generate_perf_telegram_report, generate_performance_report
        await generate_performance_report()
        perf_text = await generate_perf_telegram_report()
        await tg_send(chat_id, perf_text)
    else:
        await tg_send(chat_id, "Unknown command. Type /help for available commands.")

    return {"ok": True}


@router.post("/send-report/{report_type}")
async def api_send_report(report_type: str):
    """Manually trigger a report."""
    success = await send_daily_report(report_type)
    return {"status": "sent" if success else "failed"}


@router.post("/send-pdf")
async def api_send_pdf(date: str = "", slot: str = "morning"):
    """Manually send ePaper PDF."""
    if not date:
        date = _ist_now().strftime("%Y-%m-%d")
    success = await send_epaper_pdf(date, slot)
    return {"status": "sent" if success else "failed"}


@router.get("/config")
async def get_config():
    """Get bot configuration."""
    chat_id = await _get_admin_chat_id()
    return {"admin_chat_id": chat_id, "bot_configured": bool(BOT_TOKEN)}
