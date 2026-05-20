from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone, timedelta
import io
from database import db, logger
from helpers import expand_summary_for_epaper, is_good_image, trim_to_complete_sentences

router = APIRouter(prefix="/api")

IST_OFFSET = timedelta(hours=5, minutes=30)


@router.get("/epaper/pdf-check")
async def pdf_health_check():
    """Diagnostic endpoint to check if PDF generation works on this server."""
    issues = []
    try:
        from weasyprint import HTML
    except ImportError as e:
        issues.append(f"WeasyPrint not installed: {e}")
    try:
        from weasyprint import HTML as WH
        pdf = WH(string="<html><body><h1>Test</h1></body></html>").write_pdf()
        if not pdf or len(pdf) < 100:
            issues.append("PDF generation returned empty output")
    except Exception as e:
        issues.append(f"PDF generation failed: {e}")
    return {"status": "ok" if not issues else "error", "issues": issues}


EPAPER_PAGES = [
    {"key": "front", "title_en": "Front Page", "categories": None, "limit": 8},
    {"key": "funding", "title_en": "Funding & VC", "categories": ["funding", "vc"], "limit": 15},
    {"key": "startups", "title_en": "Startups", "categories": ["startups", "startup", "d2c"], "limit": 15},
    {"key": "ipo", "title_en": "IPO & Markets", "categories": ["ipo"], "limit": 15},
    {"key": "deeptech", "title_en": "Deep Tech & AI", "categories": ["deeptech", "tech", "saas"], "limit": 15},
    {"key": "policy", "title_en": "Policy", "categories": ["policy"], "limit": 15},
    {"key": "climate", "title_en": "Climate & Energy", "categories": ["climate"], "limit": 15},
]


def get_slot_utc_range(date_str: str, slot: str):
    """Get UTC time range for a given IST date and edition slot."""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    if slot == "morning":
        start_utc = d - timedelta(hours=5, minutes=30)
        end_utc = d + timedelta(hours=8, minutes=30)
    else:
        start_utc = d + timedelta(hours=8, minutes=30)
        end_utc = d + timedelta(hours=18, minutes=30)
    return start_utc.strftime("%Y-%m-%dT%H:%M:%S"), end_utc.strftime("%Y-%m-%dT%H:%M:%S")


def classify_article_slot(created_at_str: str):
    """Classify an article into (date, slot) based on created_at UTC string."""
    try:
        dt_utc = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        dt_ist = dt_utc + IST_OFFSET
        date_ist = dt_ist.strftime("%Y-%m-%d")
        hour_ist = dt_ist.hour
        if hour_ist < 14:
            return date_ist, "morning"
        return date_ist, "evening"
    except Exception:
        return None, None


def get_edition_label(slot: str) -> str:
    return "Morning Edition" if slot == "morning" else "Evening Edition"


# ===== ADMIN ENDPOINTS =====

@router.post("/admin/epaper/include")
async def include_in_epaper(payload: dict):
    article_ids = payload.get("article_ids", [])
    include = payload.get("include", True)
    if not article_ids:
        raise HTTPException(400, "article_ids required")
    result = await db.news.update_many({"id": {"$in": article_ids}}, {"$set": {"epaper_featured": include}})
    return {"updated": result.modified_count}


@router.get("/admin/epaper/featured")
async def get_epaper_featured():
    articles = await db.news.find(
        {"epaper_featured": True},
        {"_id": 0, "id": 1, "title": 1, "category": 1, "published_at": 1, "image": 1}
    ).sort("published_at", -1).to_list(50)
    return {"articles": articles}


