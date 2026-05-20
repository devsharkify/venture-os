from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
from database import db, logger, EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage
import uuid
import asyncio

router = APIRouter(prefix="/api/agents")

# ============================================================
# NEWS EDITOR AGENT
# Analyzes articles, detects duplicates, scores importance,
# auto-assigns ePaper positions, generates editorial summaries
# ============================================================

async def _llm_call(system_msg, user_msg):
    """Single LLM call helper with timeout."""
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"agent-{uuid.uuid4()}",
        system_message=system_msg
    ).with_model("gemini", "gemini-2.5-flash")
    try:
        result = await asyncio.wait_for(
            chat.send_message(UserMessage(text=user_msg)),
            timeout=25
        )
        return result.strip() if result else ""
    except (asyncio.TimeoutError, Exception) as e:
        logger.warning(f"LLM call failed: {e}")
        return ""


async def editor_analyze_articles(articles, lang="en"):
    """Editor Agent: Analyze a batch of articles — score, detect duplicates, rank."""
    if not articles:
        return {"ranked": [], "duplicates": [], "editorial": ""}

    # Build concise article list (limit to 30 articles for speed)
    article_list = ""
    for i, a in enumerate(articles[:30]):
        title = a.get("title", "") if lang == "en" else (a.get("title_te", "") or a.get("title", ""))
        source = a.get("source", "unknown")
        cat = a.get("category", "")
        article_list += f"[{i}] {source} | {cat} | {title[:100]}\n"

    lang_name = "Telugu" if lang == "te" else "English"

    # Step 1: Score and rank articles + detect duplicates
    system = """You are an expert newspaper editor for an Indian news platform.
Analyze these articles and return a JSON object with:
1. "ranked": array of article indices [0,1,2...] ordered by editorial importance (most important first).
   Consider: breaking news > political significance > public impact > sports > entertainment
2. "duplicates": array of arrays, where each inner array contains indices of articles covering the SAME story from different sources. Example: [[2,5],[7,12]] means articles 2&5 are duplicates, and 7&12 are duplicates.
3. "hero_picks": array of top 3 article indices that should be hero/featured stories
Return ONLY valid JSON, no markdown."""

    try:
        result = await _llm_call(system, f"Analyze these {len(articles)} articles:\n\n{article_list}")
        # Parse JSON
        import json
        # Clean response
        result = result.replace("```json", "").replace("```", "").strip()
        analysis = json.loads(result)
    except Exception as e:
        logger.warning(f"Editor analysis failed: {e}")
        analysis = {"ranked": list(range(len(articles))), "duplicates": [], "hero_picks": [0, 1, 2]}

    # Step 2: Generate editorial summary combining top stories
    top_indices = analysis.get("hero_picks", [0, 1, 2])[:5]
    top_articles = ""
    for idx in top_indices:
        if idx < len(articles):
            a = articles[idx]
            title = a.get("title", "") if lang == "en" else (a.get("title_te", "") or a.get("title", ""))
            summary = a.get("summary", "") if lang == "en" else (a.get("summary_te", "") or a.get("summary", ""))
            top_articles += f"- {title}: {summary[:300]}\n"

    editorial_system = f"""You are a senior newspaper editor. Write a brief editorial summary (150-200 words) 
that combines the day's top stories into a cohesive "Today's Highlights" briefing.
Write in {lang_name} language. Be professional, concise, and informative.
Output ONLY the editorial text."""

    try:
        editorial = await _llm_call(editorial_system, f"Today's top stories:\n{top_articles}")
    except Exception as e:
        logger.warning(f"Editorial generation failed: {e}")
        editorial = ""

    # Generate Telugu editorial too if English
    editorial_te = ""
    if lang == "en":
        try:
            editorial_te = await _llm_call(
                editorial_system.replace("English", "Telugu"),
                f"Today's top stories:\n{top_articles}\n\nWrite in Telugu only."
            )
        except Exception:
            pass

    return {
        "ranked": analysis.get("ranked", []),
        "duplicates": analysis.get("duplicates", []),
        "hero_picks": analysis.get("hero_picks", []),
        "editorial_en": editorial if lang == "en" else "",
        "editorial_te": editorial_te or (editorial if lang == "te" else ""),
    }


