from __future__ import annotations

from models.candidate import Candidate


def collect_geo_candidates(target: str) -> list[Candidate]:
    # Phase 1 MVP intentionally does not call remote geo-resolution services.
    # Future phases can ingest user-supplied resolver snapshots here.
    return []
