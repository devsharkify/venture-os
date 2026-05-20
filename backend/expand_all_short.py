"""Expand all short summaries (EN < 100 chars, TE < 100 chars) using AI."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import db, logger
from helpers import expand_summary_for_epaper

async def main():
    # English short summaries
    en_articles = await db.news.find(
        {"is_active": True, "$expr": {"$lt": [{"$strLenCP": {"$ifNull": ["$summary", ""]}}, 100]}},
        {"_id": 0, "id": 1, "title": 1, "summary": 1, "category": 1}
    ).to_list(500)
    print(f"Found {len(en_articles)} short English summaries to expand")

    # Telugu short summaries
    te_articles = await db.news.find(
        {"summary_te": {"$exists": True, "$ne": ""}, "$expr": {"$lt": [{"$strLenCP": "$summary_te"}, 100]}},
        {"_id": 0, "id": 1, "title": 1, "title_te": 1, "summary_te": 1, "category": 1}
    ).to_list(500)
    print(f"Found {len(te_articles)} short Telugu summaries to expand")

    en_done, en_fail = 0, 0
    for i, a in enumerate(en_articles):
        title = a.get("title", "")
        summary = a.get("summary", "")
        if not title and not summary:
            continue
        try:
            expanded = await expand_summary_for_epaper(title, summary, a.get("category", ""), "en")
            if expanded and len(expanded) > len(summary):
                await db.news.update_one({"id": a["id"]}, {"$set": {"summary": expanded}})
                en_done += 1
                print(f"  EN [{i+1}/{len(en_articles)}] {title[:50]}... {len(summary)}->{len(expanded)} chars")
            else:
                en_fail += 1
        except Exception as e:
            en_fail += 1
            print(f"  EN [{i+1}] FAIL: {e}")
        if (i + 1) % 10 == 0:
            print(f"  EN progress: {i+1}/{len(en_articles)} ({en_done} expanded, {en_fail} failed)")

    print(f"\nEN Done: {en_done} expanded, {en_fail} failed out of {len(en_articles)}")

    te_done, te_fail = 0, 0
    for i, a in enumerate(te_articles):
        title = a.get("title_te", "") or a.get("title", "")
        summary = a.get("summary_te", "")
        if not title and not summary:
            continue
        try:
            expanded = await expand_summary_for_epaper(title, summary, a.get("category", ""), "te")
            if expanded and len(expanded) > len(summary):
                await db.news.update_one({"id": a["id"]}, {"$set": {"summary_te": expanded}})
                te_done += 1
                print(f"  TE [{i+1}/{len(te_articles)}] {title[:50]}... {len(summary)}->{len(expanded)} chars")
            else:
                te_fail += 1
        except Exception as e:
            te_fail += 1
            print(f"  TE [{i+1}] FAIL: {e}")
        if (i + 1) % 10 == 0:
            print(f"  TE progress: {i+1}/{len(te_articles)} ({te_done} expanded, {te_fail} failed)")

    print(f"\nTE Done: {te_done} expanded, {te_fail} failed out of {len(te_articles)}")
    print(f"\nTOTAL: {en_done + te_done} expanded successfully")

if __name__ == "__main__":
    asyncio.run(main())
