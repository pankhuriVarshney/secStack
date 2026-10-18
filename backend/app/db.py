from pymongo import MongoClient, ASCENDING
from app.config import MONGO_URI, DB_NAME

_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
db = _client[DB_NAME]


def ensure_indexes():
    r = db.resources
    r.create_index([("category", ASCENDING), ("published_day", ASCENDING)])
    r.create_index("cluster_id")
    r.create_index("url", unique=True)
    r.create_index([("title", "text"), ("summary", "text"), ("tags", "text")])
    db.bookmarks.create_index([("client_id", ASCENDING), ("resource_id", ASCENDING)], unique=True)
    db.subscribers.create_index("email", unique=True)
    db.newsletters.create_index("week_of", unique=True)
    db.clusters.create_index("slug", unique=True)
    db.agent_runs.create_index("run_id", unique=True)
    db.agent_runs.create_index("created_at")
    # collections actually used by agent/orchestrator.py
    db.client_scores.create_index("client_id", unique=True)
    db.solved_challenges.create_index(
        [("client_id", ASCENDING), ("run_id", ASCENDING), ("task_index", ASCENDING)], unique=True)
    db.unlocked_hints.create_index(
        [("client_id", ASCENDING), ("run_id", ASCENDING), ("hint_index", ASCENDING)], unique=True)