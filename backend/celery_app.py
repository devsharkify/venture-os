"""Celery application configuration — unified task queue for all background jobs."""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from celery import Celery
from celery.schedules import crontab

app = Celery(
    "kaizer_news",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 min max per task
    task_soft_time_limit=240,
    worker_concurrency=2,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=50,
)

# Beat schedule — replaces telegram_scheduler.py and scraper_loop
app.conf.beat_schedule = {
    "scrape-all-sources": {
        "task": "tasks.scrape_all_sources",
        "schedule": 1800.0,  # Every 30 minutes
    },
    "morning-report-6am": {
        "task": "tasks.send_morning_report",
        "schedule": crontab(hour=0, minute=30),  # 6:00 AM IST = 00:30 UTC
    },
    "evening-report-6pm": {
        "task": "tasks.send_evening_report",
        "schedule": crontab(hour=12, minute=30),  # 6:00 PM IST = 12:30 UTC
    },
    "seo-meta-backfill": {
        "task": "tasks.backfill_seo_meta",
        "schedule": 3600.0,  # Every hour
    },
    "static-seo-regenerate": {
        "task": "tasks.generate_static_seo",
        "schedule": 1800.0,  # Every 30 minutes (after scraper runs)
    },
    "perf-report-hourly": {
        "task": "tasks.generate_perf_report",
        "schedule": 3600.0,  # Every hour
    },
    "cleanup-old-metrics": {
        "task": "tasks.cleanup_old_metrics",
        "schedule": crontab(hour=2, minute=0),  # 7:30 AM IST daily
    },
}

app.autodiscover_tasks(["tasks"])
