"""Live ingestion from security RSS feeds (the 'streaming' source).

New items are categorized by scoring their text against each cluster's
top terms stored in MongoDB, then assigned that cluster. Re-run clustering
after large batches:
    python -c "from app.clustering import run_clustering; run_clustering()"

Usage:  python -m scripts.ingest_rss
"""

import datetime as dt
import feedparser

from app.db import db

FEEDS = [
    ("https://krebsonsecurity.com/feed/", "threat-intel", "Krebs on Security", "krebsonsecurity.com"),
    ("https://feeds.feedburner.com/TheHackersNews", "threat-intel", "The Hacker News", "thehackernews.com"),
    ("https://www.bleepingcomputer.com/feed/", "threat-intel", "BleepingComputer", "bleepingcomputer.com"),
    ("https://www.schneier.com/feed/atom/", "cryptography", "Schneier on Security", "schneier.com"),
    ("https://portswigger.net/research/rss", "web-security", "PortSwigger Research", "portswigger.net"),
    ("https://aws.amazon.com/blogs/security/feed/", "cloud-security", "AWS Security Blog", "aws.amazon.com"),
    ("https://isc.sans.edu/rssfeed.xml", "network-security", "SANS Internet Storm Center", "isc.sans.edu"),
    ("https://www.darkreading.com/rss.xml", "threat-intel", "Dark Reading", "darkreading.com"),
    ("https://www.securityweek.com/feed/", "threat-intel", "SecurityWeek", "securityweek.com"),
    ("https://feeds.feedburner.com/GoogleOnlineSecurityBlog", "cloud-security", "Google Online Security Blog", "google.com"),
    ("https://www.microsoft.com/en-us/security/blog/feed/", "enterprise-security", "Microsoft Security Blog", "microsoft.com"),
    ("https://blog.talosintelligence.com/feed/", "threat-intel", "Cisco Talos Intelligence", "talosintelligence.com"),
    ("https://unit42.paloaltonetworks.com/feed/", "threat-intel", "Palo Alto Networks Unit 42", "paloaltonetworks.com"),
    ("https://www.sentinelone.com/labs/feed/", "malware-analysis", "SentinelOne Labs", "sentinelone.com"),
    ("https://www.crowdstrike.com/blog/feed/", "threat-intel", "CrowdStrike Blog", "crowdstrike.com"),
    ("https://blog.rapid7.com/rss/", "vulnerability-management", "Rapid7 Blog", "rapid7.com"),
    ("https://therecord.media/feed", "threat-intel", "The Record by Recorded Future", "therecord.media"),
    ("https://www.malwarebytes.com/blog/feed/", "malware-analysis", "Malwarebytes Labs", "malwarebytes.com"),
    ("https://www.tripwire.com/state-of-security/feed/", "enterprise-security", "Tripwire State of Security", "tripwire.com"),
    ("https://blog.qualys.com/feed/", "vulnerability-management", "Qualys Security Blog", "qualys.com"),
    ("https://www.cisa.gov/cybersecurity-advisories/all.xml", "vulnerability-management", "CISA Advisories", "cisa.gov"),
    ("https://www.helpnetsecurity.com/feed/", "threat-intel", "Help Net Security", "helpnetsecurity.com"),
    ("https://www.welivesecurity.com/feed/", "malware-analysis", "ESET WeLiveSecurity", "welivesecurity.com"),
    ("https://redcanary.com/blog/feed/", "red-canary", "Red Canary Blog", "redcanary.com"),
    ("https://www.troyhunt.com/rss/", "web-security", "Troy Hunt Blog", "troyhunt.com"),
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
    total_inserted = 0
    now_iso = dt.datetime.utcnow().isoformat()
    day = dt.date.today().isoformat()

    for url, fallback_cat, pub_name, domain in FEEDS:
        inserted_for_feed = 0
        status = "healthy"
        error_msg = None
        try:
            feed = feedparser.parse(url)
            src = (feed.feed.get("title") or pub_name).strip()
            entries = feed.entries
            if not entries and not feed.get("feed", {}).get("title"):
                raise ValueError("Empty feed or parse error")
            
            for e in entries[:max_per_feed]:
                link = e.get("link")
                if not link or db.resources.find_one({"url": link}, {"_id": 1}):
                    continue
                title = e.get("title", "untitled").strip()
                summary = getattr(e.get("summary", ""), "strip", lambda: "")() or ""
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
                inserted_for_feed += 1
                total_inserted += 1
        except Exception as exc:
            status = "failing"
            error_msg = str(exc)
            print(f"[ingest error] {pub_name} ({url}): {exc}")

        db.publisher_health.update_one(
            {"domain": domain},
            {
                "$set": {
                    "name": pub_name,
                    "domain": domain,
                    "url": url,
                    "fallback_category": fallback_cat,
                    "status": status,
                    "last_fetched_at": now_iso,
                    "error": error_msg,
                },
                "$inc": {"articles_ingested": inserted_for_feed}
            },
            upsert=True
        )

    print(f"[ingest] inserted {total_inserted} new resources across {len(FEEDS)} feeds")
    return total_inserted


if __name__ == "__main__":
    run()
