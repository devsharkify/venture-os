"""
Backfill script: Updates all existing articles with:
1. Proper 4-5 line AI-generated summaries (Gemini Flash)
2. SEO metadata (keywords, description, og tags)
Runs in background. Skips articles that already have seo_keywords.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

from motor.motor_asyncio import AsyncIOMotorClient
import httpx
from bs4 import BeautifulSoup
from emergentintegrations.llm.chat import LlmChat, UserMessage
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

async def fetch_article_page(link):
    """Fetch article page and extract full text + SEO tags"""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as http:
            resp = await http.get(link, headers=HEADERS)
            if resp.status_code != 200:
                return None, {}
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Extract full article body
            full_text = ""
            content_div = soup.find('div', class_='entry-content')
            if content_div:
                paragraphs = content_div.find_all('p')
                full_text = ' '.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
            
            # Extract SEO tags
            seo = {"seo_description": "", "seo_keywords": [], "seo_author": "", "og_title": "", "og_description": "", "og_image": "", "article_published_time": ""}
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                seo["seo_description"] = (meta_desc.get('content', '') or '')[:500]
            
            meta_kw = soup.find('meta', attrs={'name': 'keywords'}) or soup.find('meta', attrs={'name': 'news_keywords'})
            if meta_kw:
                raw_kw = meta_kw.get('content', '') or ''
                seo["seo_keywords"] = [k.strip() for k in raw_kw.split(',') if k.strip()][:15]
            
            meta_author = soup.find('meta', attrs={'name': 'author'})
            if meta_author:
                seo["seo_author"] = (meta_author.get('content', '') or '')[:100]
            
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            if og_title:
                seo["og_title"] = (og_title.get('content', '') or '')[:200]
            
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc:
                seo["og_description"] = (og_desc.get('content', '') or '')[:500]
            
            og_img = soup.find('meta', attrs={'property': 'og:image'})
            if og_img:
                seo["og_image"] = og_img.get('content', '') or ''
            
            pub_time = soup.find('meta', attrs={'property': 'article:published_time'})
            if pub_time:
                seo["article_published_time"] = (pub_time.get('content', '') or '')[:50]
            
            return full_text, seo
    except Exception as e:
        logger.warning(f"Failed to fetch {link}: {e}")
        return None, {}

async def generate_summary(full_text):
    """Generate 4-5 line summary using Gemini Flash"""
    if not full_text or not EMERGENT_LLM_KEY:
        return None
    try:
        import uuid
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"backfill-{uuid.uuid4()}",
            system_message="You are a professional news editor. Summarize the given news article into a concise 4-5 line paragraph. Keep it informative, factual, and engaging. Output only the summary, nothing else."
        ).with_model("gemini", "gemini-2.5-flash")
        user_message = UserMessage(text=f"Summarize this news article in 4-5 lines:\n\n{full_text[:3000]}")
        result = await chat.send_message(user_message)
        if result and len(result.strip()) > 50:
            return result.strip()
    except Exception as e:
        logger.warning(f"Summary generation failed: {e}")
    return None

async def main():
    # Find articles without SEO keywords (not yet backfilled)
    query = {
        "link": {"$exists": True, "$ne": ""},
        "$or": [
            {"seo_keywords": {"$exists": False}},
            {"seo_keywords": []},
        ]
    }
    
    total = await db.news.count_documents(query)
    logger.info(f"Found {total} articles to backfill")
    
    cursor = db.news.find(query, {"_id": 0, "id": 1, "link": 1, "title": 1, "summary": 1, "image": 1}).sort("published_at", -1)
    
    updated = 0
    failed = 0
    batch_size = 5  # Process 5 at a time to avoid rate limits
    
    articles = await cursor.to_list(length=total)
    
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        
        for article in batch:
            link = article.get("link", "")
            if not link:
                continue
            
            try:
                full_text, seo = await fetch_article_page(link)
                
                update_data = {}
                
                # Add SEO tags
                if seo.get("seo_keywords"):
                    update_data.update(seo)
                
                # Generate AI summary if we have full text
                if full_text:
                    new_summary = await generate_summary(full_text)
                    if new_summary:
                        update_data["summary"] = new_summary
                elif seo.get("og_description") and (len(article.get("summary", "")) < 100):
                    update_data["summary"] = seo["og_description"]
                
                # Update image if missing
                if not article.get("image") and seo.get("og_image"):
                    update_data["image"] = seo["og_image"]
                
                # Update published_at from actual article time
                if seo.get("article_published_time"):
                    update_data["published_at"] = seo["article_published_time"]
                
                if update_data:
                    await db.news.update_one({"id": article["id"]}, {"$set": update_data})
                    updated += 1
                else:
                    failed += 1
                
            except Exception as e:
                logger.warning(f"Error processing {article['title'][:50]}: {e}")
                failed += 1
            
            # Small delay between articles
            await asyncio.sleep(0.5)
        
        logger.info(f"Progress: {min(i+batch_size, len(articles))}/{len(articles)} | Updated: {updated} | Failed: {failed}")
        # Pause between batches
        await asyncio.sleep(1)
    
    logger.info(f"Backfill complete! Updated: {updated}, Failed: {failed}, Total: {total}")

if __name__ == "__main__":
    asyncio.run(main())
