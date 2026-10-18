import re
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

from app.db import db

router = APIRouter(prefix="/resources", tags=["resources"])
SORTS = {"recent": [("published_at", -1), ("_id", -1)],
         "popular": [("bookmark_count", -1), ("published_at", -1)],
         "read_time": [("read_time_min", -1)]}


def _public(d: dict) -> dict:
    d = dict(d)
    d["id"] = str(d.pop("_id"))
    return d


@router.get("")
def list_resources(category: str | None = None,
                   q: str | None = None,
                   media_type: str | None = None,
                   source: str | None = None,
                   difficulty: str | None = None,
                   sort: str = "recent",
                   page: int = Query(1, ge=1),
                   page_size: int = Query(12, ge=1, le=100)):
    flt = {}
    if category:
        flt["category"] = category
    if media_type:
        flt["media_type"] = media_type
    if difficulty:
        flt["difficulty"] = difficulty
    if source:
        flt["source"] = {"$regex": re.escape(source), "$options": "i"}
    if q:
        flt["$or"] = [{"title": {"$regex": re.escape(q), "$options": "i"}},
                      {"summary": {"$regex": re.escape(q), "$options": "i"}},
                      {"tags": {"$regex": re.escape(q), "$options": "i"}}]
    total = db.resources.count_documents(flt)
    cur = (db.resources.find(flt)
           .sort(SORTS.get(sort, SORTS["recent"]))
           .skip((page - 1) * page_size).limit(page_size))
    return {"items": [_public(d) for d in cur], "total": total,
            "page": page, "pages": max(1, -(-total // page_size))}


@router.get("/{rid}")
def get_resource(rid: str):
    try:
        doc = db.resources.find_one({"_id": ObjectId(rid)})
    except Exception:
        doc = None
    if not doc:
        raise HTTPException(404, "resource not found")
    related = list(db.resources.find(
        {"cluster_id": doc.get("cluster_id"), "_id": {"$ne": doc["_id"]}},
        {"title": 1, "url": 1}).sort("bookmark_count", -1).limit(4))
    return {**_public(doc),
            "related": [{"title": r["title"], "url": r["url"]} for r in related]}