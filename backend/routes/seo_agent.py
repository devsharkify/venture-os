"""Social Media Expert Agent - SEO optimization, trending content, social media posts."""
from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
from database import db, logger, EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage
import uuid
import asyncio
import json

router = APIRouter(prefix="/api/agents/seo")

AGENT_PYTHON = "/root/.venv/bin/python3"


async def _llm_call(system_msg, user_msg):
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"seo-{uuid.uuid4()}",
        system_message=system_msg
    ).with_model("gemini", "gemini-2.5-flash")
    try:
        result = await asyncio.wait_for(
            chat.send_message(UserMessage(text=user_msg)),
            timeout=30
        )
        return result.strip() if result else ""
    except Exception as e:
        logger.warning(f"SEO LLM call failed: {e}")
        return ""


async def run_seo_analysis():
    """Analyze recent articles and generate SEO recommendations, social content, trending keywords."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    articles = await db.news.find(
        {"is_active": True, "created_at": {"$gte": cutoff}},
        {"_id": 0, "title": 1, "summary": 1, "category": 1, "source": 1, "id": 1}
    ).sort("created_at", -1).to_list(30)

    if not articles:
        return None

    # Build article list for AI
    article_list = "\n".join([
        f"[{i}] ({a.get('category','')}) {a.get('title','')[:120]}"
        for i, a in enumerate(articles)
    ])

    # Step 1: SEO Keywords & Trending Analysis
    seo_result = await _llm_call(
        """You are an SEO expert for an Indian news platform called "Mint Street" (kaizernews.com).
Analyze these articles and return JSON with:
1. "trending_keywords": top 15 keywords/phrases people are searching right now related to these stories. Include both English and Telugu search terms.
2. "meta_suggestions": array of top 5 articles (by index) that need better SEO, each with: {"index": N, "optimized_title": "...", "meta_description": "...(max 155 chars)", "focus_keyword": "..."}
3. "content_gaps": 3-5 trending topics in India/Telangana that Mint Street should cover but hasn't yet.
4. "seo_score": overall score 1-100 for how well these articles are optimized for search.
Return ONLY valid JSON, no markdown.""",
        f"Today's {len(articles)} articles:\n{article_list}"
    )

    try:
        seo_data = json.loads(seo_result.replace("```json", "").replace("```", "").strip())
    except Exception:
        seo_data = {"trending_keywords": [], "meta_suggestions": [], "content_gaps": [], "seo_score": 50}

    # Step 2: Generate Social Media Posts
    top_5 = articles[:5]
    top_summaries = "\n".join([
        f"- {a.get('title','')}: {a.get('summary','')[:150]}" for a in top_5
    ])

    social_result = await _llm_call(
        """You are a social media manager for "Mint Street", an Indian news platform.
Create viral social media content. Return JSON with:
1. "tweets": array of 5 tweet-style posts (max 280 chars each) for these news stories. Include relevant #hashtags and make them engaging.
2. "instagram_captions": array of 3 longer captions (100-200 words) for Instagram/Facebook posts.
3. "hashtag_sets": array of 3 hashtag collections (10-15 tags each) optimized for discoverability. Mix popular + niche tags.
4. "best_posting_times": array of 3 optimal posting times for Indian audience (e.g., "9:00 AM IST - Morning commuters").
Return ONLY valid JSON.""",
        f"Top stories:\n{top_summaries}"
    )

    try:
        social_data = json.loads(social_result.replace("```json", "").replace("```", "").strip())
    except Exception:
        social_data = {"tweets": [], "instagram_captions": [], "hashtag_sets": [], "best_posting_times": []}

    # Step 3: Competitor & Search Trends Summary
    trend_result = await _llm_call(
        """You are a digital marketing strategist. Based on these Indian news articles, write a brief SEO strategy report (200-300 words) for "Mint Street" covering:
