# SecStack: Agentic AI & Copilot UI Architecture Documentation

---

## 1. Overview for AI Handover & Developers
This document provides a complete technical roadmap of SecStack's **Agentic AI Layer**, **CTF Copilot UI**, **Backend/Frontend Integration**, and an **Exact File Map** to enable another AI or developer to modify, extend, or maintain the codebase seamlessly.

---

## 2. Agentic AI & Multi-Agent Team Architecture

SecStack implements a **Multi-Agent Harness Engineering** framework where an autonomous team of specialized AI agents collaborates to solve cybersecurity challenges and generate secure Docker lab environments.

### 2.1 The Multi-Agent Team (`backend/app/agent/`)
1. **Planner Agent (`orchestrator.py` & `prompts.py`)**:
   - Deconstructs user-submitted challenge descriptions into capability requirements (`capabilities_needed`), galaxy categories, and knowledge retrieval queries.
2. **Researcher Agent (`orchestrator.py` & `tools.py`)**:
   - Acts as the RAG (Retrieval-Augmented Generation) retrieval engine, querying the PySpark-clustered MongoDB security corpus (`search_knowledge`) to pull relevant advisories, articles, and documentation.
3. **Architect Agent (`tools.py`)**:
   - Performs tool selection against a strict security whitelist and deterministically assembles non-conflicting `docker-compose.yml` lab environments with resource caps, read-only root filesystems, and isolated networks.
4. **Compliance Critic (`security.py` & `orchestrator.py`)**:
   - Enforces Layer-1 deterministic security vetoes (blocking privileged mode, host networking, and `docker.sock` mounts) and generates step-by-step CTF penetration testing solution walkthroughs.

### 2.2 Harness Engineering Infrastructure
- **Model Router (`model_router.py`)**: Manages call budgets per session, circuit breakers with cooldowns, and fallback chains using Groq (`llama-3.3-70b-versatile`).
- **MCP Tool Registry (`tools.py`)**: Exposes tools as an in-process MCP (Model Context Protocol) manifest with strict JSON schemas and role-based permissions.
- **Hook Pipeline (`hooks.py`)**: Handles conversation compaction, schema linting, and deterministic repair (enum snapping/clamping).

---

## 3. Copilot UI Architecture (`/copilot`)

The **CTF Lab Copilot** portal provides an interactive command center for security operators:
- **Challenge Configuration Form**: Inputs for Challenge Name, Description, Category (Galaxy Discipline), and Difficulty Level (Beginner, Intermediate, Advanced, Expert).
- **Execution & Lab Artifacts**: Displays whitelisted tools with command snippets, generated Docker Compose YAML, and an **AI Walkthrough Generator** button.
- **Non-Conflicting Port Guides**: Instructs operators on how to run `docker compose up -d` and access targets (Juice Shop on `3001`, DVWA on `8081`) without conflicting with the Next.js frontend (`3000`) or FastAPI backend (`8000`).
- **Generated Challenges Drawer**: Lists past runs with a **Destroy / Teardown (Trash icon)** button to delete Docker Compose files and free up system resources.
- **Expandable Developer Logs**: Collapsible technical trace viewer displaying multi-agent team steps and security harness verification logs.

---

## 4. Frontend & Backend API Integration

### 4.1 Backend API (`backend/app/`)
- **FastAPI Framework (`main.py`)**: Configured with CORS middleware (`allow_origins=["*"]`) and routers for metadata, resources, bookmarks, newsletter, stats, and **agent**.
- **Agent Router (`routers/agent.py`)**:
  - `POST /agent/ctf-copilot`: Triggers the multi-agent workflow.
  - `POST /agent/walkthrough`: Generates solution guides.
  - `GET /agent/runs` & `GET /agent/runs/{run_id}`: Retrieves historical audit trails.
  - `DELETE /agent/runs/{run_id}`: Deletes generated challenge runs.
  - `GET /agent/harness/manifest`: Exposes MCP tool and agent manifests.

### 4.2 Frontend API Client (`frontend/lib/api.ts`)
- Communicates with FastAPI via `fetchFromApi` using `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).
- Provides asynchronous helper functions (`runCtfCopilot`, `getAgentRuns`, `deleteAgentRun`, `generateWalkthrough`, etc.).

---

## 5. Exact File Map for AI Handover

```
secStack/
├── backend/
│   ├── app/
│   │   ├── agent/                 # Agentic AI Layer
│   │   │   ├── __init__.py
│   │   │   ├── gemini_client.py   # Low-level Groq transport client
│   │   │   ├── model_router.py    # Model routing, budgets, circuit breakers
│   │   │   ├── tools.py           # MCP tool registry & Docker whitelist
│   │   │   ├── registry.py        # Agent roles & handoff rights
│   │   │   ├── hooks.py           # Compaction, linting, deterministic repair
│   │   │   ├── security.py        # Layer-1 deterministic security vetoes
│   │   │   ├── prompts.py         # Versioned system prompts (v2.0-harness)
│   │   │   └── orchestrator.py    # Multi-agent workflow orchestrator
│   │   ├── routers/
│   │   │   ├── agent.py           # FastAPI router for /agent endpoints
│   │   │   ├── bookmarks.py       # Bookmark sync
│   │   │   ├── meta.py            # Galaxy, categories, planets, ingest
│   │   │   ├── newsletter.py      # Weekly digests & subscriptions
│   │   │   ├── resources.py       # Resource search, filters, pagination
│   │   │   └── stats.py           # Analytics timeseries & sources
│   │   ├── clustering.py          # PySpark ML clustering (TF-IDF + KMeans)
│   │   ├── config.py              # Environment configuration
│   │   ├── db.py                  # MongoDB connection & indexes
│   │   ├── main.py                # FastAPI app & CORS setup
│   │   ├── models.py              # Pydantic data models
│   │   └── seed_data.py           # Default security knowledge seed data
│   ├── scripts/                   # RSS ingestion & seeding scripts
│   ├── requirements.txt           # Python dependencies (openai, pyyaml, etc.)
│   └── .env                       # Backend env variables (LLM_API_KEY, MONGO_URI)
├── frontend/
│   ├── app/
│   │   ├── about/, analytics/, copilot/, index/, planet/, saved/, signal/, tracks/ # Next.js App Router
│   │   ├── layout.tsx             # Root layout with suppressHydrationWarning
│   │   └── page.tsx               # Entry page rendering SecStackApp
│   ├── components/
│   │   ├── secstack-app.tsx       # Complete UI component suite (Galaxy, Index, Copilot, Saved, etc.)
│   │   └── ui/                    # Reusable UI primitives
│   ├── lib/
│   │   ├── api.ts                 # Frontend API client communicating with FastAPI
│   │   └── utils.ts               # Utility helpers
│   ├── package.json               # Node dependencies
│   └── .env.local                 # NEXT_PUBLIC_API_URL=http://localhost:8000
├── API.md                         # Complete REST API documentation
├── PROJECT_REPORT.md              # Academic/project report covering Big Data criteria
└── docs/
    ├── AGENTIC_AI_AND_COPILOT.md  # This documentation file
    └── HARNESS.md                 # Harness engineering technical deep-dive
