import uuid
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from fastapi import HTTPException
from emergentintegrations.llm.chat import LlmChat, UserMessage
from database import db, logger, EMERGENT_LLM_KEY, CATEGORIES


def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def prepare_for_mongo(data: dict) -> dict:
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result

def parse_from_mongo(data: dict) -> dict:
    """Normalize datetime objects from Mongo to ISO strings.
    Pydantic v2 auto-coerces ISO strings back to datetime for datetime-typed fields,
    so this works for both str-typed and datetime-typed model fields."""
    datetime_fields = ['published_at', 'created_at', 'updated_at', 'timestamp', 'approved_at', 'reviewed_at', 'submitted_at']
    for field in datetime_fields:
        if field in data and isinstance(data[field], datetime):
            data[field] = data[field].isoformat()
    return data

async def scrape_url(url: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            title = ""
            if soup.title:
                title = soup.title.string or ""
            if not title:
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text(strip=True)
            summary = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                summary = meta_desc.get('content', '')
            if not summary:
                og_desc = soup.find('meta', attrs={'property': 'og:description'})
                if og_desc:
                    summary = og_desc.get('content', '')
            if not summary:
                p = soup.find('p')
                if p:
                    summary = p.get_text(strip=True)[:500]
            image = ""
            og_image = soup.find('meta', attrs={'property': 'og:image'})
            if og_image:
                image = og_image.get('content', '')
            return {
                'title': title[:200] if title else "Untitled",
                'summary': summary[:1000] if summary else "No summary available",
                'image': image,
                'source': url
            }
    except Exception as e:
        logger.error(f"Error scraping URL: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")

async def rephrase_with_ai(text: str, is_title: bool = False) -> str:
    if not EMERGENT_LLM_KEY:
        return text
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"rephrase-{uuid.uuid4()}",
            system_message="You are a professional news editor. Rephrase the given text to be unique while maintaining the same meaning and facts. Keep it concise and journalistic. IMPORTANT: The summary MUST be at least 4 paragraphs/lines. Each paragraph should cover a distinct point or angle of the story."
        ).with_model("openai", "gpt-4o-mini")
        prompt = f"Rephrase this {'headline' if is_title else 'news summary (write at least 4 separate lines/paragraphs)'} to be unique: {text}"
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response.strip()
    except Exception as e:
        logger.error(f"Error rephrasing with AI: {e}")
        return text

async def translate_to_telugu(text: str) -> str:
    if not EMERGENT_LLM_KEY or not text or len(text.strip()) < 3:
        return ""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"translate-{uuid.uuid4()}",
            system_message="You are a professional translator. Translate the given English text to Telugu. Provide only the Telugu translation, nothing else."
        ).with_model("openai", "gpt-4o-mini")
        user_message = UserMessage(text=f"Translate to Telugu: {text}")
        response = await chat.send_message(user_message)
        return response.strip()
    except Exception as e:
        logger.error(f"Error translating to Telugu: {e}")
        return ""

async def translate_to_english(text: str) -> str:
    if not EMERGENT_LLM_KEY or not text or len(text.strip()) < 3:
        return ""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"translate-en-{uuid.uuid4()}",
            system_message="You are a professional translator. Translate the given Telugu text to English. Provide only the English translation, nothing else."
        ).with_model("openai", "gpt-4o-mini")
        user_message = UserMessage(text=f"Translate to English: {text}")
        response = await chat.send_message(user_message)
        return response.strip()
    except Exception as e:
        logger.error(f"Error translating to English: {e}")
        return ""

async def classify_article_category(title: str, summary: str) -> str:
    if not EMERGENT_LLM_KEY:
        return guess_category_from_content(title, summary)
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"classify-{uuid.uuid4()}",
            system_message="""You are a news article categorizer for a Hyderabad-based news app. Classify the article into exactly ONE category. Reply with ONLY the category key, nothing else.

Rules:
- "local" = News specifically about Dammaiguda area
- "city" = News about Hyderabad city, Secunderabad, or surrounding areas
- "state" = News about Telangana state, state government, Telangana politics
- "national" = News about other Indian states, central government, India-wide topics
- "international" = News about other countries, global events
- "sports" = Sports news
- "entertainment" = Bollywood, Tollywood, OTT, celebrities
- "tech" = Technology, gadgets, apps, AI, startups
- "health" = Health, medical, fitness
- "business" = Business, economy, stock market"""
        ).with_model("gemini", "gemini-2.5-flash")
        user_message = UserMessage(text=f"Title: {title}\nSummary: {summary[:300]}")
        result = await chat.send_message(user_message)
        category = result.strip().lower().replace('"', '').replace("'", "")
        if category in CATEGORIES:
            return category
    except Exception as e:
        logger.warning(f"AI classification failed: {e}")
    return guess_category_from_content(title, summary)