1. Which topics are trending in search right now
2. Quick wins to rank higher on Google for these stories
3. Content strategy recommendations for the next 24 hours
4. Suggested internal linking opportunities between articles
Write in English, be actionable and specific.""",
        f"Articles:\n{article_list}"
    )

    # Enrich meta_suggestions with actual article data
    enriched_metas = []
    for m in seo_data.get("meta_suggestions", []):
        idx = m.get("index", 0)
        if idx < len(articles):
            enriched_metas.append({
                "article_id": articles[idx].get("id", ""),
                "original_title": articles[idx].get("title", ""),
                "optimized_title": m.get("optimized_title", ""),
                "meta_description": m.get("meta_description", ""),
                "focus_keyword": m.get("focus_keyword", ""),
                "category": articles[idx].get("category", ""),
            })

    report = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_articles_analyzed": len(articles),
        "seo_score": seo_data.get("seo_score", 50),
        "trending_keywords": seo_data.get("trending_keywords", []),
        "meta_suggestions": enriched_metas,
        "content_gaps": seo_data.get("content_gaps", []),
        "tweets": social_data.get("tweets", []),
        "instagram_captions": social_data.get("instagram_captions", []),
        "hashtag_sets": social_data.get("hashtag_sets", []),
        "best_posting_times": social_data.get("best_posting_times", []),
        "strategy_report": trend_result,
    }

    await db.seo_reports.insert_one({**report})
    return report


async def generate_seo_telegram_report():
    """Generate a Telegram-friendly SEO report."""
    report = await db.seo_reports.find_one({}, {"_id": 0}, sort=[("created_at", -1)])
    if not report:
        return "No SEO report available yet."

    keywords = ", ".join(report.get("trending_keywords", [])[:10])
    tweets = report.get("tweets", [])[:3]
    tweet_text = "\n".join([f"  {i+1}. {t[:100]}" for i, t in enumerate(tweets)])
    gaps = report.get("content_gaps", [])[:3]
    gap_text = "\n".join([f"  - {g}" for g in gaps]) or "  None identified"
    score = report.get("seo_score", "N/A")

    return f"""<b>SEO & Social Media Report</b>

<b>SEO Score:</b> {score}/100

<b>Trending Keywords:</b>
{keywords}

<b>Content Gaps (Missing Coverage):</b>
{gap_text}

<b>Ready-to-Post Tweets:</b>
{tweet_text}

<b>Articles Analyzed:</b> {report.get('total_articles_analyzed', 0)}

<i>Generated at {datetime.now(timezone.utc).strftime('%H:%M UTC')}</i>"""


# ============================================================
# API Endpoints
# ============================================================

@router.post("/run")
async def api_run_seo():
    """Run SEO agent as subprocess (non-blocking)."""
    import subprocess
    subprocess.Popen(
        [AGENT_PYTHON, "/app/backend/run_agents.py", "seo"],
        cwd="/app/backend",
        stdout=open("/tmp/agent_seo.log", "w"),
        stderr=subprocess.STDOUT
    )
    return {"status": "started", "message": "SEO Agent running. Check /seo/latest for results."}


@router.get("/latest")
async def get_latest_seo_report():
    """Get the most recent SEO report."""
    report = await db.seo_reports.find_one({}, {"_id": 0}, sort=[("created_at", -1)])
    if not report:
        return {"status": "no_report", "report": None}
    return {"status": "ok", "report": report}


@router.get("/reports")
async def get_seo_reports():
    """Get recent SEO reports."""
    reports = await db.seo_reports.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(30).to_list(30)
    return {"reports": reports}


@router.get("/keywords")
async def get_trending_keywords():
    """Get latest trending keywords."""
    report = await db.seo_reports.find_one({}, {"_id": 0, "trending_keywords": 1, "created_at": 1}, sort=[("created_at", -1)])
    if not report:
        return {"keywords": []}
    return {"keywords": report.get("trending_keywords", []), "updated_at": report.get("created_at", "")}


@router.get("/social-content")
async def get_social_content():
    """Get latest social media content."""
    report = await db.seo_reports.find_one(
        {}, {"_id": 0, "tweets": 1, "instagram_captions": 1, "hashtag_sets": 1, "best_posting_times": 1, "created_at": 1},
        sort=[("created_at", -1)]
    )
    if not report:
        return {"content": None}
    return {"content": report}
