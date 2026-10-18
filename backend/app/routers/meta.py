from fastapi import APIRouter, HTTPException

from app.db import db
from app.seed_data import CATEGORIES
from scripts.ingest_rss import run as run_rss_ingest

router = APIRouter(tags=["meta"])


@router.get("/galaxy")
def galaxy():
    doc = db.galaxy.find_one({}, {"_id": 0})
    if not doc:
        raise HTTPException(503, "galaxy not built -- run scripts.seed_and_cluster.py")
    return doc


@router.get("/categories")
def categories():
    out = []
    for c in CATEGORIES:
        count = db.resources.count_documents({"category": c["slug"]})
        cluster = db.clusters.find_one({"slug": {"$regex": f"^{c['slug']}"}},
                                       {"top_terms": 1}) or {}
        out.append({**c, "count": count, "top_terms": cluster.get("top_terms", [])})
    return out


@router.get("/planets/{slug}")
def planet(slug: str):
    cluster = db.clusters.find_one({"slug": {"$regex": f"^{slug}"}}, {"_id": 0})
    if not cluster:
        raise HTTPException(404, "planet not found")
    base = cluster["slug"].split("-")[0]
    resources = list(db.resources.find({"category": base})
                     .sort("bookmark_count", -1).limit(10))
    for r in resources:
        r["id"] = str(r.pop("_id"))
    trend_map = {}
    for d in db.resources.find({"category": base}, {"week": 1}):
        trend_map[d["week"]] = trend_map.get(d["week"], 0) + 1
    trend = [{"week": w, "count": n} for w, n in
             sorted(trend_map.items())[-12:]]
    count = db.resources.count_documents({"category": base})
    avg = db.resources.aggregate([
        {"$match": {"category": base}},
        {"$group": {"_id": None, "avg_rt": {"$avg": "$read_time_min"}}}])
    avg_rt = round(next(iter(avg), {}).get("avg_rt", 0) or 0, 1)
    return {"cluster": cluster, "resource_count": count, "avg_read_time": avg_rt,
            "top_resources": resources, "trend": trend}


@router.get("/clusters/stats")
def cluster_stats():
    return list(db.clusters.find({}, {"_id": 0}))


@router.post("/ingest")
def trigger_ingest():
    try:
        new_count = run_rss_ingest(max_per_feed=5)
        return {"status": "success", "new_signals": new_count}
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {str(e)}")
