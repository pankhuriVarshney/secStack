"""Live ingestion from security RSS feeds (the 'streaming' source).

New items are categorized by scoring their text against each cluster's
top terms stored in MongoDB, then assigned that cluster. Re-run clustering
after large batches:  python -m scripts.seed_and_cluster --force is NOT
needed; instead run `python -m app.clustering` via:
    python -c "from app.clustering import run_clustering; run_clustering()"

Usage:  python -m scripts.ingest_rss
"""

import datetime as dt
import feedparser

from app.db import db

FEEDS = [
    ("https://krebsonsecurity.com/feed/", "threat-intel"),
    ("https://feeds.feedburner.com/TheHackersNews", "threat-intel"),
    ("https://www.bleepingcomputer.com/feed/", "threat-intel"),
    ("https://www.schneier.com/feed/atom/", "cryptography"),
    ("https://blog.portswigger.net/rss/", "web-security"),
    ("https://aws.amazon.com/blogs/security/feed/", "cloud-security"),
    ("https://isc.sans.edu/rssfeed.xml", "network-security"),
    ("https://www.darkreading.com/rss.xml", "threat-intel"),
]


def categorize(title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    best, best_score = "threat-intel", 0.0
    for c in db.clusters.find({}):
        score = sum(1 for t in c.get("top_terms", []) if t in text)
        if score > best_score:
            best, best_score = c["slug"], score
    return best


def run(max_per_feed: int = 5) -> int:
    inserted = 0
    for url, fallback in FEEDS:
        feed = feedparser.parse(url)
        src = (feed.feed.get("title") or url.split("/")[2]).strip()
        domain = url.split("/")[2].replace("www.", "")
        for e in feed.entries[:max_per_feed]:
            link = e.get("link")
            if not link or db.resources.find_one({"url": link}, {"_id": 1}):
                continue
            title = e.get("title", "untitled").strip()
            summary = getattr(e.get("summary", ""), "strip", lambda: "")() or ""
            day = dt.date.today().isoformat()
            cat_slug = categorize(title, summary)
            db.resources.insert_one({
                "title": title, "url": link, "source": src, "source_domain": domain,
                "author": e.get("author", ""), "summary": summary[:500],
                "category": cat_slug, "media_type": "article",
                "difficulty": "intermediate",
                "tags": [w for w in title.lower().split() if len(w) > 4][:5],
                "published_at": day, "published_day": day,
                "week": dt.date.today().strftime("%G-W%V"),
                "read_time_min": 10, "bookmark_count": 0, "origin": "rss-live",
                "cluster_slug": cat_slug,
            })
            inserted += 1
    print(f"[ingest] inserted {inserted} new resources from {len(FEEDS)} feeds")
    return inserted


if __name__ == "__main__":
    run()