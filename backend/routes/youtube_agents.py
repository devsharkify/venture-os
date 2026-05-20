"""YouTube AI Agents — Content Curator & Performance Analyzer."""
from fastapi import APIRouter
from database import db, logger, EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime, timezone
import uuid
import asyncio
import json

router = APIRouter(prefix="/api/agents/youtube")


async def _ai_analyze(system_prompt, user_prompt):
    """Run AI analysis via Gemini."""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"yt-agent-{uuid.uuid4()}",
            system_message=system_prompt
        ).with_model("gemini", "gemini-2.5-flash")
        result = await asyncio.wait_for(
            chat.send_message(UserMessage(text=user_prompt)),
            timeout=60
        )
        return result.strip() if result else None
    except Exception as e:
        logger.error(f"YouTube agent AI error: {e}")
        return None


# ============================================================
# AGENT 1: YouTube Content Curator
# ============================================================

@router.get("/content-curator")
async def content_curator_report():
    """AI Content Curator Agent — analyzes video content across channels, identifies trends, suggests content strategy."""
    cached = await db.youtube_agent_reports.find_one(
        {"agent": "content_curator"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    if cached:
        return {"report": cached}
    return {"report": None}


@router.post("/content-curator/run")
async def run_content_curator():
    """Run the Content Curator agent analysis."""
    # Gather channel data
    channels_info = [
        "Mint Street Telugu (2.75M subs, 9143 videos)",
        "Trinetra News Telugu (2.44M subs, 185 videos)",
        "RTV (4.2M subs, 156K videos)",
        "Kaizer Nigha (1.1M subs, 2849 videos)",
        "Ground Zero News Telugu (579K subs, 168 videos)",
        "Mint Street Politics (330K subs, 4873 videos)",
        "Mint Street Andhra (329K subs, 2093 videos)",
        "Praja Toli Velugu (217K subs, 821 videos)",
        "Raama Raajyam TV (115K subs, 3556 videos)",
        "Kaizer Court (105K subs, 2419 videos)",
        "Public Court News (92K subs, 9626 videos)",
        "Mint Street Prakasam (9.7K subs, 648 videos)",
        "Mint Street Telangana (8.6K subs, 2877 videos)",
    ]

    system_prompt = """You are a YouTube Content Curator AI Agent for the Mint Street Network — a Telugu news media group with 13 YouTube channels totaling 12M+ subscribers.

Your job is to analyze the network's channel portfolio and provide actionable content strategy. Return your analysis as a JSON object with this structure:
{
  "network_overview": "Brief summary of the network's YouTube presence",
  "content_strategy": [
    {"title": "Strategy Title", "description": "...", "priority": "high/medium/low", "channels": ["channel names"]}
  ],
  "trending_topics": ["topic1", "topic2", ...],
  "cross_promotion_opportunities": [
    {"from_channel": "...", "to_channel": "...", "strategy": "..."}
  ],
  "content_gaps": [
    {"gap": "...", "recommendation": "...", "potential_channel": "..."}
  ],
  "shorts_strategy": {
    "recommendations": ["..."],
    "best_channels_for_shorts": ["..."],
    "estimated_reach_boost": "..."
  },
  "weekly_content_calendar": [
    {"day": "Monday", "channel": "...", "content_type": "...", "topic": "..."}
  ]
}
Return ONLY valid JSON."""

    user_prompt = f"""Analyze this YouTube news network and provide content strategy:

CHANNELS:
{chr(10).join(f"- {c}" for c in channels_info)}

The network covers: Telangana politics, Andhra Pradesh news, Telugu entertainment, court proceedings, ground-level reporting, and investigative journalism.

Current date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}

Provide a comprehensive content strategy with focus on:
1. How to grow smaller channels using the bigger ones
2. Shorts strategy for maximum reach
3. Content gaps that could be filled
4. Cross-promotion tactics
5. Weekly content calendar"""

    result = await _ai_analyze(system_prompt, user_prompt)
    if not result:
        return {"status": "error", "message": "AI analysis failed"}

    try:
        clean = result.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        report_data = json.loads(clean)
    except json.JSONDecodeError:
        report_data = {"raw_analysis": result}

    report = {
        "agent": "content_curator",
        "report": report_data,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "channels_analyzed": len(channels_info),
    }

    await db.youtube_agent_reports.insert_one({**report})
    # Remove _id before returning
    report.pop("_id", None)
    return {"status": "ok", "report": report}


# ============================================================
# AGENT 2: YouTube Performance Analyzer
# ============================================================

@router.get("/performance")
async def performance_report():
    """YouTube Performance Analyzer — latest report."""
    cached = await db.youtube_agent_reports.find_one(
        {"agent": "performance_analyzer"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    if cached:
        return {"report": cached}
    return {"report": None}


@router.post("/performance/run")
async def run_performance_analyzer():
    """Run the Performance Analyzer agent."""
    channels_data = [
        {"name": "RTV", "subs": 4200000, "videos": 156405, "handle": "R-Telugu-Tv"},
        {"name": "Mint Street Telugu", "subs": 2750000, "videos": 9143, "handle": "KaizerNewsTelugu"},
        {"name": "Trinetra News Telugu", "subs": 2440000, "videos": 185, "handle": "TrinetraNewsTelugu1"},
        {"name": "Kaizer Nigha", "subs": 1110000, "videos": 2849, "handle": "KaizerNigha"},
        {"name": "Ground Zero News Telugu", "subs": 579000, "videos": 168, "handle": "GroundZeroNewsTelugu1"},
        {"name": "Mint Street Politics", "subs": 330000, "videos": 4873, "handle": "KaizerNewsPolitics"},
        {"name": "Mint Street Andhra", "subs": 329000, "videos": 2093, "handle": "KaizerNewsAndhra"},
        {"name": "Praja Toli Velugu", "subs": 217000, "videos": 821, "handle": "Praja-ToliVelugu"},
        {"name": "Raama Raajyam TV", "subs": 115000, "videos": 3556, "handle": "RaamaraajyamTv"},
        {"name": "Kaizer Court", "subs": 105000, "videos": 2419, "handle": "Kaizer-Court"},
        {"name": "Public Court News", "subs": 92400, "videos": 9626, "handle": "publiccourtnews"},
        {"name": "Mint Street Prakasam", "subs": 9700, "videos": 648, "handle": "KaizerNewsPrakasam112"},
        {"name": "Mint Street Telangana", "subs": 8620, "videos": 2877, "handle": "KaizerNewstelangana"},
    ]

    system_prompt = """You are a YouTube Performance Analyzer AI Agent for the Mint Street Network. Analyze channel metrics and provide actionable insights.

Return your analysis as a JSON object:
{
  "network_health_score": 85,
  "total_subscribers": 12000000,
  "total_videos": 195000,
  "channel_rankings": [
    {"rank": 1, "name": "...", "subs": 0, "score": 95, "growth_potential": "high/medium/low", "key_metric": "..."}
  ],
  "growth_insights": [
    {"insight": "...", "impact": "high/medium/low", "channels_affected": ["..."]}
  ],
  "underperforming_channels": [
    {"name": "...", "issue": "...", "fix": "...", "expected_improvement": "..."}
  ],
  "top_performers": [
    {"name": "...", "strength": "...", "recommendation": "..."}
  ],
  "monetization_analysis": {
    "estimated_monthly_revenue": "...",
    "optimization_tips": ["..."],
    "best_revenue_channels": ["..."]
  },
  "growth_targets": {
    "30_day": {"target_subs": 0, "strategy": "..."},
    "90_day": {"target_subs": 0, "strategy": "..."}
  },
  "alerts": [
    {"type": "warning/info/success", "message": "..."}
  ]
}
Return ONLY valid JSON."""

    channels_text = "\n".join([
        f"- {c['name']} (@{c['handle']}): {c['subs']:,} subscribers, {c['videos']:,} videos"
        for c in channels_data
    ])

    user_prompt = f"""Analyze this YouTube news network's performance:

CHANNELS:
{channels_text}

Network total: ~12M subscribers across 13 channels, ~195K videos
Genre: Telugu language news, politics, court proceedings, investigative journalism

Current date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}

Provide detailed performance analysis including:
1. Overall network health score (0-100)
2. Channel-by-channel ranking with growth potential
3. Underperformers and how to fix them
4. Revenue optimization
5. 30-day and 90-day growth targets
6. Alerts for any concerning metrics"""

    result = await _ai_analyze(system_prompt, user_prompt)
    if not result:
        return {"status": "error", "message": "AI analysis failed"}

    try:
        clean = result.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        report_data = json.loads(clean)
    except json.JSONDecodeError:
        report_data = {"raw_analysis": result}

    report = {
        "agent": "performance_analyzer",
        "report": report_data,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "channels_analyzed": len(channels_data),
    }

    await db.youtube_agent_reports.insert_one({**report})
    report.pop("_id", None)
    return {"status": "ok", "report": report}
