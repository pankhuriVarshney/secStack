from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.agent import orchestrator, challenges, registry

router = APIRouter(prefix="/agent", tags=["agent"])


class CtfRoomIn(BaseModel):
    challenge_name: str
    description: str
    difficulty: str = "intermediate"
    category: str = "web-security"
    selected_tools: list[str]
    expose_target_ui: bool = False


class TaskFlagSubmitIn(BaseModel):
    client_id: str
    run_id: str
    task_index: int | None = None   # optional: server matches the flag to a task
    flag: str


@router.post("/ctf-room")
def create_ctf_room(body: CtfRoomIn):
    if not body.challenge_name.strip():
        raise HTTPException(422, "challenge name required")
    try:
        result = orchestrator.generate_ctf_room(
            challenge_name=body.challenge_name.strip(),
            description=body.description.strip(),
            difficulty=body.difficulty,
            category=body.category,
            selected_tool_names=body.selected_tools,
            expose_target_ui=body.expose_target_ui,
        )
    except Exception as e:
        raise HTTPException(500, f"CTF Room generation failed: {str(e)}")
    if result.get("refused"):
        raise HTTPException(422, result.get("reason", "Request refused by the safety guard"))
    return result


@router.get("/score/{client_id}")
def get_score(client_id: str):
    return {"client_id": client_id, "score": orchestrator.get_client_score(client_id)}


@router.post("/submit-task-flag")
def submit_task_flag(body: TaskFlagSubmitIn):
    return orchestrator.submit_task_flag(body.client_id, body.run_id, body.flag, body.task_index)


@router.get("/hints/{run_id}/{hint_index}")
def get_hint(run_id: str, hint_index: int, client_id: str = "default-client"):
    res = orchestrator.unlock_hint(client_id, run_id, hint_index)
    if not res.get("success"):
        raise HTTPException(400, res.get("message", "Failed to unlock hint"))
    return res


@router.get("/leaderboard")
def leaderboard(client_id: str | None = None):
    return {"leaderboard": orchestrator.get_leaderboard(client_id)}


@router.get("/runs")
def runs(limit: int = 20):
    return {"runs": orchestrator.list_room_runs(limit)}


@router.get("/runs/{run_id}")
def run_detail(run_id: str, client_id: str | None = None):
    doc = orchestrator.get_public_run(run_id, client_id)
    if not doc:
        raise HTTPException(404, "run not found")
    return doc


@router.get("/runs/{run_id}/download")
def download_run(run_id: str):
    """A single docker-compose.yml can't run this lab on its own -- the target is
    *built* from a Dockerfile + app code, not pulled. This ships the whole
    workspace (Dockerfile, app/flag files, compose, README) as a zip."""
    zpath = orchestrator.get_workspace_zip(run_id)
    if not zpath:
        raise HTTPException(404, "run not found or has no downloadable workspace")
    return FileResponse(zpath, filename=f"secstack-{run_id[:8]}.zip", media_type="application/zip")


@router.delete("/runs/{run_id}")
def delete_run(run_id: str):
    success = orchestrator.delete_room_run(run_id)
    if not success:
        raise HTTPException(404, "run not found")
    return {"status": "deleted", "run_id": run_id}


@router.get("/harness/manifest")
def harness_manifest():
    return {
        "tool_groups": challenges.KALI_TOOLS,
        "archetypes": {k: {"title": v["title"], "purpose": v["purpose"]}
                       for k, v in challenges.ARCHETYPES.items()},
        "agent_registry": registry.AGENT_REGISTRY,
        "security_layers": ["Layer-1: Deterministic regex/keyword veto",
                            "Layer-2: LLM safety judge (when LLM_API_KEY is configured)"],
    }