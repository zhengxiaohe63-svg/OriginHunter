from __future__ import annotations

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    ip: str
    domain: str
    sources: list[str] = Field(default_factory=list)
    first_seen: str | None = None
    last_seen: str | None = None
    tags: list[str] = Field(default_factory=list)
