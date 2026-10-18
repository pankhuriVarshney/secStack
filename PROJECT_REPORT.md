# SecStack: A Big Data Knowledge System for Cybersecurity Intelligence

---

## Executive Summary

**SecStack** is an end-to-end big data knowledge management and visualization platform engineered to address the critical information overload faced by cybersecurity professionals, threat intelligence analysts, and students. By combining **Apache Spark (MLlib)** for unsupervised clustering and TF-IDF feature extraction, **FastAPI** for high-performance asynchronous REST APIs, **MongoDB** for flexible document and metadata storage, and a sci-fi/terminal-themed **Next.js & React** frontend with interactive **SVG/CSS data visualizations**, SecStack ingests, structures, clusters, and visualizes thousands of disparate security research resources, documentation guides, threat feeds, and lab environments in real-time.

---

## 1. Problem Identification

### 1.1 The Challenge of Cybersecurity Information Overload
The cybersecurity domain generates an unprecedented volume of unstructured and semi-structured data daily—including vulnerability advisories (CVEs), threat intelligence reports (MITRE ATT&CK), protocol specifications (RFCs), security blogs, exploit write-ups, and certification study guides. Security operators face severe challenges:
- **Fragmentation:** Knowledge is scattered across thousands of disparate source domains (PortSwigger, OWASP, Krebs on Security, AWS Security Blog, GitHub repositories).
- **Lack of Taxonomy:** Traditional bookmarking tools lack semantic understanding, relationship mapping, and automated categorical clustering.
- **High Ingestion Velocity:** Keeping pace with newly published intelligence without automated pipeline filtering is manually unsustainable.

### 1.2 Alignment with Big Data Concepts
SecStack addresses Big Data challenges across the **4 Vs**:
1. **Volume:** Aggregates and indexes hundreds of seed resources and continuously streams live RSS articles from multiple feeds.
2. **Velocity:** Automated background ingestion and on-demand live RSS tuning (`POST /ingest`).
3. **Variety:** Handles diverse data formats (HTML articles, PDF documentation guides, GitHub repos, YouTube video transcripts, and RSS XML feeds).
4. **Veracity:** Employs TF-IDF term weighting and K-Means clustering silhouette scoring to ensure high signal-to-noise ratios.

---

## 2. Tool & Framework Architecture

SecStack utilizes a modern, production-grade technology stack:

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Big Data / ML Engine** | Apache Spark, PySpark (MLlib) | Text tokenization, stop-words removal, HashingTF, IDF, K-Means clustering (`k=8`). |
| **Backend API** | FastAPI, Uvicorn, Pydantic | Asynchronous REST endpoints, CORS middleware, background task scheduling. |
| **Database & Indexing** | MongoDB, PyMongo | Document storage for resources, clusters, galaxy coordinates, and user bookmarks. |
| **Live Ingestion** | Feedparser, Python Requests | Real-time RSS/Atom feed parsing from top security intelligence sources. |
| **Frontend Framework** | Next.js 16, React 19, TypeScript | Server-side rendering, client state management via Zustand. |
| **Visualizations & UI** | SVG, CSS3, Tailwind / Vanilla CSS | Interactive PCA scatter plots, velocity charts, TF-IDF weight meters, and cyber aesthetic shell. |

---

## 3. Data Processing & Analysis Pipeline

### 3.1 Pipeline Architecture
```
[Live RSS Feeds / Seed Data] 
       │
       ▼
[Feedparser & Sanitizer]
       │
       ▼
[MongoDB Storage (resources collection)]
       │
       ▼
[PySpark ML Pipeline]
  ├── Tokenizer (extract words)
  ├── StopWordsRemover (strip noise words)
  ├── HashingTF (term frequency vectorization, numFeatures=8192)
  ├── IDF (inverse document frequency weighting)
  └── KMeans (unsupervised clustering, k=8, maxIter=25)
       │
       ▼
[Clustering Evaluation & Persistence]
  ├── Silhouette Score Calculation
  ├── Majority-Vote Category Labeling
  └── Cluster Centroid & Galaxy Coordinate Layout (Golden Angle Spiral)
```

