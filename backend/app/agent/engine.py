"""Bounded agent loop: plan -> retrieve -> select -> assemble -> critic.
Every iteration is appended to a trace persisted in MongoDB (db.agent_runs)
so the reasoning is fully observable — screenshot the trace for the report.
"""

import json
import time
import uuid
import datetime as dt

from openai import OpenAI

from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from app.db import db
from app.agent import tools, prompts

_client = (OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
           if LLM_API_KEY and LLM_BASE_URL else None)


def _llm_json(system: str, user: str, max_retries: int = 2) -> dict | None:
    """JSON-mode LLM call with bounded self-correction on malformed output."""
    if _client is None:
        return None
    for attempt in range(max_retries + 1):
        try:
            resp = _client.chat.completions.create(
                model=LLM_MODEL, temperature=0.2, max_tokens=900,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}])
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            last = e
    print(f"[agent] LLM failed after {max_retries + 1} tries: {last}")
    return None


def _offline_plan(challenge: str) -> dict:
    """Deterministic fallback so the demo never depends on network/API keys."""
    text = challenge.lower()
    caps = sorted({cap for k, names in tools.CAPABILITY_HINTS.items()
                   if k in text for cap in names})
    cats = sorted({p for k, names in tools.CAPABILITY_HINTS.items() if k in text
                   for n in names for p in tools.WHITELIST
                   if p["name"] == n for p_ in [p] for p in p_["planets"]})
    if not cats:
        cats, caps = ["tools-labs"], ["kali"]
    return {"challenge_summary": challenge[:120],
            "capabilities_needed": caps or ["kali"],
            "relevant_categories": cats[:3],
            "search_queries": [text.split()[0] if text else "ctf"]}


def run_ctf_copilot(challenge: str, max_iterations: int = 3) -> dict:
    trace: list[dict] = []
    t0 = time.time()

    # -- 1. PLAN ---------------------------------------------------------
    plan = _llm_json(prompts.PLANNER_SYS, f"Challenge: {challenge}") \
           or _offline_plan(challenge)
    plan.setdefault("relevant_categories", ["tools-labs"])
    plan.setdefault("search_queries", [challenge[:60]])
    trace.append({"step": "plan", "output": plan})

    # -- 2. RETRIEVE (tool: knowledge base = Spark clusters in Mongo) -----
    evidence: dict[str, list[dict]] = {}
    citations: list[dict] = []
    for cat in plan["relevant_categories"][:3]:
        hits = tools.search_knowledge(plan["search_queries"][0], cat)
        evidence[cat] = hits
        citations.extend({"title": h["title"], "url": h["url"]} for h in hits[:2])
    trace.append({"step": "retrieve", "output":
                  {k: len(v) for k, v in evidence.items()}})

    # -- 3. SELECT tools (whitelisted) ------------------------------------
    whitelist_txt = json.dumps([{k: w[k] for k in ("name", "purpose", "planets")}
                                for w in tools.WHITELIST])
    sel = _llm_json(prompts.SELECTOR_SYS,
                    f"Plan: {json.dumps(plan)}\nWhitelist: {whitelist_txt}")
    names = (sel or {}).get("selected_tools") or []
    if not names:  # keyword fallback
        flat = " ".join(plan.get("capabilities_needed", [])).lower()
        names = [n for k, ns in tools.CAPABILITY_HINTS.items() if k in flat
                 for n in ns][:3] or ["kali"]
    images = tools.validate_image_selection(names)
    trace.append({"step": "select", "output":
                  {"requested": names, "validated": [w["name"] for w in images]}})

    # -- 4. ASSEMBLE (constrained generation: code builds, LLM doesn't) ---
    compose_yaml, warnings = tools.build_compose(images, challenge)
    commands = [w["command"] for w in images]
    trace.append({"step": "assemble", "output":
                  {"services": [w["name"] for w in images], "warnings": warnings}})

    # -- 5. CRITIC loop with bounded self-correction ----------------------
    final_issues: list[str] = []
    for i in range(max_iterations):
        ok, issues = tools.critic_check(compose_yaml)
        trace.append({"step": f"critic[{i + 1}]", "output":
                      {"passed": ok, "issues": issues}})
        if ok:
            break
        final_issues = issues
        doc = yaml_safe(compose_yaml)
        bad = {s for s, why in
               ((i_.split("'")[1], i_) for i_ in issues if "'" in i_)
               if s in (doc.get("services") or {})}
        for b in bad:
            doc["services"].pop(b, None)
            images = [w for w in images if w["name"] != b]
        compose_yaml = yaml.safe_dump(doc, sort_keys=False) if doc.get("services") else compose_yaml

    # -- 6. PERSIST trace (observability) ---------------------------------
    answer = {
        "challenge": challenge,
        "summary": plan.get("challenge_summary", challenge),
        "categories": plan["relevant_categories"],
        "tools": [{"name": w["name"], "image": w["image"], "purpose": w["purpose"],
                   "command": w["command"]} for w in images],
        "compose_yaml": compose_yaml,
        "warnings": warnings,
        "safety": {"passed": not final_issues and bool(images),
                   "guardrails": ["no privileged mode", "no host networking",
                                  "no docker.sock", "whitelist-only images",
                                  "read-only rootfs where possible",
                                  "resource caps (1g / 256 pids)"]},
        "citations": citations[:8],
        "evidence_counts": {k: len(v) for k, v in evidence.items()},
        "duration_s": round(time.time() - t0, 2),
        "llm_enabled": _client is not None,
    }
    run = {"run_id": str(uuid.uuid4()), "created_at": dt.datetime.utcnow().isoformat(),
           "type": "ctf_copilot", "trace": trace, "answer": answer}
    db.agent_runs.insert_one(run)
    return {"run_id": run["run_id"], "trace": trace, "answer": answer}


def generate_walkthrough(challenge: str, tools_list: list[str]) -> str:
    if _client is None:
        return f"### Step-by-Step Walkthrough for: {challenge}\n\n1. **Reconnaissance:** Spin up the lab environment and use `nmap` or `kali` to scan the target.\n2. **Enumeration:** Probe endpoints using `{', '.join(tools_list)}` to identify parameters or vulnerabilities.\n3. **Exploitation / Resolution:** Apply targeted methodology or hardening steps as outlined in the Spark knowledge base."
    
    prompt = f"Create a clear, professional penetration testing walkthrough and solution guide for the following CTF challenge using tools ({', '.join(tools_list)}):\n\nChallenge: {challenge}\n\nProvide structured markdown instructions (Reconnaissance, Enumeration, Exploitation/Fix)."
    try:
        resp = _client.chat.completions.create(
            model=LLM_MODEL, temperature=0.3, max_tokens=1200,
            messages=[{"role": "system", "content": "You are an expert security mentor and CTF author. Provide clear, educational penetration testing walkthroughs."},
                      {"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except Exception as e:
        return f"Walkthrough generation error: {str(e)}"


def yaml_safe(text: str) -> dict:
    import yaml
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return {}


def get_run(run_id: str) -> dict | None:
    doc = db.agent_runs.find_one({"run_id": run_id}, {"_id": 0})
    return doc


def list_runs(limit: int = 20) -> list[dict]:
    return list(db.agent_runs.find({}, {"_id": 0, "answer": 0})
                .sort("created_at", -1).limit(limit))
