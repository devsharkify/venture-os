import asyncio, calendar, email.utils, os, uuid
from datetime import datetime, timezone
from pathlib import Path
import feedparser, aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent / ".env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ.get("DB_NAME", "mint_street")
CUTOFF = datetime(2026, 2, 19, tzinfo=timezone.utc)
TARGET = 300
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

CATEGORY_RULES = [
    ("ipo",     ["ipo","initial public offering","public issue","stock listing","ipo filing"]),
    ("funding", ["funding","series a","series b","series c","series d","series e","seed round","pre-seed","angel round","raises","raised","crore in funding","million in funding","capital raise","equity round","backed by","led by","investment round","fundraise","venture debt","debt funding"]),
    ("fintech", ["fintech","payment","neobank","crypto","blockchain","insurtech","wealthtech","lending","nbfc","upi","digital payment","wallet","razorpay","paytm","phonepe","zerodha","groww","cred"]),
    ("vc",      ["venture capital","vc fund","private equity","pe fund","fund launch","corpus","limited partner","vc firm","new fund","sequoia","accel","lightspeed","matrix","blume","kalaari","nexus","elevation","bessemer"]),
    ("policy",  ["sebi","rbi","regulation","regulatory","dpiit","startup india","fdi","ministry","government policy","budget","gst","compliance"]),
    ("tech",    ["saas","artificial intelligence"," ai ","machine learning","deep tech","agritech","edtech","healthtech","proptech","cloud","software platform","automation"]),
    ("startup", ["startup","founder","co-founder","launch","bootstrapped","incubator","accelerator","entrepreneur","d2c"]),
    ("business",["merger","acquisition","takeover","partnership","expansion","revenue","growth","valuation","unicorn"]),
]
SKIP = ["cricket","ipl","football","sports","bollywood","film","movie","actor","actress","entertainment","crime","murder","election","bjp","congress","parliament","weather","army","military","flood","earthquake","accident","temple","church","mosque"]
INDIA_WORDS = ["india","indian","bengaluru","bangalore","mumbai","delhi","hyderabad","pune","chennai","kolkata","inr","crore","lakh","sebi","rbi","dpiit","rupee","flipkart","zomato","swiggy","ola","paytm","byju","meesho","razorpay","groww","zerodha","nykaa","dream11","cred","unacademy","upgrad","freshworks","infosys","tcs","wipro"]
STARTUP_MUST = ["startup","funding","vc","series a","series b","series c","raise","raised","unicorn","fintech","saas","ipo","invest","founder","crore","million","venture","acquisition","valuation","entrepreneur","capital","backed","funded","round"]

FEEDS = [
    {"url": "https://inc42.com/feed/", "source": "Inc42"},
    {"url": "https://yourstory.com/feed", "source": "YourStory"},
    {"url": "https://economictimes.indiatimes.com/small-biz/startups/rssfeeds/5575607.cms", "source": "ET Startups"},
    {"url": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms", "source": "ET Tech"},
    {"url": "https://www.moneycontrol.com/rss/business.xml", "source": "Moneycontrol"},
    {"url": "https://feeds.feedburner.com/ndtvprofit-latest", "source": "NDTV Profit"},
    {"url": "https://www.vccircle.com/feed", "source": "VCCircle"},
    {"url": "https://entrackr.com/feed/", "source": "Entrackr"},
    {"url": "https://www.business-standard.com/rss/companies-101.rss", "source": "Business Standard"},
    {"url": "https://www.business-standard.com/rss/technology-108.rss", "source": "Business Standard Tech"},
]

def detect_cat(title, text):
    c = (title + " " + text[:3000]).lower()
    labels = {"vc":"Venture Capital","ipo":"IPO & Markets","fintech":"Fintech","funding":"Funding","policy":"Policy","tech":"Tech","startup":"Startups","business":"Business"}
    for cat, kws in CATEGORY_RULES:
        if any(k in c for k in kws): return cat, labels[cat]
    return "startup", "Startups"

def is_relevant(title, text=""):
    t = (title + " " + text[:800]).lower()
    if any(k in t for k in SKIP): return False
    return any(k in t for k in STARTUP_MUST)

def is_india(t, tx):
    combined = (t + " " + tx[:3000]).lower()
    return any(k in combined for k in INDIA_WORDS)

def parse_date(e):
    for a in ("published_parsed","updated_parsed"):
        t = getattr(e, a, None)
        if t:
            try: return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc)
            except: pass
    for a in ("published","updated"):
        raw = getattr(e, a, None)
        if raw:
            try: return email.utils.parsedate_to_datetime(raw).astimezone(timezone.utc)
            except: pass
    return None

