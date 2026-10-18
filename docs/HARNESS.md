# SecStack Harness Engineering & Multi-Agent Architecture

## 1. Executive Summary
SecStack incorporates an advanced multi-agent harness engineering layer that transforms unstructured cybersecurity challenges into secure, containerized Docker labs. The architecture bridges the PySpark-clustered MongoDB knowledge base with autonomous LLM agents (powered by Groq `llama-3.3-70b-versatile`) while enforcing strict deterministic safety guardrails.

---

## 2. Multi-Agent Team & Roles (`agents/`)

| Agent Role | Module | Responsibilities & Permissions |
| :--- | :--- | :--- |
| **Planner Agent** | `agents/orchestrator.py` | Deconstructs user challenge descriptions into capability requirements and knowledge base queries. |
| **Researcher Agent** | `agents/orchestrator.py` | Executes RAG retrieval queries over the Spark-clustered MongoDB security corpus (`search_knowledge`). |
| **Architect Agent** | `agents/tools.py` | Selects containerized tools from a strict security whitelist and assembles non-conflicting Docker Compose files. |
| **Compliance Critic** | `agents/security.py` | Performs Layer-2 security review, verifies guardrails, and generates step-by-step penetration testing walkthroughs. |

---

## 3. Harness Engineering Technicalities

### 3.1 MCP-Style Tool Registry (`agents/tools.py`)
Tools are exposed as an in-process MCP (Model Context Protocol) manifest with strict JSON schemas and role-based permissions. The LLM proposes tool invocations, but execution is validated and executed deterministically by Python code.

### 3.2 Model Routing & Circuit Breakers (`agents/model_router.py`)
Manages call budgets per session, fallbacks, and circuit breakers with automatic cooldown periods to ensure high availability and prevent token exhaustion.

### 3.3 Security Harness Layers (`agents/security.py`)
- **Layer-1 (Deterministic Veto):** Regex scanners block prompt injection payloads, privilege escalation flags (`privileged: true`), host networking, and `docker.sock` mounts before reaching the LLM.
- **Layer-2 (Compliance Critic):** AI-powered review of the final lab architecture and automated walkthrough generation.

### 3.4 Hook Pipeline (`agents/hooks.py`)
Provides conversation compaction for long reasoning traces, schema linting, and deterministic repair (enum snapping/clamping) on model outputs.

---

## 4. Observability & REST Endpoints
- `POST /agent/ctf-copilot`: Executes the multi-agent workflow and persists full traces to `db.agent_runs`.
- `GET /agent/runs`: Retrieves historical agent runs.
- `DELETE /agent/runs/{run_id}`: Destroys a generated challenge and frees up system resources.
- `GET /agent/harness/manifest`: Exposes the active MCP tools and agent registry manifest.
