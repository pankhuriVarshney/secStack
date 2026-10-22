import datetime as dt
from fastapi import APIRouter, Query

from app.db import db

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/timeseries")
def timeseries(days: int = Query(30, ge=7, le=365)):
    start = (dt.date.today() - dt.timedelta(days=days - 1)).isoformat()
    per_day_cat = {}
    for d in db.resources.find({"published_day": {"$gte": start}},
                               {"published_day": 1, "category": 1}):
        day = per_day_cat.setdefault(d["published_day"], {})
        day[d["category"]] = day.get(d["category"], 0) + 1
    out = []
    for i in range(days):
        day = (dt.date.today() - dt.timedelta(days=days - 1 - i)).isoformat()
        by_cat = per_day_cat.get(day, {})
        out.append({"date": day, "count": sum(by_cat.values()),
                    "by_category": by_cat})
    return out


@router.get("/sources")
def sources():
    cur = db.resources.aggregate([
        {"$group": {"_id": "$source_domain", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}, {"$limit": 25}])
    return [{"domain": d["_id"], "count": d["count"]} for d in cur]


@router.get("/publishers")
def publisher_stats():
    publishers = list(db.publisher_health.find({}, {"_id": 0}))
    from scripts.ingest_rss import FEEDS
    existing_domains = {p["domain"] for p in publishers}
    for url, cat, name, domain in FEEDS:
        if domain not in existing_domains:
            publishers.append({
                "name": name,
                "domain": domain,
                "url": url,
                "fallback_category": cat,
                "status": "pending",
                "last_fetched_at": None,
                "articles_ingested": 0,
                "error": None
            })
    
    total_configured = len(FEEDS)
    healthy = sum(1 for p in publishers if p.get("status") == "healthy")
    failing = sum(1 for p in publishers if p.get("status") == "failing")
    
    domain_counts = {}
    for r in db.resources.find({}, {"source_domain": 1}):
        d = r.get("source_domain")
        if d:
            domain_counts[d] = domain_counts.get(d, 0) + 1

    unique_articles = db.resources.estimated_document_count()
    spark_processed = db.resources.count_documents({"cluster_id": {"$exists": True}})
    clusters_count = db.clusters.count_documents({})
    
    return {
        "total_configured": total_configured,
        "healthy_feeds": healthy,
        "failing_feeds": failing,
        "unique_articles": unique_articles,
        "spark_processed_articles": spark_processed,
        "clustering_run_count": clusters_count,
        "publishers": publishers,
        "domain_distribution": domain_counts
    }
