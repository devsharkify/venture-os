"""Celery tasks - unified background jobs for scrapers, agents, SEO, Telegram, performance."""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from celery_app import app
from database import db, logger

# Helper to run async functions in sync celery tasks
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ============================================================
# SCRAPER TASKS
# ============================================================

@app.task(name="tasks.scrape_all_sources", bind=True, max_retries=2)
def scrape_all_sources(self):
    """Run all 5 scrapers and trigger post-scrape SEO + agents."""
    from routes.scraper import scrape_siasat, scrape_deccan_chronicle, scrape_toi, scrape_eenadu, scrape_way2news

    async def _run():
        results = await asyncio.gather(
            scrape_siasat(), scrape_deccan_chronicle(), scrape_toi(),
            scrape_eenadu(), scrape_way2news(),
            return_exceptions=True
        )
        total = sum(r for r in results if isinstance(r, int))
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Scraper error: {r}")
        logger.info(f"All scrapers done: {total} new articles added")

        if total > 0:
            # Trigger agents
            run_all_agents.delay()
            # Trigger SEO meta generation for new articles
            backfill_seo_meta.delay()

        return total

    return run_async(_run())


# ============================================================
# AGENT TASKS
# ============================================================

@app.task(name="tasks.run_all_agents", bind=True, max_retries=1, soft_time_limit=180)
def run_all_agents(self):
    """Run all AI agents (editor, investigator, SEO analysis, tech report)."""
    import subprocess
    AGENT_PYTHON = "/root/.venv/bin/python3"
    try:
        result = subprocess.run(
            [AGENT_PYTHON, "/app/backend/run_agents.py", "all"],
            cwd="/app/backend",
            capture_output=True, text=True, timeout=180
        )
        logger.info(f"Agents completed: {result.stdout[-200:] if result.stdout else 'no output'}")
        return {"status": "completed", "output": result.stdout[-500:]}
    except Exception as e:
        logger.error(f"Agents failed: {e}")
        return {"status": "failed", "error": str(e)}


@app.task(name="tasks.run_editor_agent")
def run_editor_agent():
    """Run editor agent only."""
    import subprocess
    subprocess.run(
        ["/root/.venv/bin/python3", "/app/backend/run_agents.py", "editor"],
        cwd="/app/backend", capture_output=True, timeout=120
    )


@app.task(name="tasks.run_investigator_agent")
def run_investigator_agent(topic_id=None):
    """Run investigator agent."""
    import subprocess
    cmd = ["/root/.venv/bin/python3", "/app/backend/run_agents.py", "investigator"]
    if topic_id:
        cmd.append(topic_id)
    subprocess.run(cmd, cwd="/app/backend", capture_output=True, timeout=120)


@app.task(name="tasks.run_seo_agent")
def run_seo_agent():
    """Run SEO analysis agent."""
    import subprocess
    subprocess.run(
        ["/root/.venv/bin/python3", "/app/backend/run_agents.py", "seo"],
        cwd="/app/backend", capture_output=True, timeout=120
    )


# ============================================================
# SEO TASKS
# ============================================================

@app.task(name="tasks.backfill_seo_meta")
def backfill_seo_meta():
    """Generate SEO meta tags for articles that don't have them."""
    from routes.seo_engine import batch_generate_seo_meta
    count = run_async(batch_generate_seo_meta(20))
    logger.info(f"SEO backfill: {count} articles processed")
    return count


@app.task(name="tasks.generate_static_seo")
def generate_static_seo():
    """Regenerate static sitemap.xml, robots.txt, rss.xml."""
    from routes.seo_engine import generate_static_seo_files
    run_async(generate_static_seo_files())
    logger.info("Static SEO files regenerated")


@app.task(name="tasks.ping_indexnow_urls")
def ping_indexnow_urls(urls):
    """Ping IndexNow with new URLs."""
    from routes.seo_engine import ping_indexnow
    run_async(ping_indexnow(urls))


# ============================================================
# TELEGRAM TASKS
# ============================================================

@app.task(name="tasks.send_morning_report")
def send_morning_report():
    """Send 6 AM IST morning report + ePaper PDFs."""
    from routes.telegram_bot import scheduled_morning
    run_async(scheduled_morning())
    logger.info("Morning report sent")


@app.task(name="tasks.send_evening_report")
def send_evening_report():
    """Send 6 PM IST evening report + SEO + Perf reports."""
    from routes.telegram_bot import scheduled_evening, tg_send, _get_admin_chat_id
    from routes.seo_agent import generate_seo_telegram_report
    from routes.tech_agent import generate_perf_telegram_report, generate_performance_report

    async def _run():
        await scheduled_evening()

        chat_id = await _get_admin_chat_id()
        if chat_id:
            try:
                seo_text = await generate_seo_telegram_report()
                await tg_send(chat_id, seo_text)
            except Exception as e:
                logger.error(f"SEO telegram report failed: {e}")

            try:
                await generate_performance_report()
                perf_text = await generate_perf_telegram_report()
                await tg_send(chat_id, perf_text)
            except Exception as e:
                logger.error(f"Perf telegram report failed: {e}")

    run_async(_run())
    logger.info("Evening report + SEO + Perf sent")


# ============================================================
# PERFORMANCE TASKS
# ============================================================

@app.task(name="tasks.generate_perf_report")
def generate_perf_report():
    """Generate performance report."""
    from routes.tech_agent import generate_performance_report
    report = run_async(generate_performance_report())
    return {"health_score": report.get("health_score") if report else None}


@app.task(name="tasks.cleanup_old_metrics")
def cleanup_old_metrics():
    """Clean up metrics older than 7 days."""
    from datetime import datetime, timezone, timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    async def _cleanup():
        result = await db.perf_metrics.delete_many({"timestamp": {"$lt": cutoff}})
        logger.info(f"Cleaned up {result.deleted_count} old metrics")
        return result.deleted_count

    return run_async(_cleanup())
