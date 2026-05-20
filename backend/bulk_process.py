"""
Bulk Telugu Translation + Summary Backfill Script
Run: cd /app/backend && python3 bulk_process.py
Processes articles in batches:
1. Translates titles and summaries to Telugu
2. Generates AI summaries for articles missing them
"""
import asyncio
import os
import sys
import uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.chat import LlmChat, UserMessage

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

# Get Emergent LLM key from environment
EMERGENT_LLM_KEY = None
for key in ["EMERGENT_LLM_KEY", "EMERGENT_API_KEY"]:
    val = os.environ.get(key)
    if val:
        EMERGENT_LLM_KEY = val
        break

# Fallback: read from .env
if not EMERGENT_LLM_KEY:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if "EMERGENT" in line and "=" in line:
                    k, v = line.strip().split("=", 1)
                    if v and "KEY" in k:
                        EMERGENT_LLM_KEY = v.strip().strip('"')
                        break


async def translate_text(text: str) -> str:
    """Translate text to Telugu using Gemini (faster + cheaper than GPT)."""
    if not text or not EMERGENT_LLM_KEY:
        return ""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"tr-{uuid.uuid4()}",
            system_message="Translate the given English text to Telugu. Output only the Telugu translation."
        ).with_model("gemini", "gemini-2.5-flash")
        result = await chat.send_message(UserMessage(text=text[:2000]))
        return result.strip() if result else ""
    except Exception as e:
        print(f"    Translation error: {e}")
        return ""


async def generate_summary(title: str, category: str) -> str:
    """Generate a summary from just the title when full text isn't available."""
    if not title or not EMERGENT_LLM_KEY:
        return ""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"sum-{uuid.uuid4()}",
            system_message="You are a newspaper editor. Given a news headline and category, write a detailed 150-200 word summary that provides context, background, and analysis. Use formal newspaper tone. Output only the summary."
        ).with_model("gemini", "gemini-2.5-flash")
        result = await chat.send_message(UserMessage(text=f"Headline: {title}\nCategory: {category}\n\nWrite a 150-200 word newspaper summary:"))
        return result.strip() if result else ""
    except Exception as e:
        print(f"    Summary error: {e}")
        return ""


async def main():
    if not EMERGENT_LLM_KEY:
        print("ERROR: No Emergent LLM key found!")
        return

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    coll = db.news

    total = await coll.count_documents({})
    print(f"Total articles: {total}")

    # --- TASK 1: Generate missing summaries ---
    no_summary = await coll.find(
        {"$or": [{"summary": {"$in": [None, ""]}}, {"summary": {"$exists": False}}]},
        {"_id": 0, "id": 1, "title": 1, "title_te": 1, "category": 1}
    ).to_list(500)
    
    print(f"\n=== TASK 1: Generate summaries for {len(no_summary)} articles ===")
    sum_ok, sum_fail = 0, 0
    for i, a in enumerate(no_summary):
        title = a.get("title", "") or a.get("title_te", "")
        summary = await generate_summary(title, a.get("category", "national"))
        if summary and len(summary) > 50:
            await coll.update_one({"id": a["id"]}, {"$set": {"summary": summary}})
            sum_ok += 1
        else:
            sum_fail += 1
        if (i + 1) % 10 == 0:
            print(f"  Summaries: {i+1}/{len(no_summary)} (ok={sum_ok}, fail={sum_fail})")
        await asyncio.sleep(0.3)
    print(f"  Done: {sum_ok} generated, {sum_fail} failed")

    # --- TASK 2: Telugu translation ---
    no_te = await coll.find(
        {"$or": [{"title_te": {"$in": [None, ""]}}, {"title_te": {"$exists": False}}]},
        {"_id": 0, "id": 1, "title": 1, "summary": 1}
    ).sort("created_at", -1).to_list(5000)

    print(f"\n=== TASK 2: Translate {len(no_te)} articles to Telugu ===")
    te_ok, te_fail = 0, 0
    for i, a in enumerate(no_te):
        title = a.get("title", "")
        summary = a.get("summary", "")
        
        update = {}
        
        # Translate title
        title_te = await translate_text(title)
        if title_te:
            update["title_te"] = title_te
        
        # Translate summary (only if it exists)
        if summary and len(summary) > 30:
            summary_te = await translate_text(summary[:1500])
            if summary_te:
                update["summary_te"] = summary_te
        
        if update:
            await coll.update_one({"id": a["id"]}, {"$set": update})
            te_ok += 1
        else:
            te_fail += 1
        
        if (i + 1) % 20 == 0:
            print(f"  Translations: {i+1}/{len(no_te)} (ok={te_ok}, fail={te_fail})")
        await asyncio.sleep(0.3)
    
    print(f"  Done: {te_ok} translated, {te_fail} failed")

    # --- Summary ---
    remaining_te = await coll.count_documents({"$or": [{"title_te": {"$in": [None, ""]}}, {"title_te": {"$exists": False}}]})
    remaining_sum = await coll.count_documents({"$or": [{"summary": {"$in": [None, ""]}}, {"summary": {"$exists": False}}]})
    print(f"\n=== FINAL STATUS ===")
    print(f"  Still missing Telugu: {remaining_te}")
    print(f"  Still missing summary: {remaining_sum}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
