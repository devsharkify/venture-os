"""Bulk expand short article summaries to 200+ words using AI."""
import asyncio
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
MIN_SUMMARY_CHARS = 200


async def expand_summary(title: str, summary: str, category: str) -> str:
    if not title or not EMERGENT_LLM_KEY:
        return summary
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"expand-{uuid.uuid4()}",
            system_message="""You are a professional newspaper editor. Given a headline and short summary, write an expanded news article summary (200-300 words) that:
- Keeps all original facts intact
- Adds relevant context, background, and implications
- Uses formal newspaper tone
- Uses short to medium sentences (40-80 words each)
- Ends with a complete sentence ending in a period
- Write in the same language as the input
Output ONLY the expanded text, nothing else."""
        ).with_model("gemini", "gemini-2.5-flash")
        result = await chat.send_message(
            UserMessage(text=f"Title: {title}\nCategory: {category}\nOriginal: {summary}\n\nExpand to 200-300 words:")
        )
        if result and len(result.strip()) > len(summary):
            return result.strip()
    except Exception as e:
        print(f"  Error: {e}")
    return summary


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    short_articles = await db.news.find(
        {"summary": {"$exists": True, "$ne": ""},
         "$expr": {"$lt": [{"$strLenCP": "$summary"}, MIN_SUMMARY_CHARS]}},
        {"_id": 0, "id": 1, "title": 1, "summary": 1, "category": 1}
    ).to_list(500)

    print(f"Found {len(short_articles)} articles with summary < {MIN_SUMMARY_CHARS} chars")
    ok, fail = 0, 0

    for i, a in enumerate(short_articles):
        title = a.get("title", "")
        summary = a.get("summary", "")
        if not title:
            fail += 1
            continue

        expanded = await expand_summary(title, summary, a.get("category", "national"))
        if expanded and len(expanded) > len(summary) and len(expanded) >= MIN_SUMMARY_CHARS:
            update = {"summary": expanded}
            await db.news.update_one({"id": a["id"]}, {"$set": update})
            ok += 1
        else:
            fail += 1

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(short_articles)} (ok={ok}, fail={fail})")
        await asyncio.sleep(0.2)

    print(f"\nDone: {ok} expanded, {fail} failed")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
