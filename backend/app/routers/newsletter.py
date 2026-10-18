import datetime as dt
from fastapi import APIRouter, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db import db
from app.models import SubscribeIn
from app.seed_data import CATEGORIES

router = APIRouter(tags=["newsletter"])


def _week_of(day: dt.date | None = None) -> str:
    return (day or dt.date.today()).strftime("%G-W%V")


def build_newsletter() -> dict:
    """Assemble the current week's digest: top 3 new items per category."""
    start = (dt.date.today() - dt.timedelta(days=6)).isoformat()
    sections = []
    for c in CATEGORIES:
        cur = (db.resources.find({"category": c["slug"],
                                  "published_day": {"$gte": start}})
               .sort([("bookmark_count", -1), ("published_at", -1)]).limit(3))
        items = [{"title": r["title"], "url": r["url"], "summary": r.get("summary", "")}
                 for r in cur]
        if items:
            sections.append({"category": c["slug"], "items": items})
    total = sum(len(s["items"]) for s in sections)
    doc = {
        "subject": f"SecStack Signal // {_week_of()} -- {total} new resources across {len(sections)} sectors",
        "week_of": _week_of(),
        "intro": ("Weekly transmission of the highest-signal cybersecurity resources, "
                  "auto-curated by Spark clustering from this week's ingest."),
        "sections": sections,
    }
    db.newsletters.update_one({"week_of": doc["week_of"]},
                              {"$set": doc}, upsert=True)
    return doc


@router.get("/newsletter/latest")
def latest():
    doc = db.newsletters.find_one(sort=[("week_of", -1)])
    if not doc:
        doc = build_newsletter()
    doc.pop("_id", None)
    return doc


@router.get("/newsletter/archive")
def archive():
    return [{"week_of": d["week_of"], "subject": d.get("subject", "")}
            for d in db.newsletters.find(sort=[("week_of", -1)])]


@router.post("/subscribe")
def subscribe(body: SubscribeIn):
    email = body.email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(422, "invalid email")
    existed = db.subscribers.find_one({"email": email})
    db.subscribers.update_one({"email": email},
                              {"$set": {"email": email,
                                        "subscribed_day": dt.date.today().isoformat()}},
                              upsert=True)
    return {"status": "already-subscribed" if existed else "subscribed"}


_scheduler: BackgroundScheduler | None = None


def start_scheduler():
    global _scheduler
    if _scheduler:
        return
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(build_newsletter, CronTrigger(day_of_week="mon", hour=9),
                       id="weekly_newsletter", replace_existing=True)
    _scheduler.start()