@router.post("/admin/epaper/expand-summaries")
async def trigger_expand_summaries():
    """Trigger background expansion of short article summaries."""
    import asyncio
    short = await db.news.find(
        {"is_active": True, "$expr": {"$lt": [{"$strLenCP": {"$ifNull": ["$summary", ""]}}, 120]}},
        {"_id": 0, "id": 1, "title": 1, "summary": 1, "category": 1}
    ).to_list(200)
    count = len(short)
    if count == 0:
        return {"message": "No short summaries found", "count": 0}

    async def expand_batch():
        expanded = 0
        for a in short:
            try:
                result = await expand_summary_for_epaper(a.get("title", ""), a.get("summary", ""), a.get("category", ""))
                if result and len(result) > len(a.get("summary", "")):
                    await db.news.update_one({"id": a["id"]}, {"$set": {"summary": result}})
                    expanded += 1
            except Exception:
                pass
        logger.info(f"Summary expansion done: {expanded}/{count} expanded")

    asyncio.create_task(expand_batch())
    return {"message": f"Expanding {count} short summaries in background", "count": count}


# ===== EDITIONS LIST =====

import time as _time

_editions_cache = {"data": None, "ts": 0}


@router.get("/epaper/editions")
async def get_epaper_editions():
    """Get available editions grouped by date and slot (morning/evening)."""
    if _editions_cache["data"] and (_time.time() - _editions_cache["ts"]) < 120:
        return _editions_cache["data"]

    cutoff = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    articles = await db.news.find(
        {"is_active": True, "created_at": {"$gte": cutoff}},
        {"_id": 0, "created_at": 1}
    ).to_list(15000)

    editions = {}
    for a in articles:
        created = a.get("created_at", "")
        if not created or len(created) < 16:
            continue
        date_ist, slot = classify_article_slot(created)
        if not date_ist:
            continue
        key = f"{date_ist}_{slot}"
        if key not in editions:
            editions[key] = {"date": date_ist, "slot": slot, "article_count": 0}
        editions[key]["article_count"] += 1

    result = sorted(
        editions.values(),
        key=lambda x: (x["date"], 0 if x["slot"] == "evening" else 1),
        reverse=True,
    )
    response = {"editions": result[:120]}
    _editions_cache["data"] = response
    _editions_cache["ts"] = _time.time()
    return response


# ===== EDITION CONTENT =====

@router.get("/epaper/{date}")
async def get_epaper_edition(
    date: str,
    lang: str = Query("en"),  # back-compat: ignored, always English
    slot: str = Query("", regex="^(morning|evening|)$"),
):
    """Get ePaper edition content. English only."""
    if slot:
        start, end = get_slot_utc_range(date, slot)
        query = {"is_active": True, "created_at": {"$gte": start, "$lte": end}}
    else:
        start = f"{date}T00:00:00"
        end = f"{date}T23:59:59"
        query = {"is_active": True, "published_at": {"$gte": start, "$lte": end}}

    all_articles = await db.news.find(query, {"_id": 0}).sort([
        ("epaper_featured", -1), ("is_pinned", -1), ("published_at", -1)
    ]).to_list(300)

    existing_ids = [a["id"] for a in all_articles]
    featured = await db.news.find(
        {"epaper_featured": True, "is_active": True, "id": {"$nin": existing_ids}},
        {"_id": 0},
    ).sort("published_at", -1).to_list(20)
    all_articles = featured + all_articles

    # English-only filter: drop empties
    all_articles = [a for a in all_articles if a.get("title", "") and a.get("summary", "")]

    effective_slot = slot or "evening"
    if not all_articles:
        return {
            "date": date, "slot": effective_slot, "lang": "en",
            "edition_title": f"Mint Street - {get_edition_label(effective_slot)}",
            "pages": [], "total_articles": 0,
        }

    # Prioritize funding/ipo/policy (high-signal sections) then everything else
    priority_cats = {"funding", "ipo", "policy"}
    priority = [a for a in all_articles if a.get("category") in priority_cats]
    others = [a for a in all_articles if a.get("category") not in priority_cats]
    priority.sort(key=lambda a: len(a.get("summary", "")), reverse=True)
    others.sort(key=lambda a: len(a.get("summary", "")), reverse=True)
    prioritized = priority + others

    def fmt_article(a):
        return {
            "id": a.get("id"),
            "title": a.get("title", ""),
            "summary": a.get("summary", ""),
            "image": a.get("image", "") if is_good_image(a.get("image", "")) else "",
            "category": a.get("category", ""),
            "category_label": a.get("category_label", ""),
            "published_at": a.get("published_at", ""),
            "_db_id": a.get("id"),
        }

    SUMMARY_REQS = {
        0: (800, 1400), 1: (700, 1200),
        2: (550, 900), 3: (550, 900), 4: (550, 900),
        5: (450, 750), 6: (450, 750), 7: (450, 750),
    }
    DEFAULT_REQ = (350, 600)
    TITLE_MAX = 80

    MAX_PER_PAGE = 12
    selected = prioritized[:MAX_PER_PAGE * 2]
    if len(selected) <= MAX_PER_PAGE:
        page_chunks = [selected]
    else:
        page_chunks = [selected[:MAX_PER_PAGE], selected[MAX_PER_PAGE:]]

    pages = []
    for i, chunk in enumerate(page_chunks):
        page_title = "Front Page" if i == 0 else "Latest News"
        key = "front" if i == 0 else "latest"
        formatted = [fmt_article(a) for a in chunk]

        for idx, art in enumerate(formatted):
            min_chars, max_chars = SUMMARY_REQS.get(idx, DEFAULT_REQ)
            db_article = next((a for a in chunk if a.get("id") == art["_db_id"]), None)
            if len(art["summary"]) < min_chars and db_article:
                cached_expanded = db_article.get("epaper_summary_en")
                if cached_expanded and len(cached_expanded) > len(art["summary"]):
                    art["summary"] = cached_expanded
            art["summary"] = trim_to_complete_sentences(art["summary"], max_chars, min_chars)
            if len(art["title"]) > TITLE_MAX and db_article:
                cached = db_article.get("epaper_title_en")
                if cached and len(cached) <= TITLE_MAX + 10:
                    art["title"] = cached
                else:
                    art["title"] = art["title"][:TITLE_MAX]
            art.pop("_db_id", None)

        pages.append({"key": key, "title": page_title, "articles": formatted})

    return {
        "date": date, "slot": effective_slot, "lang": "en",
        "edition_title": f"Mint Street - {get_edition_label(effective_slot)}",
        "pages": pages, "total_articles": len(selected),
    }