async def editor_merge_duplicates(articles, duplicate_groups):
    """Merge duplicate articles into one comprehensive article."""
    merged = []
    merged_indices = set()

    for group in duplicate_groups:
        if len(group) < 2:
            continue
        # Pick the article with the longest summary as base
        group_articles = [articles[i] for i in group if i < len(articles)]
        if not group_articles:
            continue
        base = max(group_articles, key=lambda a: len(a.get("summary", "")))
        sources = [a.get("source", "") for a in group_articles]
        titles = [a.get("title", "") for a in group_articles]

        # Generate merged summary
        all_summaries = "\n".join([f"[{a.get('source','')}]: {a.get('summary','')[:300]}" for a in group_articles])
        try:
            merged_summary = await _llm_call(
                "You are a news editor. Combine these different reports of the same story into one comprehensive summary (200-300 words). Keep all unique facts. Write in English.",
                f"Title: {base.get('title','')}\nReports:\n{all_summaries}"
            )
            if merged_summary:
                base["summary"] = merged_summary
                base["merged_from"] = sources
                base["merged_titles"] = titles
        except Exception:
            pass

        merged.append(base)
        for idx in group:
            merged_indices.add(idx)

    return merged, merged_indices


AGENT_PYTHON = "/root/.venv/bin/python3"


@router.post("/editor/run")
async def run_editor_agent():
    """Run the News Editor Agent as a subprocess (non-blocking)."""
    import subprocess
    subprocess.Popen(
        [AGENT_PYTHON, "/app/backend/run_agents.py", "editor"],
        cwd="/app/backend",
        stdout=open("/tmp/agent_editor.log", "w"),
        stderr=subprocess.STDOUT
    )
    return {"status": "started", "message": "Editor Agent running. Check /editor/latest for results."}


@router.get("/editor/latest")
async def get_latest_editor_report():
    """Get the latest editor report."""
    report = await db.editor_reports.find_one(
        {}, {"_id": 0}, sort=[("created_at", -1)]
    )
    if not report:
        return {"status": "no_report", "report": None}
    return {"status": "ok", "report": report}


@router.get("/editor/reports")
async def get_editor_reports():
    """Get all editor reports."""
    reports = await db.editor_reports.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(30).to_list(30)
    return {"reports": reports}


# ============================================================
# INVESTIGATIVE REPORTER AGENT
# Tracks topics over time, builds timelines, generates reports
# Pre-configured: Telangana Politics, India Politics, Corruption
# ============================================================

DEFAULT_TOPICS = [
    {
        "id": "telangana-politics",
        "name_en": "Telangana Politics",
        "name_te": "తెలంగాణ రాజకీయాలు",
        "keywords": ["telangana", "kcr", "ktr", "brs", "trs", "revanth reddy", "congress telangana",
                      "hyderabad politics", "cm revanth", "kavitha", "harish rao", "etela rajender",
                      "తెలంగాణ", "కేసీఆర్", "రేవంత్ రెడ్డి", "కాంగ్రెస్"],
        "active": True
    },
    {
        "id": "india-politics",
        "name_en": "India Politics",
        "name_te": "భారత రాజకీయాలు",
        "keywords": ["modi", "rahul gandhi", "parliament", "lok sabha", "rajya sabha", "bjp congress",
                      "election", "amit shah", "nda", "india alliance", "opposition",
                      "మోదీ", "రాహుల్", "పార్లమెంట్", "ఎన్నిక"],
        "active": True
    },
    {
        "id": "corruption",
        "name_en": "Corruption & Scams",
        "name_te": "అవినీతి & కుంభకోణాలు",
        "keywords": ["corruption", "scam", "fraud", "bribe", "cbi", "ed", "enforcement directorate",
                      "money laundering", "hawala", "benami", "disproportionate assets", "arrest",
                      "అవినీతి", "కుంభకోణం", "మోసం", "లంచం"],
        "active": True
    }
]


