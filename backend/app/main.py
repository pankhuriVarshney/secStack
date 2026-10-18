import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError

from app.db import ensure_indexes
from app.routers import bookmarks, meta, newsletter, stats, resources, agent, ctf

log = logging.getLogger("secstack")

app = FastAPI(title="SecStack API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # no cookies are used; "*" + credentials is invalid per the CORS spec
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    # Unique indexes (scores, solved flags, hints...) must exist or double-awards become possible.
    try:
        ensure_indexes()
    except PyMongoError as e:
        log.error("Could not reach MongoDB at startup: %s", e)


@app.exception_handler(PyMongoError)
async def mongo_error_handler(request: Request, exc: PyMongoError):
    # Clear 503 instead of a raw 500 + stack trace when MongoDB is down.
    log.error("MongoDB error on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=503, content={"detail": "Database unavailable. Is MongoDB running?"})


@app.get("/")
def root():
    return {"status": "ok"}


app.include_router(meta.router)
app.include_router(resources.router)
app.include_router(bookmarks.router)
app.include_router(newsletter.router)
app.include_router(stats.router)
app.include_router(agent.router)
app.include_router(ctf.router)