# ===== PDF DOWNLOAD =====

@router.get("/epaper/{date}/pdf")
async def get_epaper_pdf(
    date: str,
    lang: str = Query("en"),  # back-compat: ignored, always English
    slot: str = Query("", regex="^(morning|evening|)$"),
):
    from weasyprint import HTML
    if slot:
        start, end = get_slot_utc_range(date, slot)
        query = {"is_active": True, "created_at": {"$gte": start, "$lte": end}}
    else:
        start = f"{date}T00:00:00"
        end = f"{date}T23:59:59"
        query = {"is_active": True, "published_at": {"$gte": start, "$lte": end}}

    all_articles = await db.news.find(query, {"_id": 0}).sort([
        ("is_pinned", -1), ("published_at", -1)
    ]).to_list(100)
    all_articles = [a for a in all_articles if a.get("title", "")]

    if not all_articles:
        raise HTTPException(status_code=404, detail="No articles found for this edition")

    from html import escape as _esc
    hF = "'Fraunces', Georgia, serif"
    pages_data = []
    used_ids = set()
    for page_def in EPAPER_PAGES:
        if page_def["categories"]:
            page_articles = [a for a in all_articles if a.get("category") in page_def["categories"] and a["id"] not in used_ids]
        else:
            page_articles = [a for a in all_articles if a["id"] not in used_ids]
        page_articles = page_articles[:page_def["limit"]]
        for a in page_articles:
            used_ids.add(a["id"])
        if not page_articles:
            continue
        page_title = page_def["title_en"]
        sorted_arts = sorted(page_articles, key=lambda x: len(x.get("summary", "")), reverse=True)
        hero = sorted_arts[0] if sorted_arts else None
        sub = sorted_arts[1] if len(sorted_arts) > 1 else None
        mid = sorted_arts[2:5]
        bottom = sorted_arts[5:8]
        tail = sorted_arts[8:]

        def _txt(a, max_len=0):
            t = a.get("title", "")
            s = a.get("summary", "")
            if max_len and len(s) > max_len:
                s = s[:max_len].rsplit(".", 1)[0] + "." if "." in s[:max_len] else s[:max_len]
            img = a.get("image", "") if is_good_image(a.get("image", "")) else ""
            return _esc(t), _esc(s), img

        body = ""
        if hero:
            ht, hs, hi = _txt(hero, 900)
            h_img = f'<img src="{hi}" style="width:100%;height:220px;object-fit:cover;display:block">' if hi else ""
            hero_block = f'{h_img}<h2 style="font-size:32px;font-weight:900;line-height:1.08;font-family:{hF};color:#111;margin:8px 0 6px">{ht}</h2><p style="font-size:13px;line-height:1.65;color:#333;text-align:justify">{hs}</p>'
            sub_block = ""
            if sub:
                st, ss, si = _txt(sub, 700)
                s_img = f'<img src="{si}" style="width:100%;height:140px;object-fit:cover;display:block;margin-bottom:6px">' if si else ""
                tsz = "22px" if si else "26px"
                ssz = "12px" if si else "13px"
                sub_block = f'{s_img}<h3 style="font-size:{tsz};font-weight:900;line-height:1.1;font-family:{hF};color:#111;margin-bottom:5px">{st}</h3><p style="font-size:{ssz};line-height:1.65;color:#444;text-align:justify">{ss}</p>'
            body += f'<div style="display:flex;gap:0;border-bottom:2px solid #1a1a1a;margin-bottom:8px"><div style="flex:1.5;padding:0 14px 10px 0;border-right:1px solid #ccc">{hero_block}</div><div style="flex:1;padding:0 0 10px 14px">{sub_block}</div></div>'

        if mid:
            mc = ""
            for i, a in enumerate(mid):
                mt, ms, mi_img = _txt(a, 500)
                m_img = f'<img src="{mi_img}" style="width:100%;height:100px;object-fit:cover;display:block;margin-bottom:6px">' if mi_img else ""
                br = "border-right:1px solid #ccc;" if i < len(mid) - 1 else ""
                mc += f'<div style="flex:1;padding:8px 12px;{br}">{m_img}<h4 style="font-size:16px;font-weight:800;line-height:1.15;font-family:{hF};color:#1a1a1a;margin-bottom:4px">{mt}</h4><p style="font-size:11px;line-height:1.55;color:#444;text-align:justify">{ms}</p></div>'
            body += f'<div style="display:flex;gap:0;border-bottom:2px solid #1a1a1a;margin-bottom:8px">{mc}</div>'

        if bottom:
            bc = ""
            for i, a in enumerate(bottom):
                bt, bs, bi = _txt(a, 350)
                br = "border-right:1px solid #ccc;" if i < len(bottom) - 1 else ""
                b_img = f'<img src="{bi}" style="float:left;width:40%;height:70px;object-fit:cover;margin-right:8px;margin-bottom:4px">' if bi and i == 0 else ""
                bc += f'<div style="flex:1;padding:6px 10px;{br}">{b_img}<h5 style="font-size:14px;font-weight:700;line-height:1.15;font-family:{hF};color:#1a1a1a;margin-bottom:3px">{bt}</h5><p style="font-size:10.5px;line-height:1.5;color:#555;text-align:justify">{bs}</p><div style="clear:both"></div></div>'
            body += f'<div style="display:flex;gap:0;border-bottom:1px solid #ccc;margin-bottom:8px">{bc}</div>'

        if tail:
            ti = ""
            for a in tail:
                tt, ts, _ = _txt(a, 250)
                ti += f'<div style="break-inside:avoid;margin-bottom:8px;padding-bottom:6px;border-bottom:0.5px solid #e0e0e0"><h6 style="font-size:13px;font-weight:700;line-height:1.15;font-family:{hF};color:#1a1a1a;margin-bottom:2px">{tt}</h6><p style="font-size:10px;line-height:1.5;color:#555;text-align:justify">{ts}</p></div>'
            cc = min(4, max(2, len(tail)))
            body += f'<div style="column-count:{cc};column-gap:14px;column-rule:1px solid #ddd">{ti}</div>'

        pages_data.append({"title": page_title, "body": body})

    total_pages = len(pages_data)
    edition_label = get_edition_label(slot or "evening")

    def _cmyk_footer(pn, tp):
        dl = " ".join(f'<span style="color:{c};font-size:8px">●</span>' for c in ["#00bcd4", "#e91e63", "#ffeb3b", "#212121"])
        dr = " ".join(f'<span style="color:{c};font-size:8px">●</span>' for c in ["#212121", "#ffeb3b", "#e91e63", "#00bcd4"])
        return f'<div style="margin-top:10px;padding-top:6px;border-top:2px solid #1a1a1a;display:flex;justify-content:space-between;align-items:center"><div>{dl}</div><div style="font-size:7px;color:#999">mintstreet.in • Page {pn}/{tp} • {date}</div><div>{dr}</div></div>'

    pages_html = []
    tagline = "Where new money meets new ideas"
    for idx, pg in enumerate(pages_data):
        pn = idx + 1
        if pn == 1:
            hdr = f'''<div style="margin-bottom:6px">
<div style="text-align:center;padding:8px 0 4px;border-bottom:5px double #F26B1F">
<div style="font-size:48px;font-weight:900;letter-spacing:6px;font-family:'Fraunces',Georgia,serif;color:#F26B1F;line-height:1;text-transform:uppercase">MINT STREET</div>
<div style="font-size:8px;color:#888;letter-spacing:3px;text-transform:uppercase;margin-top:3px">{tagline}</div>
</div>
<div style="display:flex;justify-content:space-between;font-size:9px;color:#555;padding:4px 0;border-bottom:2px solid #1a1a1a">
<span style="font-weight:600">{date}</span>
<span style="letter-spacing:2px;text-transform:uppercase;font-size:8px;color:#F26B1F;font-weight:700">{edition_label}</span>
<span>mintstreet.in</span>
</div></div>'''
        else:
            ed_tag = "Morning" if (slot or "evening") == "morning" else "Evening"
            hdr = f'<div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:3px solid #1a1a1a;padding-bottom:4px;margin-bottom:8px"><span style="font-size:13px;font-weight:900;letter-spacing:3px;text-transform:uppercase;color:#F26B1F">MINT STREET</span><span style="font-size:22px;font-weight:900;font-family:{hF};color:#111">{pg["title"]}</span><span style="font-size:8px;color:#888">{date} | {ed_tag} | Pg {pn}</span></div>'
        pb = "page-break-after:always;" if pn < total_pages else ""
        pages_html.append(f'<div style="{pb}padding:14px 20px 10px;display:flex;flex-direction:column;min-height:100%">{hdr}{pg["body"]}{_cmyk_footer(pn, total_pages)}</div>')

    html_content = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=PT+Serif:wght@400;700&display=swap');
