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
        {"$sort": {"count": -1}}, {"$limit": 20}])
    return [{"domain": d["_id"], "count": d["count"]} for d in cur]