async def fetch(session, url):
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=25), ssl=False, allow_redirects=True) as r:
            if r.status == 200: return await r.text(errors="replace")
    except: pass
    return None

def extract(html):
    soup = BeautifulSoup(html, "lxml")
    img = None
    for tag in soup.find_all("meta"):
        prop = tag.get("property","") or tag.get("name","")
        if "og:image" in prop or "twitter:image" in prop:
            c = tag.get("content","").strip()
            if c.startswith("http"): img = c; break
    if not img:
        for itag in soup.find_all("img", src=True):
            s = itag.get("src","")
            w = itag.get("width","0")
            try:
                if int(str(w)) >= 200 and s.startswith("http"): img = s; break
            except: pass
    text = ""
    for cls in ["entry-content","artText","article-body","Normal","story-content","article-content","post-content","storyContent","td-post-content","field-items"]:
        tag = soup.find(attrs={"class": cls})
        if tag:
            t = " ".join(p.get_text(strip=True) for p in tag.find_all("p") if len(p.get_text(strip=True)) > 40)
            if len(t) > 200: text = t; break
    if not text:
        art = soup.find("article")
        if art: text = " ".join(p.get_text(strip=True) for p in art.find_all("p") if len(p.get_text(strip=True)) > 40)
    if not text:
        text = " ".join(p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 50)
    return img, text[:3000]

async def get_seen(col):
    seen = set()
    async for d in col.find({}, {"source_url": 1}):
        if d.get("source_url"): seen.add(d["source_url"])
    return seen

async def main():
    print(f"=== Mint Street - All Sources Scraper ===")
    print(f"Target: {TARGET} | Cutoff: {CUTOFF.date()}\n")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    col = db.news
    seen = await get_seen(col)
    print(f"Existing in DB: {len(seen)}\n")
    saved = 0
    sem = asyncio.Semaphore(8)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=10)) as session:
        for feed_cfg in FEEDS:
            if saved >= TARGET: break
            print(f"── {feed_cfg['source']}: {feed_cfg['url'][:55]}...")
            feed = feedparser.parse(feed_cfg["url"])
            entries = feed.entries
            print(f"   {len(entries)} entries")
            src_saved = 0

            for entry in entries:
                if saved >= TARGET: break
                url = getattr(entry, "link", "")
                if not url or url in seen: continue
                title = getattr(entry, "title", "").strip()
                if not title: continue
                if not is_relevant(title): continue
                pub = parse_date(entry)
                if pub and pub < CUTOFF: continue

                async with sem:
                    html = await fetch(session, url)
                if not html: continue
                img, text = extract(html)

                if not img:
                    print(f"   [no-img] {title[:55]}")
                    continue
                if not is_relevant(title, text):
                    print(f"   [irrelevant] {title[:55]}")
                    continue
                if not is_india(title, text):
                    print(f"   [not-india] {title[:55]}")
                    continue

                cat, label = detect_cat(title, text)
                doc = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "summary": text or title,
                    "category": cat,
                    "category_label": label,
                    "image": img,
                    "source": feed_cfg["source"],
                    "source_url": url,
                    "is_pinned": False,
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                    "published_at": pub or datetime.now(timezone.utc),
                    "views": 0,
                    "language": "en"
                }
                try:
                    r = await col.update_one({"source_url": url}, {"$setOnInsert": doc}, upsert=True)
                    if r.upserted_id:
                        saved += 1; src_saved += 1; seen.add(url)
                        print(f"   [{saved:03d}] [{cat:8s}] {title[:62]}")
                        if saved % 25 == 0:
                            print(f"\n   {'='*50}")
                            print(f"   PROGRESS: {saved}/{TARGET} saved")
                            print(f"   {'='*50}\n")
                except Exception as e:
                    print(f"   [err] {e}")
                await asyncio.sleep(0.15)

            print(f"   → {feed_cfg['source']}: {src_saved} saved\n")

    total = await col.count_documents({})
    print(f"\n{'='*55}")
    print(f"✅ DONE - {saved} new articles | {total} total in DB\n")
    print("Category breakdown:")
    async for row in col.aggregate([{"$group":{"_id":"$category","count":{"$sum":1}}},{"$sort":{"count":-1}}]):
        print(f"   {row['_id']:14s}: {row['count']}")
    print("\nSource breakdown:")
    async for row in col.aggregate([{"$group":{"_id":"$source","count":{"$sum":1}}},{"$sort":{"count":-1}}]):
        print(f"   {row['_id']:20s}: {row['count']}")
    client.close()

asyncio.run(main())
