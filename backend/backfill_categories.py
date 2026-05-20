"""
Backfill script: Re-categorizes all existing articles using keyword-based logic.
Uses keyword matching (no LLM) to be fast and free.
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

from motor.motor_asyncio import AsyncIOMotorClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

CATEGORIES = {
    "funding": {"en": "Funding"},
    "startups": {"en": "Startups"},
    "vc": {"en": "Venture Capital"},
    "ipo": {"en": "IPO & Markets"},
    "tech": {"en": "Tech"},
    "fintech": {"en": "Fintech"},
    "saas": {"en": "SaaS"},
    "deeptech": {"en": "Deep Tech"},
    "d2c": {"en": "D2C"},
    "climate": {"en": "Climate"},
    "policy": {"en": "Policy"},
    "business": {"en": "Business"},
}

def classify(title, summary):
    text = (title + " " + summary).lower()

    hyd_keywords = ["hyderabad", "secunderabad", "cyberabad", "rachakonda", "ghmc", "shamshabad", "hitec city", "hi-tech city", "charminar", "hussain sagar", "osmania", "nampally", "banjara hills", "jubilee hills", "kukatpally", "miyapur", "uppal", "lb nagar", "dilsukhnagar", "ameerpet", "begumpet", "mehdipatnam", "malakpet", "old city", "malkajgiri", "kompally", "medchal"]
    if any(kw in text for kw in hyd_keywords):
        return "city"

    ts_keywords = ["telangana", "revanth reddy", "kcr", "trs", "brs", "warangal", "karimnagar", "nizamabad", "khammam", "adilabad", "mahbubnagar", "mahabubnagar", "nalgonda", "siddipet", "medak", "sangareddy", "indiramma", "telangana cm", "ts government", "jagtial", "mancherial", "nirmal", "kamareddy", "rajanna", "sircilla", "peddapalli", "bhadradri", "kothagudem", "suryapet", "jangaon", "vikarabad", "yadadri", "bhongir", "wanaparthy", "narayanpet", "mulugu", "jayashankar"]
    if any(kw in text for kw in ts_keywords):
        return "state"

    ent_keywords = ["bollywood", "tollywood", "movie", "film", "actor", "actress", "ott", "netflix", "amazon prime", "hotstar", "nayanthara", "prabhas", "mahesh babu", "allu arjun", "shah rukh", "salman khan", "celebrity", "bigg boss", "cinema", "box office", "trailer", "director", "kollywood", "south indian cinema", "vignesh shivan", "samantha", "pooja hegde", "jr ntr", "ram charan", "chiranjeevi", "nagarjuna"]
    if any(kw in text for kw in ent_keywords):
        return "entertainment"

    sport_keywords = ["cricket", "ipl", "bcci", "football", "tennis", "olympics", "match score", "player", "team india", "world cup", "batsman", "bowler", "kohli", "rohit sharma", "dhoni", "t20", "wicket", "century scored", "sportsperson", "srh", "sunrisers", "rcb", "csk", "mi ", "tendulkar"]
    if any(kw in text for kw in sport_keywords):
        return "sports"

    tech_keywords = ["technology", " ai ", "artificial intelligence", "startup", "google", "apple", "microsoft", "software", " app ", "gadget", "cyber", "digital", "elon musk", "tesla", "openai", "chatgpt", "smartphone", "iphone", "android", "samsung"]
    if any(kw in text for kw in tech_keywords):
        return "tech"

    health_keywords = ["health", "medical", "hospital", "doctor", "disease", "covid", "vaccine", "treatment", "patient", "surgery", "ayush", "pharma", "medicine", "diabetes", "cancer", "mental health"]
    if any(kw in text for kw in health_keywords):
        return "health"

    biz_keywords = ["sensex", "nifty", "stock market", "rbi ", "economy", " gdp", "inflation", "trade deal", "export", "import", "rupee", "dollar", "investment", "shares", "mutual fund", "banking", "loan", "interest rate"]
    if any(kw in text for kw in biz_keywords):
        return "business"

    intl_keywords = [" us ", " usa", "china", "pakistan", "iran", "israel", "ukraine", "russia", "saudi", "dubai", "uae", " uk ", "europe", "bangladesh", "nepal", "sri lanka", "afghanistan", "syria", "global", "united nations", "nato", "trump", "biden", "gulf", "middle east", "khamenei", "tehran", "gaza", "hamas", "hezbollah"]
    if any(kw in text for kw in intl_keywords):
        return "international"

    return "national"


async def main():
    total = await db.news.count_documents({})
    logger.info(f"Total articles: {total}")

    cursor = db.news.find({}, {"_id": 0, "id": 1, "title": 1, "summary": 1, "category": 1})
    
    changed = 0
    unchanged = 0

    async for article in cursor:
        old_cat = article.get("category", "national")
        new_cat = classify(article["title"], article.get("summary", ""))
        
        if old_cat != new_cat:
            await db.news.update_one(
                {"id": article["id"]},
                {"$set": {
                    "category": new_cat,
                    "category_label": CATEGORIES.get(new_cat, {}).get("en", new_cat),
                }}
            )
            changed += 1
        else:
            unchanged += 1
        
        if (changed + unchanged) % 500 == 0:
            logger.info(f"Progress: {changed + unchanged}/{total} | Changed: {changed}")

    logger.info(f"Done! Changed: {changed}, Unchanged: {unchanged}, Total: {total}")

if __name__ == "__main__":
    asyncio.run(main())