def guess_category_from_content(title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    kw = {
        "city": ["hyderabad", "secunderabad", "cyberabad", "ghmc", "rachakonda", "shamshabad", "hitec city", "old city", "charminar"],
        "state": ["telangana", "revanth reddy", "kcr", "trs", "brs", "warangal", "karimnagar", "nizamabad", "khammam", "nalgonda"],
        "national": ["india", "modi", "parliament", "bjp", "congress", "delhi", "mumbai", "supreme court", "lok sabha"],
        "international": ["us ", "usa", "china", "pakistan", "russia", "ukraine", "israel", "gaza", "trump", "biden", "un "],
        "sports": ["cricket", "ipl", "football", "tennis", "olympic", "match", "player", "team", "kohli", "dhoni"],
        "entertainment": ["movie", "film", "bollywood", "tollywood", "actor", "actress", "ott", "netflix", "song", "album"],
        "tech": ["tech", "ai ", "artificial intelligence", "google", "apple", "microsoft", "startup", "app ", "software"],
        "health": ["health", "hospital", "doctor", "medical", "disease", "covid", "vaccine", "fitness", "mental health"],
        "business": ["business", "market", "stock", "economy", "rbi", "bank", "gdp", "inflation", "trade", "company"],
    }
    scores = {}
    for cat, keywords in kw.items():
        scores[cat] = sum(1 for k in keywords if k in text)
    best = max(scores, key=scores.get) if scores else "national"
    return best if scores[best] > 0 else "national"

SIASAT_CATEGORY_MAP = {
    "hyderabad": "city", "telangana": "state", "andhra-pradesh": "state",
    "bangalore": "city", "south-india": "state", "india": "national",
    "national": "national", "middle-east": "international", "world": "international",
    "international": "international", "technology": "tech", "technology-2": "tech",
    "entertainment": "entertainment", "sports": "sports", "business": "business", "health": "health",
}

def guess_category_from_url(url: str) -> str:
    url_lower = url.lower()
    for key, cat in SIASAT_CATEGORY_MAP.items():
        if f"/{key}/" in url_lower or f"/news/{key}" in url_lower:
            return cat
    return ""

async def extract_seo_and_text(url: str, headers: dict) -> tuple:
    """Extract SEO metadata and full article text from a URL. Returns (seo_dict, full_text)."""
    seo = {"seo_description": "", "seo_keywords": [], "seo_author": "", "og_title": "", "og_description": "", "og_image": "", "article_published_time": ""}
    full_text = ""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as http:
            resp = await http.get(url, headers=headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Full article body
                for selector in ['div.entry-content', 'div.article-body', 'article', 'div.story-content', 'div.content-area']:
                    content_div = soup.select_one(selector)
                    if content_div:
                        paragraphs = content_div.find_all('p')
                        full_text = ' '.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
                        if full_text:
                            break
                # SEO meta
                for tag, key in [
                    (('meta', {'name': 'description'}), 'seo_description'),
                    (('meta', {'name': 'author'}), 'seo_author'),
                    (('meta', {'property': 'og:title'}), 'og_title'),
                    (('meta', {'property': 'og:description'}), 'og_description'),
                    (('meta', {'property': 'og:image'}), 'og_image'),
                    (('meta', {'property': 'article:published_time'}), 'article_published_time'),
                ]:
                    el = soup.find(tag[0], attrs=tag[1])
                    if el:
                        seo[key] = (el.get('content', '') or '')[:500]
                # Keywords
                meta_kw = soup.find('meta', attrs={'name': 'keywords'}) or soup.find('meta', attrs={'name': 'news_keywords'})
                if meta_kw:
                    seo["seo_keywords"] = [k.strip() for k in (meta_kw.get('content', '') or '').split(',') if k.strip()][:15]
                # Image from lazy-loaded or regular
                if not seo["og_image"]:
                    img = soup.find('img', class_=lambda x: x and ('featured' in str(x) or 'hero' in str(x) or 'main' in str(x)))
                    if img:
                        seo["og_image"] = img.get('data-src') or img.get('data-lazy-src') or img.get('src') or ""
    except Exception:
        pass
    return seo, full_text

async def generate_ai_summary(full_text: str, link: str) -> str:
    """Generate a detailed 8-10 line summary using Gemini Flash for newspaper-quality content."""
    if not full_text or not EMERGENT_LLM_KEY:
        return ""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"summarize-{uuid.uuid4()}",
            system_message=(
                "You are a professional newspaper editor. Write a detailed summary of the given news article in EXACTLY 4 to 6 short paragraphs (each separated by a blank line). "
                "Each paragraph should be 1-2 sentences with key facts, context, or background. Use formal newspaper tone. "
                "Total length 150-250 words. Do NOT use bullet points. Output ONLY the summary, with paragraphs separated by '\\n\\n'."
            )
        ).with_model("gemini", "gemini-2.5-flash")
        user_message = UserMessage(text=f"Write a 4-6 paragraph newspaper summary (paragraphs separated by blank lines):\n\n{full_text[:3000]}")
        result = await chat.send_message(user_message)
        if result and len(result.strip()) > 50:
            return ensure_min_paragraphs(result.strip(), min_paragraphs=4)
    except Exception as e:
        logger.warning(f"Summary generation failed for {link}: {e}")
    return ""


def ensure_min_paragraphs(text: str, min_paragraphs: int = 4) -> str:
    """Format `text` as at least `min_paragraphs` paragraphs (separated by blank lines)
    WITHOUT breaking sentences. If sentences < min_paragraphs, return as-is (caller
    should call expand_summary_with_ai for true expansion)."""
    if not text:
        return text
    import re
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    if len(paragraphs) >= min_paragraphs:
        return "\n\n".join(paragraphs)

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    if len(sentences) < min_paragraphs:
        # Not enough material to safely split; return each sentence as its own paragraph.
        return "\n\n".join(sentences) if sentences else text

    # Distribute sentences across exactly min_paragraphs blocks (1-2 sentences each).
    per = max(1, len(sentences) // min_paragraphs)
    grouped = []
    i = 0
    while i < len(sentences):
        if len(grouped) == min_paragraphs - 1:
            grouped.append(" ".join(sentences[i:]))
            break
        grouped.append(" ".join(sentences[i:i + per]))
        i += per
    return "\n\n".join([g for g in grouped if g.strip()])


async def expand_summary_with_ai(thin_text: str, source_full_text: str = "", min_paragraphs: int = 4) -> str:
    """Use AI to expand a thin (< min_paragraphs) summary into a proper 4-6 paragraph newspaper summary."""
    if not thin_text or not EMERGENT_LLM_KEY:
        return thin_text
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"expand-{uuid.uuid4()}",
            system_message=(
                f"You are a professional newspaper editor. Expand the following short news brief into EXACTLY {min_paragraphs} short paragraphs "
                "(separated by a blank line). Each paragraph should be 1-2 sentences with key facts, context, or background. "
                "Do not invent facts; you may add reasonable context (date, people involved, what it means). "
                "Use formal newspaper tone. Output ONLY the expanded summary, paragraphs separated by '\\n\\n'."
            )
        ).with_model("gemini", "gemini-2.5-flash")
        context = f"\n\nFull article context (optional, for facts only):\n{source_full_text[:2500]}" if source_full_text else ""
        user_message = UserMessage(text=f"Short brief to expand:\n{thin_text}{context}")
        result = await chat.send_message(user_message)
        if result and len(result.strip()) > len(thin_text):
            return ensure_min_paragraphs(result.strip(), min_paragraphs=min_paragraphs)
    except Exception as e:
        logger.warning(f"Summary expansion failed: {e}")
    return thin_text



async def condense_title_for_epaper(title: str, max_chars: int = 75, lang: str = "en") -> str:
    """Use AI to rephrase a long headline into a concise version that fits ~3 lines."""
    if not title or len(title) <= max_chars or not EMERGENT_LLM_KEY:
        return title
    lang_instruction = "Keep the headline in Telugu language." if lang == "te" else "Keep the headline in English."
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"condense-{uuid.uuid4()}",
            system_message=f"You are a newspaper headline editor. Rewrite the given headline to be shorter and punchier while keeping all key facts. {lang_instruction} The result MUST be under the character limit. Output ONLY the rewritten headline, nothing else."
        ).with_model("gemini", "gemini-2.5-flash")
        user_message = UserMessage(text=f"Rewrite this headline in under {max_chars} characters:\n{title}")
        result = await chat.send_message(user_message)
        result = result.strip().strip('"').strip("'")
        if result and len(result) <= max_chars + 10:
            return result
    except Exception as e:
        logger.warning(f"Title condensing failed: {e}")
    return title[:max_chars]