### 3.2 Core Code Snippet: PySpark ML & Clustering Pipeline (`backend/app/clustering.py`)
```python
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

def run_clustering(verbose: bool = True) -> dict:
    docs = list(db.resources.find({}, {"title": 1, "summary": 1, "tags": 1, "category": 1}))
    spark = SparkSession.builder.appName("secstack-clustering").master("local[*]").getOrCreate()
    try:
        rows = [(str(d["_id"]), d["category"], (d.get("title", "") + " " + d.get("summary", "")).lower()) for d in docs]
        sdf = spark.createDataFrame(rows, ["rid", "seed_category", "text"])

        remover = StopWordsRemover(inputCol="words", outputCol="filtered")
        pipe = Pipeline(stages=[
            Tokenizer(inputCol="text", outputCol="words"),
            remover,
            HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=8192),
            IDF(inputCol="rawFeatures", outputCol="features"),
            KMeans(featuresCol="features", k=8, seed=42, maxIter=25),
        ])
        model = pipe.fit(sdf)
        out = model.transform(sdf)
        sil = float(ClusteringEvaluator(featuresCol="features", predictionCol="prediction").evaluate(out))
        # ... persists clusters and galaxy layout ...
        return {"silhouette": sil, "clusters": 8, "documents": len(docs)}
    finally:
        spark.stop()
```

---

## 4. Visualization & Insights

SecStack fulfills the requirement for clear, meaningful Big Data visualizations using responsive SVG charts and CSS HUD telemetry:

1. **PySpark K-Means Vector Space & PCA Cluster Dispersion (Interactive Scatter Plot):**
   - Visualizes cluster centroids mapped in 2D space, sizing nodes proportional to cluster resource volume with hover tooltips displaying top weighted TF-IDF terms.
2. **Ingestion Velocity Trend Line & Area Chart:**
   - Tracks daily resource ingestion counts over a 14-day window using SVG polylines and gradient area fills.
3. **Top Source Domains Breakdown:**
   - Responsive horizontal progress bars displaying contribution volume across top intelligence feeds (`owasp.org`, `portswigger.net`, `aws.amazon.com`, etc.).
4. **TF-IDF Feature Term Weight Meters:**
   - Visual progress bars within planet command centers representing mathematical feature importance.

---

## 5. Innovation & Real-world Relevance

- **Actionable Intelligence for Operators:** SecStack bridges the gap between raw data collection and actionable learning paths.
- **Structured Markdown Exports:** Security professionals can filter harvested intelligence by category, add custom field notes, and export professional structured markdown reports for team audits.
- **On-Demand Live Tuning:** Users are not restricted to static seed data; they can trigger live RSS ingestion and automated cluster assignment instantly.

---

## 6. Suggested Screenshots for Final Presentation / Report

When compiling your final slide deck or PDF report, capture and include screenshots of the following views:

1. **Figure 1: The Cybersecurity Galaxy (`/`)**
   - *What to capture:* The main interactive galaxy stage with glowing discipline planets, orbital moons, and the focus dock.
2. **Figure 2: Big Data Analytics Telemetry (`/analytics`)**
   - *What to capture:* The analytics dashboard showing the PCA cluster scatter plot, ingestion velocity chart, and top source domain progress bars.
3. **Figure 3: Planetary Command Center (`/planet/web-security`)**
   - *What to capture:* The HUD panel displaying TF-IDF term weights, rotation readouts, and orbital resource cards.
4. **Figure 4: Structured Export & Private Archive (`/saved`)**
   - *What to capture:* The saved signals grid alongside the personal field notes textarea and category export dropdown.
5. **Figure 5: FastAPI Interactive Documentation (`/docs`)**
   - *What to capture:* Swagger UI showing all endpoints (`/galaxy`, `/resources`, `/stats/timeseries`, `/ingest`, `/bookmarks/sync`).

---
*Report generated for SecStack Knowledge System.*
