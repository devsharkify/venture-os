"""Run agents as a standalone script (subprocess) to avoid blocking the main server."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import db, logger, EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime, timezone, timedelta
import uuid
import json


async def llm_call(system_msg, user_msg):
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"agent-{uuid.uuid4()}",
        system_message=system_msg
    ).with_model("gemini", "gemini-2.5-flash")
    try:
        result = await asyncio.wait_for(
            chat.send_message(UserMessage(text=user_msg)),
            timeout=30
        )
        return result.strip() if result else ""
    except Exception as e:
        print(f"LLM call failed: {e}")
        return ""


async def run_editor():
    print("Editor Agent: Starting...")
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    articles = await db.news.find(
        {"is_active": True, "created_at": {"$gte": cutoff}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(30)

    if not articles:
        print("No recent articles")
        return

    # Build concise article list
    article_list = ""
    for i, a in enumerate(articles):
        title = a.get("title", "")
        source = a.get("source", "unknown")
        cat = a.get("category", "")
        article_list += f"[{i}] {source} | {cat} | {title[:100]}\n"

    # Step 1: Analyze and rank
    print(f"Analyzing {len(articles)} articles...")
    analysis_result = await llm_call(
        """You are an expert newspaper editor. Analyze these articles and return JSON:
{"ranked": [indices ordered by importance], "duplicates": [[duplicate group indices]], "hero_picks": [top 3 indices]}
Breaking news > political > public impact > sports > entertainment. Return ONLY valid JSON.""",
        f"Articles:\n{article_list}"
    )

    try:
        analysis = json.loads(analysis_result.replace("```json", "").replace("```", "").strip())
    except Exception:
        analysis = {"ranked": list(range(len(articles))), "duplicates": [], "hero_picks": [0, 1, 2]}

    print(f"  Heroes: {analysis.get('hero_picks', [])}")
    print(f"  Duplicates: {len(analysis.get('duplicates', []))} groups")

    # Step 2: Generate editorial
    top_indices = analysis.get("hero_picks", [0, 1, 2])[:5]
    top_summaries = "\n".join([
        f"- {articles[i].get('title', '')}: {articles[i].get('summary', '')[:200]}"
        for i in top_indices if i < len(articles)
    ])

    print("Generating editorial...")
    editorial_en = await llm_call(
        "Write a 150-200 word 'Today's Highlights' editorial briefing combining these top stories. English only. Output ONLY the text.",
        f"Top stories:\n{top_summaries}"
    )

    # Save report
    report = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_articles": len(articles),
        "hero_picks": analysis.get("hero_picks", []),
        "ranked_order": analysis.get("ranked", []),
        "duplicate_groups": analysis.get("duplicates", []),
        "merged_count": 0,
        "editorial_en": editorial_en,
        "hero_articles": [
            {"title": articles[i].get("title", ""), "id": articles[i].get("id", ""), "source": articles[i].get("source", "")}
            for i in analysis.get("hero_picks", [])[:5] if i < len(articles)
        ],
        "duplicate_details": [
            [{"title": articles[i].get("title", "")[:80], "source": articles[i].get("source", "")}
             for i in group if i < len(articles)]
            for group in analysis.get("duplicates", [])
        ]
    }
    await db.editor_reports.insert_one({**report})

    # Update priorities
    for rank, idx in enumerate(analysis.get("ranked", [])):
        if idx < len(articles):
            await db.news.update_one(
                {"id": articles[idx].get("id")},
                {"$set": {"priority": max(1, 10 - rank), "editor_rank": rank + 1}}
            )
    for idx in analysis.get("hero_picks", [])[:3]:
        if idx < len(articles):
            await db.news.update_one(
                {"id": articles[idx].get("id")},
                {"$set": {"is_hero": True, "editor_featured": True}}
            )

    print(f"Editor Agent: Done! {len(articles)} articles, editorial generated.")


async def run_investigator(topic_id=None):
    # Ensure default topics
    from routes.agents import DEFAULT_TOPICS
    for topic_data in DEFAULT_TOPICS:
        existing = await db.investigation_topics.find_one({"id": topic_data["id"]})
        if not existing:
            doc = {**topic_data, "created_at": datetime.now(timezone.utc).isoformat(), "event_count": 0, "last_analyzed": None}
            await db.investigation_topics.insert_one(doc)

    if topic_id:
        topics = [await db.investigation_topics.find_one({"id": topic_id}, {"_id": 0})]
        topics = [t for t in topics if t]
    else:
        topics = await db.investigation_topics.find({"active": True}, {"_id": 0}).to_list(50)

    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    all_articles = await db.news.find(
        {"is_active": True, "created_at": {"$gte": cutoff}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(500)

    for topic in topics:
        print(f"\nInvestigating: {topic.get('name_en', '')}")
        keywords = [k.lower() for k in topic.get("keywords", [])]
        matched = [a for a in all_articles if any(
            kw in f"{a.get('title','')} {a.get('summary','')}".lower()
            for kw in keywords
        )]
        print(f"  Matched {len(matched)} articles")

        # Save new events
        existing_links = set()
        existing = await db.investigation_events.find({"topic_id": topic["id"]}, {"_id": 0, "article_link": 1}).to_list(1000)
        for e in existing:
            existing_links.add(e.get("article_link", ""))

        new_events = []
        for a in matched:
            if a.get("link") in existing_links:
                continue
            new_events.append({
                "id": str(uuid.uuid4()),
                "topic_id": topic["id"],
                "article_id": a.get("id", ""),
                "article_link": a.get("link", ""),
                "title": a.get("title", ""),
                "summary": a.get("summary", "")[:300],
                "source": a.get("source", ""),
                "category": a.get("category", ""),
                "image": a.get("image", ""),
                "published_at": a.get("published_at", ""),
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        if new_events:
            await db.investigation_events.insert_many(new_events)
        print(f"  New events: {len(new_events)}")

        # Get all events for report
        all_events = await db.investigation_events.find(
            {"topic_id": topic["id"]}, {"_id": 0}
        ).sort("published_at", -1).limit(30).to_list(30)

        event_text = "\n".join([
            f"- [{e.get('source','')}] {e.get('title','')}: {e.get('summary','')[:150]}"
            for e in all_events[:15]
        ])

        print("  Generating report...")
        report_en = await llm_call(
            f"""You are an investigative journalist. Analyze events about "{topic.get('name_en', '')}" and write a 300-500 word investigation report.