def trim_to_complete_sentences(text: str, max_chars: int, min_chars: int = 0) -> str:
    """Trim text to the last complete sentence within the character limit."""
    if not text:
        return text
    text = text.rstrip('…').strip()
    if text.endswith('...'):
        text = text[:-3].strip()
    elif text.endswith('..'):
        text = text[:-2].strip()

    if len(text) <= max_chars and text and text[-1] in '.!?':
        return text

    # min_acceptable: prefer results at least this long
    min_acceptable = max(min_chars, int(max_chars * 0.5))

    best_result = None
    for extension in [0, 0.15, 0.3, 0.5]:
        limit = min(int(max_chars * (1 + extension)), len(text))
        window = text[:limit]
        last_period = window.rfind('.')
        last_excl = window.rfind('!')
        last_quest = window.rfind('?')
        best = max(last_period, last_excl, last_quest)

        if best > 0:
            end = best + 1
            if end < len(window) and window[end] in '"\'':
                end += 1
            candidate = window[:end].strip()
            if len(candidate) >= min_acceptable:
                return candidate
            if best_result is None or len(candidate) > len(best_result):
                best_result = candidate

    if best_result and len(best_result) > max_chars * 0.2:
        return best_result

    trimmed = text[:max_chars]
    pos = trimmed.rstrip().rfind(' ')
    if pos > 0:
        return trimmed[:pos].strip() + '.'
    return trimmed.strip() + '.'


