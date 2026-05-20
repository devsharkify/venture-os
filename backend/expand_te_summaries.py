"""Bulk expand short Telugu article summaries using AI."""
import asyncio
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
MIN_CHARS = 200


async def expand(title: str, summary: str, category: str) -> str:
    if not title or not EMERGENT_LLM_KEY:
        return summary
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"te-{uuid.uuid4()}",
            system_message="""You are a professional Telugu newspaper editor. Given a headline and short summary in Telugu, write an expanded summary (200-300 words) that:
- Keeps all original facts intact
- Adds relevant context, background, and implications
- Uses formal Telugu newspaper tone
- Uses short to medium sentences (40-80 words each)
- Ends with a complete sentence ending in a period
- Write ONLY in Telugu. Do NOT use English.
Output ONLY the expanded Telugu text, nothing else."""
        ).with_model("gemini", "gemini-2.5-flash")
        result = await chat.send_message(
            UserMessage(text=f"శీర్షిక: {title}\nవర్గం: {category}\nసారాంశం: {summary}\n\n200-300 పదాలలో విస్తరించండి:")
        )
        if result and len(result.strip()) > len(summary):
            return result.strip()
    except Exception as e:
        print(f"  Error: {e}")
    return summary


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    short = await db.news.find(
        {"summary_te": {"$exists": True, "$ne": ""},
         "$expr": {"$lt": [{"$strLenCP": "$summary_te"}, MIN_CHARS]}},
        {"_id": 0, "id": 1, "title_te": 1, "summary_te": 1, "category": 1}
    ).to_list(500)

    print(f"Found {len(short)} Telugu articles with summary_te < {MIN_CHARS} chars")
    ok, fail = 0, 0

    for i, a in enumerate(short):
        title = a.get("title_te", "")
        summary = a.get("summary_te", "")
        if not title:
            fail += 1
            continue

        expanded = await expand(title, summary, a.get("category", "national"))
        if expanded and len(expanded) > len(summary) and len(expanded) >= MIN_CHARS:
            await db.news.update_one({"id": a["id"]}, {"$set": {"summary_te": expanded}})
            ok += 1
        else:
            fail += 1

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(short)} (ok={ok}, fail={fail})")
        await asyncio.sleep(0.2)

    print(f"\nDone: {ok} expanded, {fail} failed")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