@page {{ size: A3 portrait; margin: 12mm; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'PT Serif', Georgia, serif; color: #1a1a1a; font-size: 11px; line-height: 1.4; background: #fefcf7; }}
img {{ border: 0; }}
</style></head><body>
{"".join(pages_html)}
</body></html>'''

    try:
        pdf_bytes = HTML(string=html_content).write_pdf()
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        try:
            simple_html = f'''<!DOCTYPE html><html><head><meta charset="utf-8">
            <style>body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #F26B1F; text-align: center; }} h2 {{ font-size: 14pt; margin-top: 15px; }}
            p {{ font-size: 10pt; color: #333; line-height: 1.5; }}</style></head><body>
            <h1>MINT STREET</h1><p style="text-align:center">{date} - {edition_label}</p><hr>'''
            for a in all_articles[:20]:
                simple_html += f'<h2>{a.get("title", "")}</h2><p>{a.get("summary", "")[:400]}</p><hr>'
            simple_html += '</body></html>'
            pdf_bytes = HTML(string=simple_html).write_pdf()
        except Exception as e2:
            logger.error(f"Fallback PDF also failed: {e2}")
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e2)}")

    slot_suffix = f"_{slot}" if slot else ""
    return StreamingResponse(
        io.BytesIO(pdf_bytes), media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=mint_street_{date}{slot_suffix}.pdf"},
    )
