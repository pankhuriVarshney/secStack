"""Unified Enterprise CTF Matrix Orchestrator for SecStack.

Real, flag-bearing labs: the LLM (if configured) only picks an archetype;
app/agent/challenges.py deterministically builds the Dockerfile, app code
and flag.txt, so the walkthrough always matches what's actually deployed.
"""

import hmac
import json
import shutil
import time
import uuid
import datetime as dt
from pathlib import Path

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.config import AGENT_WORKSPACE
from app.db import db
from app.agent import llm_client, prompts, guard, challenges

DIFFICULTY_POINTS = {"beginner": 50, "intermediate": 100, "advanced": 200, "expert": 350}
HINT_COST_FRACTION = challenges.HINT_FRACTION  # 0.25 of base points, per hint

ARCHETYPES_FLAT: list[str] = list(challenges.ARCHETYPES.keys())
ALL_KALI_PACKAGES = {p for group in challenges.KALI_TOOLS.values() for p in group}


def _public_answer(answer: dict) -> dict:
    """Strip everything secret before anything reaches the browser:
    task flags, and `files`, whose contents (app.py / flag.txt) embed the flag."""
    out = {k: v for k, v in answer.items() if k != "files"}
    out["tasks"] = [{k: v for k, v in t.items() if k != "flag"} for t in answer.get("tasks", [])]
    return out


def public_run(doc: dict, client_id: str | None = None) -> dict:
    out = {k: v for k, v in doc.items() if k != "answer"}
    out["answer"] = _public_answer(doc.get("answer", {}))
    if client_id:
        out["solved_tasks"] = solved_tasks(client_id, doc["run_id"])
    return out


def solved_tasks(client_id: str, run_id: str) -> list[int]:
    return sorted(d["task_index"] for d in
                  db.solved_challenges.find({"client_id": client_id, "run_id": run_id},
                                            {"task_index": 1}))


def _plan_archetype(challenge_name: str, description: str) -> str | None:
    """Ask the LLM which archetype fits best; None if unavailable or malformed."""
    if not llm_client.LLM_API_KEY:
        return None
    try:
        out = llm_client.call_llm(prompts.PLANNER_SYS,
                                  f"Challenge name: {challenge_name}\nDescription: {description}")
        choice = (out or {}).get("archetype") if isinstance(out, dict) else None
        return choice if choice in challenges.ARCHETYPES else None
    except Exception:
        return None  # challenges.pick_archetype() falls back to keyword matching