async def _ensure_topics():
    """Ensure default investigation topics exist."""
    for topic in DEFAULT_TOPICS:
        existing = await db.investigation_topics.find_one({"id": topic["id"]})
        if not existing:
            doc = {**topic}
            doc["created_at"] = datetime.now(timezone.utc).isoformat()
            doc["event_count"] = 0
            doc["last_analyzed"] = None
            await db.investigation_topics.insert_one(doc)


async def _match_articles_to_topic(topic, articles):
    """Find articles matching a topic's keywords."""
    keywords = [k.lower() for k in topic.get("keywords", [])]
    matched = []
    for a in articles:
        text = f"{a.get('title', '')} {a.get('summary', '')} {a.get('title_te', '')} {a.get('summary_te', '')}".lower()
        if any(kw in text for kw in keywords):
            matched.append(a)
    return matched


async def investigate_topic(topic_id):
    """Run investigation on a specific topic — find new articles, build timeline, generate report."""
    topic = await db.investigation_topics.find_one({"id": topic_id}, {"_id": 0})
    if not topic:
        return None

    # Get articles from last 7 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    articles = await db.news.find(
        {"is_active": True, "created_at": {"$gte": cutoff}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(500)

    matched = await _match_articles_to_topic(topic, articles)
    if not matched:
        return {"topic": topic, "matched": 0, "events": [], "report": ""}

    # Build timeline entries
    events = []
    existing_event_links = set()
    existing_events = await db.investigation_events.find(
        {"topic_id": topic_id}, {"_id": 0, "article_link": 1}
    ).to_list(1000)
    for e in existing_events:
        existing_event_links.add(e.get("article_link", ""))

    for a in matched:
        if a.get("link") in existing_event_links:
            continue
        event = {
            "id": str(uuid.uuid4()),
            "topic_id": topic_id,
            "article_id": a.get("id", ""),
            "article_link": a.get("link", ""),
            "title": a.get("title", "") or a.get("title_te", ""),
            "summary": (a.get("summary", "") or a.get("summary_te", ""))[:300],
            "source": a.get("source", ""),
            "category": a.get("category", ""),
            "image": a.get("image", ""),
            "published_at": a.get("published_at", ""),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        events.append(event)

    # Save new events
    if events:
        await db.investigation_events.insert_many(events)

    # Get all events for this topic for the report
    all_events = await db.investigation_events.find(
        {"topic_id": topic_id}, {"_id": 0}
    ).sort("published_at", -1).limit(50).to_list(50)

    # Generate investigation report
    event_summaries = "\n".join([
        f"- [{e.get('source','')}] {e.get('title','')}: {e.get('summary','')[:200]}"
        for e in all_events[:20]
    ])

    report_en = ""
    report_te = ""
    try:
        report_en = await _llm_call(
            f"""You are an investigative journalist. Analyze these news events about "{topic.get('name_en', '')}" and write a comprehensive investigation report (300-500 words).
Include: key developments, patterns, key players, implications, and what to watch next.
Write in English. Be analytical and factual.""",
            f"Topic: {topic.get('name_en', '')}\nRecent events ({len(all_events)} total):\n{event_summaries}"
        )
    except Exception as e:
        logger.warning(f"Investigation report EN failed: {e}")

    try:
        report_te = await _llm_call(
            f"""You are an investigative journalist. Analyze these news events about "{topic.get('name_te', '')}" and write a comprehensive investigation report (300-500 words).
Include: key developments, patterns, key players, implications, and what to watch next.
Write in Telugu only. Be analytical and factual.""",
            f"Topic: {topic.get('name_te', '')}\nRecent events ({len(all_events)} total):\n{event_summaries}"
        )
    except Exception as e:
        logger.warning(f"Investigation report TE failed: {e}")

    # Save report
    report_doc = {
        "id": str(uuid.uuid4()),
        "topic_id": topic_id,
        "topic_name_en": topic.get("name_en", ""),
        "topic_name_te": topic.get("name_te", ""),
        "report_en": report_en,
        "report_te": report_te,
        "total_events": len(all_events),
        "new_events": len(events),
        "matched_articles": len(matched),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    report_copy = {**report_doc}
    await db.investigation_reports.insert_one(report_copy)

    # Update topic stats
    await db.investigation_topics.update_one(
        {"id": topic_id},
        {"$set": {"event_count": len(all_events), "last_analyzed": datetime.now(timezone.utc).isoformat()}}
    )

    report_doc.pop("_id", None)
    return {
        "topic": topic,
        "matched": len(matched),
        "new_events": len(events),
        "total_events": len(all_events),
        "report": report_doc,
        "recent_events": all_events[:10]
    }


@router.get("/investigator/topics")
async def get_investigation_topics():
    """Get all investigation topics."""
    await _ensure_topics()
    topics = await db.investigation_topics.find({}, {"_id": 0}).to_list(50)
    return {"topics": topics}


@router.post("/investigator/run/{topic_id}")
async def run_investigation(topic_id: str):
    """Run investigation on a topic as a subprocess (non-blocking)."""
    import subprocess
    subprocess.Popen(
        [AGENT_PYTHON, "/app/backend/run_agents.py", "investigator", topic_id],
        cwd="/app/backend",
        stdout=open(f"/tmp/agent_invest_{topic_id}.log", "w"),
        stderr=subprocess.STDOUT
    )
    return {"status": "started", "message": f"Investigation running for {topic_id}."}


@router.post("/investigator/run-all")
async def run_all_investigations():
    """Run all investigations as a subprocess (non-blocking)."""
    import subprocess
    subprocess.Popen(
        [AGENT_PYTHON, "/app/backend/run_agents.py", "investigator"],
        cwd="/app/backend",
        stdout=open("/tmp/agent_invest_all.log", "w"),
        stderr=subprocess.STDOUT
    )
    return {"status": "started", "message": "Running all investigations."}


@router.get("/investigator/report/{topic_id}")
async def get_investigation_report(topic_id: str):
    """Get the latest investigation report for a topic."""
    report = await db.investigation_reports.find_one(
        {"topic_id": topic_id}, {"_id": 0}, sort=[("created_at", -1)]
    )
    events = await db.investigation_events.find(
        {"topic_id": topic_id}, {"_id": 0}
    ).sort("published_at", -1).limit(30).to_list(30)
    topic = await db.investigation_topics.find_one({"id": topic_id}, {"_id": 0})
    return {"report": report, "events": events, "topic": topic}


@router.get("/investigator/timeline/{topic_id}")
async def get_topic_timeline(topic_id: str):
    """Get the full event timeline for a topic."""
    events = await db.investigation_events.find(
        {"topic_id": topic_id}, {"_id": 0}
    ).sort("published_at", -1).to_list(100)
    topic = await db.investigation_topics.find_one({"id": topic_id}, {"_id": 0})
    return {"events": events, "topic": topic}


# ============================================================
# AUTO-RUN: Hook into scraper cycle
# ============================================================

async def run_agents_after_scrape():
    """Run both agents after scraper completes — as subprocess to avoid blocking server."""
    import subprocess
    try:
        subprocess.Popen(
            [AGENT_PYTHON, "/app/backend/run_agents.py", "all"],
            cwd="/app/backend",
            stdout=open("/tmp/agent_auto.log", "w"),
            stderr=subprocess.STDOUT
        )
        logger.info("Agents subprocess started after scrape")
    except Exception as e:
        logger.error(f"Failed to start agents: {e}")
