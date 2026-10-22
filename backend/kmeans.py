# live_sweep.py  (run inside .venv312)
import time
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from app.db import db
from app.clustering import STOP_EXTRA

docs = list(db.resources.find({"origin": "rss-live"},
                              {"title": 1, "summary": 1, "tags": 1, "category": 1}))
rows = [(str(d["_id"]), d["category"],
         (d.get("title", "") + " " + d.get("summary", "") + " " +
          " ".join(d.get("tags", []))).lower()) for d in docs]
print(f"live corpus n={len(docs)}")   # expect ~40

spark = (SparkSession.builder.master("local[*]").appName("secstack-live-sweep")
         .config("spark.driver.memory", "2g").getOrCreate())

for k in [2, 3, 4, 5, 6, 8]:
    if k >= len(rows):
        continue
    t0 = time.time()
    remover = StopWordsRemover(inputCol="words", outputCol="filtered")
    remover.setStopWords(remover.getStopWords() + STOP_EXTRA)
    pipe = Pipeline(stages=[
        Tokenizer(inputCol="text", outputCol="words"), remover,
        HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=8192),
        IDF(inputCol="rawFeatures", outputCol="features"),
        KMeans(featuresCol="features", k=k, seed=42, maxIter=25)])
    sdf = spark.createDataFrame(rows, ["rid", "seed_category", "text"])
    model = pipe.fit(sdf)
    out = model.transform(sdf)
    sil = float(ClusteringEvaluator(featuresCol="features",
                                    predictionCol="prediction").evaluate(out))
    sizes = [r["count"] for r in out.groupBy("prediction").count().orderBy("prediction").collect()]
    print(f"k={k} silhouette={sil:.4f} runtime={round(time.time()-t0,1)}s sizes={sizes}", flush=True)
spark.stop()