def generate_ctf_room(challenge_name: str, description: str, difficulty: str, category: str,
                      selected_tool_names: list[str],
                      expose_target_ui: bool = False) -> dict:
    t0 = time.time()

    passed, reason = guard.check(description + " " + challenge_name, selected_tool_names)
    if not passed:
        return {"refused": True, "reason": reason}

    llm_choice = _plan_archetype(challenge_name, description)
    archetype_key = challenges.pick_archetype(challenge_name + " " + description,
                                              selected_tool_names, llm_choice)
    arch = challenges.ARCHETYPES[archetype_key]

    points = DIFFICULTY_POINTS.get(difficulty, 100)
    flag = challenges.make_flag(archetype_key)
    files = challenges.build_challenge_files(archetype_key, flag)

    run_id = str(uuid.uuid4())
    run_short = run_id[:8]
    compose_yaml, kali_dockerfile = challenges.build_compose_v2(
        selected_tool_names, arch, run_short, archetype_key, flag,
        expose_target_ui=expose_target_ui,
    )
    workspace_path = challenges.write_workspace(
        AGENT_WORKSPACE, run_id, files, compose_yaml, kali_dockerfile,
        port=arch.get("port"), expose_target_ui=expose_target_ui,
    )

    port = arch.get("port")
    target_access = (f"http://127.0.0.1:{port[0]}" if (port and expose_target_ui) else None)
    setup_commands = [
        "docker compose up --build -d",
        "docker compose exec kali bash",
        f"# From the Kali box, reach the target at hostname: target{(' : ' + port[1]) if port else ''}",
    ]
    if target_access:
        setup_commands.append(f"# Optional browser UI (loopback only): {target_access}")

    task = {
        "id": 1,
        "name": arch["title"],
        "desc": arch["scenario"],
        "points": points,
        "flag": flag,
    }

    answer = {
        "challenge_id": run_short,
        "challenge_name": challenge_name,
        "difficulty": difficulty,
        "points": points,
        "archetype": archetype_key,
        "archetype_title": arch["title"],
        "purpose": arch["purpose"],
        "description": description,
        "target_hostname": "target",
        "target_access": target_access,
        "setup_commands": setup_commands,
        "kali_packages": challenges._resolve_kali_packages(selected_tool_names, archetype_key),
        "compose_yaml": compose_yaml,
        "files": files,  # stripped by _public_answer before reaching the client
        "tasks": [task],
        "walkthrough": arch["walkthrough"],
        "hints": arch["hints"],
        "warnings": [],
        "refused": False,
        "duration_s": round(time.time() - t0, 2),
    }

    run_doc = {
        "run_id": run_id,
        "created_at": dt.datetime.utcnow().isoformat(),
        "type": "ctf_room",
        "challenge_name": challenge_name,
        "workspace_path": workspace_path,
        "answer": answer,
        "trace": [
            {"step": "plan", "output": {"archetype": archetype_key, "llm_chose": bool(llm_choice)}},
            {"step": "build", "output": {"files": list(files.keys())}},
        ],
    }
    db.agent_runs.insert_one(run_doc)
    return {"run_id": run_id, "answer": _public_answer(answer)}


def get_workspace_zip(run_id: str) -> str | None:
    """Rebuild the workspace from the stored (authoritative) files/compose and
    zip it. The flag is NOT part of this rebuild -- it lives only in the
    target image's build arg, which the archive's docker-compose.yml carries."""
    run = get_room_run(run_id)
    if not run:
        return None
    answer = run.get("answer", {})
    files = answer.get("files")
    compose = answer.get("compose_yaml")
    archetype_key = answer.get("archetype")
    if not files or not compose or not archetype_key:
        return None
    flag = next((t.get("flag") for t in answer.get("tasks", []) if t.get("flag")), None)
    if not flag:
        return None
    port = challenges.ARCHETYPES.get(archetype_key, {}).get("port")
    kali_pkgs = answer.get("kali_packages") or []
    kali_dockerfile = challenges.build_kali_dockerfile(kali_pkgs or ["nmap", "netcat-traditional"])
    workspace_path = challenges.write_workspace(
        AGENT_WORKSPACE, run_id, files, compose, kali_dockerfile,
        port=port, expose_target_ui=bool(answer.get("target_access")),
    )
    archive = shutil.make_archive(workspace_path, "zip", root_dir=workspace_path)
    return archive

def get_room_run(run_id: str) -> dict | None:
    """Raw run INCLUDING flags and file contents -- server-side use only."""
    return db.agent_runs.find_one({"run_id": run_id}, {"_id": 0})


def get_public_run(run_id: str, client_id: str | None = None) -> dict | None:
    doc = get_room_run(run_id)
    return public_run(doc, client_id) if doc else None


def list_room_runs(limit: int = 20) -> list[dict]:
    cur = (db.agent_runs.find({"type": "ctf_room"},
                              {"_id": 0, "run_id": 1, "created_at": 1,
                               "answer.challenge_name": 1, "answer.difficulty": 1,
                               "answer.points": 1, "answer.archetype_title": 1})
           .sort("created_at", -1).limit(limit))
    return [{"run_id": d["run_id"], "created_at": d.get("created_at"),
             "challenge_name": d.get("answer", {}).get("challenge_name", d["run_id"]),
             "archetype_title": d.get("answer", {}).get("archetype_title"),
             "difficulty": d.get("answer", {}).get("difficulty"),
             "points": d.get("answer", {}).get("points")} for d in cur]


