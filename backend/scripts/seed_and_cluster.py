"""One-shot: (re)seed the database, then run Spark clustering + galaxy layout.

Usage:
    python -m scripts.seed_and_cluster            # seed only if empty
    python -m scripts.seed_and_cluster --force    # wipe + reseed
"""

import sys
from pymongo import UpdateOne

from app.config import SEED_SIZE
from app.db import db, ensure_indexes
from app.seed_data import build_seed
from app.clustering import run_clustering


def seed(force: bool = False) -> int:
    ensure_indexes()
    if force:
        for col in ("resources", "clusters", "galaxy", "newsletters"):
            db[col].delete_many({})
    if db.resources.estimated_document_count() >= 100 and not force:
        print(f"[seed] already have {db.resources.estimated_document_count()} docs, skipping (use --force)")
        return 0
    items = build_seed(SEED_SIZE)
    ops = [UpdateOne({"url": it["url"]}, {"$set": it}, upsert=True) for it in items]
    db.resources.bulk_write(ops)
    print(f"[seed] upserted {len(items)} resources")
    return len(items)


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
    stats = run_clustering()
    print("[done]", stats)