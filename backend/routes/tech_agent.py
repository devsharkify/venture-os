"""Tech Performance Agent - monitors API speed, DB performance, detects anomalies."""
from fastapi import APIRouter, Request
from datetime import datetime, timezone, timedelta
from database import db, logger
import time
import asyncio

router = APIRouter(prefix="/api/agents/tech")

# In-memory buffer for recent metrics (flushed to DB periodically)
_metrics_buffer = []
_BUFFER_FLUSH_SIZE = 50


async def record_metric(endpoint: str, method: str, status_code: int, response_time_ms: float):
    """Record a single API metric."""
    _metrics_buffer.append({
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "response_time_ms": round(response_time_ms, 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    if len(_metrics_buffer) >= _BUFFER_FLUSH_SIZE:
        await flush_metrics()


async def flush_metrics():
    """Flush in-memory metrics to database."""
    global _metrics_buffer
    if not _metrics_buffer:
        return
    to_flush = _metrics_buffer[:]
    _metrics_buffer = []
    try:
        await db.perf_metrics.insert_many(to_flush)
    except Exception as e:
        logger.error(f"Failed to flush perf metrics: {e}")


async def generate_performance_report():
    """Analyze recent metrics and produce a performance report."""
    now = datetime.now(timezone.utc)
    cutoff_1h = (now - timedelta(hours=1)).isoformat()
    cutoff_24h = (now - timedelta(hours=24)).isoformat()

    # Flush any pending metrics first
    await flush_metrics()

    # Get last hour metrics
    metrics_1h = await db.perf_metrics.find(
        {"timestamp": {"$gte": cutoff_1h}}, {"_id": 0}
    ).to_list(5000)

    # Get 24h metrics for trends
    pipeline_24h = [
        {"$match": {"timestamp": {"$gte": cutoff_24h}}},
        {"$group": {
            "_id": "$endpoint",
            "avg_ms": {"$avg": "$response_time_ms"},
            "max_ms": {"$max": "$response_time_ms"},
            "min_ms": {"$min": "$response_time_ms"},
            "count": {"$sum": 1},
            "errors": {"$sum": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}}
        }},
        {"$sort": {"avg_ms": -1}}
    ]
    endpoint_stats = await db.perf_metrics.aggregate(pipeline_24h).to_list(100)

    # Overall stats for last hour
    total_1h = len(metrics_1h)
    if total_1h > 0:
        avg_1h = round(sum(m["response_time_ms"] for m in metrics_1h) / total_1h, 2)
        max_1h = round(max(m["response_time_ms"] for m in metrics_1h), 2)
        errors_1h = sum(1 for m in metrics_1h if m.get("status_code", 200) >= 400)
        p95_sorted = sorted([m["response_time_ms"] for m in metrics_1h])
        p95_idx = int(len(p95_sorted) * 0.95)
        p95_1h = round(p95_sorted[min(p95_idx, len(p95_sorted) - 1)], 2)
    else:
        avg_1h = max_1h = p95_1h = 0
        errors_1h = 0

    # Detect slow endpoints (>500ms avg)
    slow_endpoints = [e for e in endpoint_stats if e.get("avg_ms", 0) > 500]

    # Detect anomalies - endpoints with error rate >10%
    anomalies = []
    for e in endpoint_stats:
        if e["count"] > 5 and e.get("errors", 0) / e["count"] > 0.1:
            anomalies.append({
                "endpoint": e["_id"],
                "error_rate": round(e["errors"] / e["count"] * 100, 1),
                "total_requests": e["count"]
            })

    # Health score: 100 - penalties
    health_score = 100
    if avg_1h > 300:
        health_score -= min(20, int((avg_1h - 300) / 50))
    if p95_1h > 1000:
        health_score -= min(20, int((p95_1h - 1000) / 200))
    if errors_1h > 0 and total_1h > 0:
        error_rate = errors_1h / total_1h
        health_score -= min(30, int(error_rate * 100))
    if slow_endpoints:
        health_score -= min(15, len(slow_endpoints) * 3)
    health_score = max(0, health_score)

    # Top 10 endpoints by response time
    top_endpoints = []
    for e in endpoint_stats[:10]:
        top_endpoints.append({
            "endpoint": e["_id"],
            "avg_ms": round(e.get("avg_ms", 0), 2),
            "max_ms": round(e.get("max_ms", 0), 2),
            "requests": e["count"],
            "errors": e.get("errors", 0)
        })

    report = {
        "id": str(f"perf-{now.strftime('%Y%m%d-%H%M')}"),
        "created_at": now.isoformat(),
        "health_score": health_score,
        "last_hour": {
            "total_requests": total_1h,
            "avg_response_ms": avg_1h,
            "max_response_ms": max_1h,
            "p95_response_ms": p95_1h,
            "error_count": errors_1h,
        },
        "top_endpoints": top_endpoints,
        "slow_endpoints": [{"endpoint": e["_id"], "avg_ms": round(e["avg_ms"], 2)} for e in slow_endpoints[:5]],
        "anomalies": anomalies,
        "total_endpoints_tracked": len(endpoint_stats),
    }

    await db.perf_reports.insert_one({**report})
    return report


async def generate_perf_telegram_report():
    """Generate Telegram-friendly performance report."""
    report = await db.perf_reports.find_one({}, {"_id": 0}, sort=[("created_at", -1)])
    if not report:
        return "No performance data collected yet. Metrics will appear after API activity."

    lh = report.get("last_hour", {})
    health = report.get("health_score", 0)
    health_emoji = "🟢" if health >= 80 else ("🟡" if health >= 50 else "🔴")

    slow = report.get("slow_endpoints", [])
    slow_text = "\n".join([f"  - {s['endpoint']}: {s['avg_ms']}ms" for s in slow[:3]]) if slow else "  None detected"

    anomaly = report.get("anomalies", [])
    anomaly_text = "\n".join([f"  - {a['endpoint']}: {a['error_rate']}% errors" for a in anomaly[:3]]) if anomaly else "  None detected"

    top = report.get("top_endpoints", [])[:5]
    top_text = "\n".join([f"  {e['endpoint']}: {e['avg_ms']}ms ({e['requests']} reqs)" for e in top]) if top else "  No data"

    return f"""<b>{health_emoji} Tech Performance Report</b>

<b>Health Score:</b> {health}/100

<b>Last Hour:</b>
  Requests: {lh.get('total_requests', 0)}
  Avg Response: {lh.get('avg_response_ms', 0)}ms
  P95: {lh.get('p95_response_ms', 0)}ms
  Max: {lh.get('max_response_ms', 0)}ms
  Errors: {lh.get('error_count', 0)}

<b>Slow Endpoints (>500ms):</b>
{slow_text}

<b>Anomalies:</b>
{anomaly_text}

<b>Top Endpoints:</b>
{top_text}

<i>Generated at {datetime.now(timezone.utc).strftime('%H:%M UTC')}</i>"""


# ============================================================
# Performance Middleware
# ============================================================

async def performance_middleware(request: Request, call_next):
    """Middleware to track API response times."""
    # Skip static files and health checks
    path = request.url.path
    if not path.startswith("/api") or path == "/api/health":
        return await call_next(request)

    start = time.time()
    response = await call_next(request)
    elapsed_ms = (time.time() - start) * 1000

    # Record async - don't block the response
    asyncio.create_task(record_metric(
        endpoint=path,
        method=request.method,
        status_code=response.status_code,
        response_time_ms=elapsed_ms
    ))

    return response


# ============================================================
# API Endpoints
# ============================================================

@router.post("/run")
async def api_run_tech_report():
    """Generate fresh performance report."""
    report = await generate_performance_report()
    return {"status": "ok", "report": report}


@router.get("/latest")
async def get_latest_report():
    """Get the most recent performance report."""
    report = await db.perf_reports.find_one({}, {"_id": 0}, sort=[("created_at", -1)])
    if not report:
        return {"status": "no_report", "report": None}
    return {"status": "ok", "report": report}


@router.get("/reports")
async def get_reports():
    """Get recent performance reports."""
    reports = await db.perf_reports.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(30).to_list(30)
    return {"reports": reports}


@router.get("/metrics/recent")
async def get_recent_metrics():
    """Get last 100 raw API metrics."""
    await flush_metrics()
    metrics = await db.perf_metrics.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).limit(100).to_list(100)
    return {"metrics": metrics}


@router.get("/metrics/endpoints")
async def get_endpoint_stats():
    """Get per-endpoint aggregated stats for last 24h."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$group": {
            "_id": "$endpoint",
            "avg_ms": {"$avg": "$response_time_ms"},
            "max_ms": {"$max": "$response_time_ms"},
            "count": {"$sum": 1},
            "errors": {"$sum": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 30}
    ]
    stats = await db.perf_metrics.aggregate(pipeline).to_list(30)
    return {"endpoints": [
        {
            "endpoint": s["_id"],
            "avg_ms": round(s["avg_ms"], 2),
            "max_ms": round(s["max_ms"], 2),
            "requests": s["count"],
            "errors": s.get("errors", 0)
        } for s in stats
    ]}


@router.delete("/metrics/cleanup")
async def cleanup_old_metrics():
    """Remove metrics older than 7 days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    result = await db.perf_metrics.delete_many({"timestamp": {"$lt": cutoff}})
    return {"deleted": result.deleted_count}
