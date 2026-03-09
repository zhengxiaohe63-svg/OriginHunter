from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict

from models.candidate import Candidate
from models.evidence import Evidence
from modules.asn_checker import IPInfrastructureInfo
from modules.fingerprint import PageFingerprint
from modules.http_fetcher import HttpSnapshot
from modules.similarity import SimilarityBundle
from modules.tls_checker import TLSSnapshot


class BaselineSnapshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    target: str
    http: HttpSnapshot
    favicon_hash: str | None = None
    tls: TLSSnapshot
    fingerprint: PageFingerprint


class AnalysisResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    candidate: Candidate
    http_features: HttpSnapshot
    tls_features: TLSSnapshot
    fingerprint: PageFingerprint
    favicon_hash: str | None = None
    similarity: SimilarityBundle
    asn: IPInfrastructureInfo
    evidences: list[Evidence] = Field(default_factory=list)
