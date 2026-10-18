from __future__ import annotations
from pydantic import BaseModel, Field


class BookmarkIn(BaseModel):
    resource_id: str
    note: str = ""
    saved_at: str | None = None
    client_id: str


class BookmarkSync(BaseModel):
    client_id: str
    bookmarks: list[BookmarkIn] = Field(default_factory=list)


class SubscribeIn(BaseModel):
    email: str