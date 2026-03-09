from __future__ import annotations

from pydantic import BaseModel, Field

from models.evidence import Evidence
from models.analysis_result import BaselineSnapshot


class BaselineReport(BaseModel):
    title: str = ""
    favicon_hash: str | None = None
    tls_san: list[str] = Field(default_factory=list)

    @classmethod
    def from_baseline(cls, baseline: BaselineSnapshot) -> "BaselineReport":
        return cls(
            title=baseline.http.title,
            favicon_hash=baseline.favicon_hash,
            tls_san=baseline.tls.san,
        )


class ReportItem(BaseModel):
    rank: int
    ip: str
    score: float
    confidence: str
    node_type: str
    sources: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    penalties: list[Evidence] = Field(default_factory=list)
    explanation: list[str] = Field(default_factory=list)


class FinalReport(BaseModel):
    target: str
    baseline: BaselineReport
    candidates: list[ReportItem] = Field(default_factory=list)
    collected_candidates: list[dict] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
