"""Legacy /ctf/* routes -- thin wrappers over the same orchestrator as /agent/*."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.agent import orchestrator
from app.routers.agent import CtfRoomIn, TaskFlagSubmitIn

router = APIRouter(prefix="/ctf", tags=["ctf"])


@router.post("/generate")
def ctf_generate(body: CtfRoomIn):
    result = orchestrator.generate_ctf_room(
        challenge_name=body.challenge_name.strip(),
        description=body.description.strip(),
        difficulty=body.difficulty,
        category=body.category,
        selected_tool_names=body.selected_tools,
    )
    if result.get("refused"):
        raise HTTPException(422, result.get("reason", "Request refused by the safety guard"))
    return result


@router.get("/rooms")
def ctf_rooms(limit: int = 20):
    return {"runs": orchestrator.list_room_runs(limit)}


@router.get("/rooms/{run_id}")
def ctf_room_detail(run_id: str, client_id: str | None = None):
    doc = orchestrator.get_public_run(run_id, client_id)
    if not doc:
        raise HTTPException(404, "room not found")
    return doc


@router.get("/rooms/{run_id}/download")
def ctf_room_download(run_id: str):
    zpath = orchestrator.get_workspace_zip(run_id)
    if not zpath:
        raise HTTPException(404, "room not found or has no downloadable workspace")
    return FileResponse(zpath, filename=f"secstack-{run_id[:8]}.zip", media_type="application/zip")


@router.post("/submit-flag")
def ctf_submit_flag(body: TaskFlagSubmitIn):
    return orchestrator.submit_task_flag(body.client_id, body.run_id, body.flag, body.task_index)