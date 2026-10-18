from datetime import datetime, timezone
from fastapi import APIRouter

from app.db import db
from app.models import BookmarkSync

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.post("/sync")
def sync(body: BookmarkSync):
    """Merge-join client bookmarks with server copy (server keeps newest saved_at)."""
    existing = {b["resource_id"]: b for b in
                db.bookmarks.find({"client_id": body.client_id})}
    now = datetime.now(timezone.utc).isoformat()
    for b in body.bookmarks:
        cur = existing.get(b.resource_id)
        incoming_time = b.saved_at or now
        if cur is None or (cur.get("saved_at") or "") <= incoming_time:
            db.bookmarks.update_one(
                {"client_id": body.client_id, "resource_id": b.resource_id},
                {"$set": {"resource_id": b.resource_id, "note": b.note,
                          "saved_at": incoming_time, "client_id": body.client_id}},
                upsert=True)
    merged = list(db.bookmarks.find({"client_id": body.client_id}))
    return {"bookmarks": [{**{k: v for k, v in m.items() if k != "_id"}}
                          for m in merged]}


@router.get("/{client_id}")
def get_bookmarks(client_id: str):
    return {"bookmarks": [{k: v for k, v in m.items() if k != "_id"}
                          for m in db.bookmarks.find({"client_id": client_id})]}