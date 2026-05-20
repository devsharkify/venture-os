"""
Bulk translate all news articles to Telugu using Gemini Flash.
Translates titles and summaries, stores in title_te and summary_te fields.
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from emergentintegrations.llm.chat import LlmChat, UserMessage
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("translator")

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]
API_KEY = os.environ['EMERGENT_LLM_KEY']

async def translate_text(text: str, session_id: str) -> str:
    """Translate English text to Telugu using Gemini Flash"""
    if not text or len(text.strip()) < 3:
        return text
    
    chat = LlmChat(
        api_key=API_KEY,
        session_id=session_id,
        system_message="You are a senior Telugu news editor at a popular Telugu news channel. Rewrite the given English news into natural, everyday Telugu — the way a Telugu news anchor or reporter speaks on TV. Use simple spoken Telugu that common people understand easily. Avoid literal word-by-word translation. Use Telugu script. Keep names, places, numbers as-is in English. Output ONLY the Telugu text, nothing else."
    ).with_model("gemini", "gemini-2.5-flash")
    
    msg = UserMessage(text=f"Translate to Telugu:\n{text}")
    response = await chat.send_message(msg)
    return response.strip() if response else text

async def bulk_translate():
    # Count untranslated articles
    untranslated = await db.news.count_documents({
        '$or': [
            {'title_te': ''},
            {'title_te': {'$exists': False}},
            {'title_te': None}
        ]
    })
    total = await db.news.count_documents({})
    logger.info(f"Total articles: {total}, Untranslated: {untranslated}")
    
    translated = 0
    failed = 0
    cursor = db.news.find(
        {'$or': [
            {'title_te': ''},
            {'title_te': {'$exists': False}},
            {'title_te': None}
        ]},
        {'_id': 0, 'id': 1, 'title': 1, 'summary': 1}
    )
    
    async for doc in cursor:
        try:
            sid = f"translate-{doc['id'][:8]}"
            
            # Translate title
            title_te = await translate_text(doc.get('title', ''), f"{sid}-t")
            
            # Translate summary (trim to 500 chars for efficiency)
            summary_text = doc.get('summary', '')[:500]
            summary_te = await translate_text(summary_text, f"{sid}-s")
            
            # Update DB
            await db.news.update_one(
                {'id': doc['id']},
                {'$set': {'title_te': title_te, 'summary_te': summary_te}}
            )
            translated += 1
            
            if translated % 10 == 0:
                logger.info(f"Progress: {translated}/{untranslated} translated, {failed} failed")
            
            # Rate limit
            await asyncio.sleep(0.3)
            
        except Exception as e:
            failed += 1
            logger.error(f"Failed to translate {doc.get('id','')}: {e}")
            await asyncio.sleep(1)
    
    logger.info(f"DONE! Translated: {translated}, Failed: {failed}")
    return translated

if __name__ == "__main__":
    count = asyncio.run(bulk_translate())
    print(f"Total translated: {count}")
