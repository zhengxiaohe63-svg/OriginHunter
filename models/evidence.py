from __future__ import annotations

from pydantic import BaseModel


class Evidence(BaseModel):
    type: str
    value: str | bool | int | float | None
    weight: float
    reason: str
    confidence: float
