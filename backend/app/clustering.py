"""Spark MLlib clustering: TF-IDF + K-Means over resource text.

Writes:
  db.resources  <- cluster_id, cluster_slug on every doc
  db.clusters   <- one doc per cluster: slug, label, color, size, top_terms
                   (with weights), silhouette_score, centroid, cx/cy/radius
  db.galaxy     <- single doc: { planets: [...], edges: [...] }
"""

from collections import Counter, defaultdict

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from bson import ObjectId   
from app.config import K_CLUSTERS
from app.db import db
from app.seed_data import CATEGORIES, CAT_COLORS, CAT_NAMES

STOP_EXTRA = ["http", "https", "www", "com", "org", "blog", "2024", "2025",
              "2026", "part", "via", "amp", "utm_source"]


import os
import sys

def _spark() -> SparkSession:
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    return (SparkSession.builder
            .appName("secstack-clustering")
            .master("local[*]")
            .config("spark.driver.memory", "2g")
            .config("spark.ui.enabled", "false")
            .getOrCreate())


def run_clustering(verbose: bool = True) -> dict:
    docs = list(db.resources.find({}, {"title": 1, "summary": 1, "tags": 1,
                                       "category": 1}))
    if len(docs) < K_CLUSTERS:
        raise RuntimeError(f"Need >= {K_CLUSTERS} resources, have {len(docs)}. Run the seeder first.")

    spark = _spark()
    try:
        rows = [(str(d["_id"]), d["category"],
                 (d.get("title", "") + " " + d.get("summary", "") + " " +
                  " ".join(d.get("tags", []))).lower()) for d in docs]
        sdf = spark.createDataFrame(rows, ["rid", "seed_category", "text"])

        remover = StopWordsRemover(inputCol="words", outputCol="filtered")
        remover.setStopWords(remover.getStopWords() + STOP_EXTRA)
        pipe = Pipeline(stages=[
            Tokenizer(inputCol="text", outputCol="words"),
            remover,
            HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=8192),
            IDF(inputCol="rawFeatures", outputCol="features"),
            KMeans(featuresCol="features", k=K_CLUSTERS, seed=42, maxIter=25),
        ])
        model = pipe.fit(sdf)
        out = model.transform(sdf)

        sil = float(ClusteringEvaluator(featuresCol="features",
                                        predictionCol="prediction").evaluate(out))

        collected = out.select("rid", "seed_category", "prediction", "filtered").collect()
        sizes, cluster_cats, termfreq = Counter(), defaultdict(Counter), defaultdict(Counter)
        membership = {}
        for r in collected:
            cid = int(r.prediction)
            sizes[cid] += 1
            cluster_cats[cid][r.seed_category] += 1
            membership[r.rid] = cid
            for w in set(r.filtered):
                if len(w) > 2:
                    termfreq[cid][w] += 1

        # cluster -> category label = majority vote of seed categories
        label_of = {cid: cats.most_common(1)[0][0] for cid, cats in cluster_cats.items()}

        clusters, used_slugs = [], set()
        for cid in sorted(sizes):
            slug = label_of[cid]
            if slug in used_slugs:                       # safety: two clusters -> same category
                slug = f"{slug}-{cid}"
            used_slugs.add(slug)
            top = termfreq[cid].most_common(12)
            max_f = top[0][1] if top else 1
            clusters.append({
                "cluster_id": cid, "slug": slug,
                "label": CAT_NAMES.get(label_of[cid], slug),
                "color": CAT_COLORS.get(label_of[cid], "#ffffff"),
                "size": sizes[cid],
                "top_terms": [t for t, _ in top[:6]],
                "top_terms_weighted": [{"term": t, "weight": round(f / max_f, 3)}
                                       for t, f in top[:10]],
                "silhouette_score": round(sil, 4),
            })

        # persist: clusters collection + back-fill resources
        db.clusters.delete_many({})
        db.clusters.insert_many(clusters)
        slug_of = {c["cluster_id"]: c["slug"] for c in clusters}
        for rid, cid in membership.items():
            db.resources.update_one({"_id": ObjectId(rid)},
                                    {"$set": {"cluster_id": cid,
                                              "cluster_slug": slug_of[cid]}})
        galaxy = build_galaxy(clusters)
        db.galaxy.delete_many({})
        db.galaxy.insert_one(galaxy)

        if verbose:
            print(f"[clustering] n={len(docs)} k={K_CLUSTERS} silhouette={sil:.4f}")
            for c in clusters:
                print(f"  cluster {c['cluster_id']:>2} -> {c['label']:<20} "
                      f"n={c['size']:>4} terms={c['top_terms'][:4]}")
        return {"silhouette": sil, "clusters": len(clusters), "documents": len(docs)}
    finally:
        spark.stop()


def build_galaxy(clusters: list[dict]) -> dict:
    """Planet layout: golden-angle spiral sized by canonical category resource count;
    edges by Jaccard similarity of top-term sets."""
    import math
    from app.seed_data import CATEGORIES

    planets = []
    for i, cat in enumerate(CATEGORIES):
        count = db.resources.count_documents({"category": cat["slug"]})
        matched = next((c for c in clusters if c["slug"].startswith(cat["slug"])), {})
        top_terms = matched.get("top_terms", [cat["slug"].replace("-", " "), "security", "telemetry"])

        angle = i * 2.399963229728653
        r = 7.0 * math.sqrt(i + 1)
        cx = 50 + r * math.cos(angle) * 0.9
        cy = 50 + r * math.sin(angle) * 0.62

        planets.append({
            "category_id": i,
            "name": cat["name"],
            "slug": cat["slug"],
            "description": cat["description"],
            "color": cat["color"],
            "resource_count": count,
            "cx": round(cx, 2),
            "cy": round(cy, 2),
            "radius": round(6 + 8 * min(math.log(count + 1), 3), 2),
            "top_terms": top_terms[:5],
        })

    # normalize coords into 0..100
    xs = [p["cx"] for p in planets]; ys = [p["cy"] for p in planets]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1)
    for p in planets:
        p["cx"] = round(10 + (p["cx"] - min(xs)) / span * 80, 2)
        p["cy"] = round(10 + (p["cy"] - min(ys)) / span * 80, 2)

    term_sets = {p["slug"]: set(p["top_terms"]) for p in planets}
    edges = []
    for i, a in enumerate(planets):
        best = []
        for j, b in enumerate(planets):
            if i == j:
                continue
            ta, tb = term_sets[a["slug"]], term_sets[b["slug"]]
            union = ta | tb
            jac = len(ta & tb) / len(union) if union else 0
            if jac > 0:
                best.append({"from": a["slug"], "to": b["slug"],
                             "strength": round(jac, 3)})
        best.sort(key=lambda e: -e["strength"])
        edges.extend(best[:2])
    edges = [e for e in edges if e["strength"] >= 0.02]
    return {"planets": planets, "edges": edges}