Include: key developments, patterns, key players, implications, what to watch next. English only.""",
            f"Topic: {topic.get('name_en','')}\nEvents ({len(all_events)}):\n{event_text}"
        )

        report_doc = {
            "id": str(uuid.uuid4()),
            "topic_id": topic["id"],
            "topic_name_en": topic.get("name_en", ""),
            "report_en": report_en,
            "total_events": len(all_events),
            "new_events": len(new_events),
            "matched_articles": len(matched),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.investigation_reports.insert_one({**report_doc})
        await db.investigation_topics.update_one(
            {"id": topic["id"]},
            {"$set": {"event_count": len(all_events), "last_analyzed": datetime.now(timezone.utc).isoformat()}}
        )
        print(f"  Report saved: {len(all_events)} total events")

    print("\nInvestigative Agent: Done!")


async def run_seo():
    """Run SEO Agent analysis."""
    print("SEO Agent: Starting...")
    from routes.seo_agent import run_seo_analysis
    report = await run_seo_analysis()
    if report:
        print(f"SEO Agent: Done! Score={report.get('seo_score', 'N/A')}, {report.get('total_articles_analyzed', 0)} articles analyzed")
        print(f"  Trending keywords: {len(report.get('trending_keywords', []))}")
        print(f"  Tweets generated: {len(report.get('tweets', []))}")
        print(f"  Content gaps: {len(report.get('content_gaps', []))}")
    else:
        print("SEO Agent: No articles to analyze")


async def run_tech():
    """Run Tech Performance report."""
    print("Tech Agent: Starting...")
    from routes.tech_agent import generate_performance_report
    report = await generate_performance_report()
    if report:
        print(f"Tech Agent: Done! Health={report.get('health_score', 'N/A')}/100")
        print(f"  Requests (1h): {report.get('last_hour', {}).get('total_requests', 0)}")
        print(f"  Avg response: {report.get('last_hour', {}).get('avg_response_ms', 0)}ms")
    else:
        print("Tech Agent: No metrics available")


async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    topic_id = sys.argv[2] if len(sys.argv) > 2 else None

    if mode in ("editor", "all"):
        await run_editor()
    if mode in ("investigator", "all"):
        await run_investigator(topic_id)
    if mode in ("seo", "all"):
        await run_seo()
    if mode in ("tech", "all"):
        await run_tech()


if __name__ == "__main__":
    asyncio.run(main())