async def expand_summary_for_epaper(title: str, summary: str, category: str, lang: str = "en") -> str:
    """Expand a short article summary to 400-500 words for ePaper layout filling."""
    if not EMERGENT_LLM_KEY:
        return summary
    if lang == "te":
        lang_inst = "Write the expanded summary in Telugu language only. Do NOT use English."
    else:
        lang_inst = "Write the expanded summary in English."
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"expand-{uuid.uuid4()}",
            system_message=f"""You are a professional newspaper editor. Given an article title, category, and short summary, write an expanded version (400-500 words) that:
- Keeps all original facts intact
- Adds relevant context, background, implications, and analysis
- Uses formal newspaper tone with detailed reporting
- Uses short to medium sentences (40-80 words each). Never write sentences longer than 100 words.
- Is factually grounded (don't invent quotes or specific numbers not in the original)
- Must end with a complete sentence ending in a period
- {lang_inst}
Output ONLY the expanded text, nothing else. Do NOT include any headers or labels."""
        ).with_model("gemini", "gemini-2.5-flash")
        user_message = UserMessage(text=f"Title: {title}\nCategory: {category}\nOriginal: {summary}\n\nWrite at least 400 words of detailed newspaper reporting:")
        result = await chat.send_message(user_message)
        if result and len(result.strip()) > len(summary):
            return result.strip()
    except Exception as e:
        logger.warning(f"Summary expansion failed: {e}")
    return summary


# Known bad image patterns - blurred thumbnails, placeholders, tiny icons
BAD_IMAGE_PATTERNS = [
    "placeholder", "default", "no-image", "noimage", "blank",
    "loading", "icon", "logo", "avatar", "pixel", "spacer",
    "1x1", "transparent", "data:image",
]

MIN_IMAGE_URL_LENGTH = 30

def is_good_image(url: str) -> bool:
    """Filter out likely bad/placeholder/tiny images based on URL patterns."""
    if not url or len(url) < MIN_IMAGE_URL_LENGTH:
        return False
    url_lower = url.lower()
    for pattern in BAD_IMAGE_PATTERNS:
        if pattern in url_lower:
            return False
    # Skip data URIs
    if url_lower.startswith("data:"):
        return False
    # Must have an image extension or be from a CDN
    good_extensions = (".jpg", ".jpeg", ".png", ".webp", ".gif")
    has_ext = any(url_lower.split("?")[0].endswith(ext) for ext in good_extensions)
    is_cdn = any(cdn in url_lower for cdn in ["imagekit", "cloudinary", "pexels", "unsplash", "cdninstagram", "wp-content", "amazonaws", "eenadu", "siasat", "deccanchronicle", "timesofindia", "indiatimes", "way2news"])
    return has_ext or is_cdn