def delete_room_run(run_id: str) -> bool:
    doc = db.agent_runs.find_one({"run_id": run_id}, {"workspace_path": 1})
    res = db.agent_runs.delete_one({"run_id": run_id})
    if doc and doc.get("workspace_path"):
        shutil.rmtree(doc["workspace_path"], ignore_errors=True)
        zpath = doc["workspace_path"] + ".zip"
        Path(zpath).unlink(missing_ok=True)
    return res.deleted_count > 0


def get_client_score(client_id: str) -> int:
    doc = db.client_scores.find_one({"client_id": client_id})
    return doc.get("score", 0) if doc else 0


def add_client_score(client_id: str, pts: int) -> int:
    doc = db.client_scores.find_one_and_update(
        {"client_id": client_id}, {"$inc": {"score": pts}},
        upsert=True, return_document=ReturnDocument.AFTER)
    return doc["score"]


def get_leaderboard(me: str | None = None) -> list[dict]:
    """Never expose raw client ids: they double as the user's identity key."""
    rows = db.client_scores.find({}, {"_id": 0}).sort("score", -1).limit(5)
    return [{"name": r["client_id"][:8], "score": r.get("score", 0),
             "is_me": bool(me) and r["client_id"] == me} for r in rows]


def submit_task_flag(client_id: str, run_id: str, submitted_flag: str,
                     task_index: int | None = None) -> dict:
    run = get_room_run(run_id)
    if not run:
        return {"success": False, "message": "Room not found"}
    tasks = run.get("answer", {}).get("tasks", [])
    submitted = submitted_flag.strip()

    if task_index is None:
        task_index = next((i for i, t in enumerate(tasks)
                           if hmac.compare_digest(str(t.get("flag", "")), submitted)), None)
        if task_index is None:
            return {"success": False, "message": "Incorrect flag"}
    elif task_index < 0 or task_index >= len(tasks):
        return {"success": False, "message": "Invalid task"}
    elif not hmac.compare_digest(str(tasks[task_index].get("flag", "")), submitted):
        return {"success": False, "message": "Incorrect flag"}

    task = tasks[task_index]
    try:
        db.solved_challenges.insert_one({"client_id": client_id, "run_id": run_id,
                                         "task_index": task_index,
                                         "solved_at": dt.datetime.utcnow().isoformat()})
    except DuplicateKeyError:
        return {"success": True, "already_solved": True, "task_index": task_index,
                "task": task["name"], "score": get_client_score(client_id),
                "solved_tasks": solved_tasks(client_id, run_id)}

    pts = task.get("points", 25)
    new_score = add_client_score(client_id, pts)
    return {"success": True, "points": pts, "score": new_score, "task_index": task_index,
            "task": task["name"], "solved_tasks": solved_tasks(client_id, run_id)}


def unlock_hint(client_id: str, run_id: str, hint_index: int) -> dict:
    run = get_room_run(run_id)
    if not run:
        return {"success": False, "message": "Room not found"}
    hints = run.get("answer", {}).get("hints", [])
    if hint_index < 0 or hint_index >= len(hints):
        return {"success": False, "message": "Invalid hint"}

    key = {"client_id": client_id, "run_id": run_id, "hint_index": hint_index}
    if db.unlocked_hints.find_one(key):
        return {"success": True, "hint": hints[hint_index], "score": get_client_score(client_id)}

    base_points = run.get("answer", {}).get("points", 100)
    cost = min(round(base_points * HINT_COST_FRACTION), get_client_score(client_id))
    try:
        db.unlocked_hints.insert_one(key)
    except DuplicateKeyError:
        return {"success": True, "hint": hints[hint_index], "score": get_client_score(client_id)}
    new_score = add_client_score(client_id, -cost) if cost else get_client_score(client_id)
    return {"success": True, "hint": hints[hint_index], "score": new_score, "penalty": cost}