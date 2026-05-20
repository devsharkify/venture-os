"""Pre-expand all short ePaper summaries to fill the cache for instant loading."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import db, logger
from helpers import expand_summary_for_epaper

# New aggressive limits matching epaper.py
SUMMARY_REQS = {
    0: (800, 1400), 1: (700, 1200),
    2: (550, 900), 3: (550, 900), 4: (550, 900),
    5: (450, 750), 6: (450, 750), 7: (450, 750),
}
DEFAULT_REQ = (350, 600)
MIN_THRESHOLD = 450  # Minimum chars needed for any ePaper position

async def expand_one(article, lang):
    """Expand a single article summary."""
    cache_key = f"epaper_summary_{lang}"
    if lang == "te":
        title = article.get("title_te", "") or article.get("title", "")
        summary = article.get("summary_te", "")
    else:
        title = article.get("title", "")
        summary = article.get("summary", "")
    
    # Skip if already cached with enough content
    cached = article.get(cache_key, "")
    if cached and len(cached) >= MIN_THRESHOLD:
        return False
    
    # Skip if raw summary is already long enough
    if len(summary) >= MIN_THRESHOLD:
        return False
    
    try:
        expanded = await expand_summary_for_epaper(title, summary, article.get("category", ""), lang)
        if expanded and len(expanded) > len(summary):
            await db.news.update_one(
                {"id": article["id"]},
                {"$set": {cache_key: expanded}}
            )
            return True
    except Exception as e:
        print(f"  FAIL: {e}")
    return False

async def main():
    # Get recent articles (last 30 days) that might appear in ePaper
    from datetime import datetime, timezone, timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    
    articles = await db.news.find(
        {"is_active": True, "created_at": {"$gte": cutoff}},
        {"_id": 0, "id": 1, "title": 1, "title_te": 1, "summary": 1, "summary_te": 1, 
         "category": 1, "epaper_summary_en": 1, "epaper_summary_te": 1}
    ).to_list(5000)
    
    print(f"Found {len(articles)} recent articles")
    
    # Process Telugu
    te_need = [a for a in articles 
               if a.get("title_te") and any(0x0C00 <= ord(c) <= 0x0C7F for c in a.get("title_te", ""))
               and len(a.get("epaper_summary_te", "")) < MIN_THRESHOLD
               and len(a.get("summary_te", "")) < MIN_THRESHOLD]
    print(f"Telugu articles needing expansion: {len(te_need)}")
    
    # Process in batches of 5 concurrent
    te_done = 0
    BATCH = 5
    for i in range(0, len(te_need), BATCH):
        batch = te_need[i:i+BATCH]
        results = await asyncio.gather(*[expand_one(a, "te") for a in batch], return_exceptions=True)
        for j, r in enumerate(results):
            if r is True:
                te_done += 1
                t = batch[j].get("title_te", "")[:40]
                print(f"  TE [{i+j+1}/{len(te_need)}] expanded: {t}")
            elif isinstance(r, Exception):
                print(f"  TE [{i+j+1}] error: {r}")
        if (i + BATCH) % 20 == 0:
            print(f"  Progress: {i+BATCH}/{len(te_need)} ({te_done} expanded)")
    
    print(f"\nTelugu: {te_done}/{len(te_need)} expanded")
    
    # Process English
    en_need = [a for a in articles
               if a.get("title", "")
               and len(a.get("epaper_summary_en", "")) < MIN_THRESHOLD
               and len(a.get("summary", "")) < MIN_THRESHOLD]
    print(f"English articles needing expansion: {len(en_need)}")
    
    en_done = 0
    for i in range(0, len(en_need), BATCH):
        batch = en_need[i:i+BATCH]
        results = await asyncio.gather(*[expand_one(a, "en") for a in batch], return_exceptions=True)
        for j, r in enumerate(results):
            if r is True:
                en_done += 1
                t = batch[j].get("title", "")[:40]
                print(f"  EN [{i+j+1}/{len(en_need)}] expanded: {t}")
            elif isinstance(r, Exception):
                print(f"  EN [{i+j+1}] error: {r}")
    
    print(f"\nEnglish: {en_done}/{len(en_need)} expanded")
    print(f"TOTAL: {te_done + en_done} articles expanded")

if __name__ == "__main__":
    asyncio.run(main())
