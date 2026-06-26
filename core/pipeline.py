from __future__ import annotations

from models.report import BaselineReport, FinalReport
from core.collector import collect_candidates
from core.analyzer import collect_target_baseline, analyze_candidates
from core.scorer import score_candidates
from core.reporter import print_console_report
from config import AppConfig


def run_pipeline(
    target: str,
    candidates_inline: str | None,
    candidates_file: str | None,
    enable_subdomains: bool,
    enable_historical: bool,
    enable_geo: bool,
    cfg: AppConfig,
    only_collect: bool,
    only_score: bool,
) -> FinalReport:
    if only_score:
        raise SystemExit("--only-score is reserved for a later phase and is not implemented in Phase 1 MVP.")

    baseline = collect_target_baseline(target=target, timeout=cfg.timeout)
    candidates = collect_candidates(
        target=target,
        candidates_inline=candidates_inline,
        candidates_file=candidates_file,
        enable_subdomains=enable_subdomains,
        enable_historical=enable_historical,
        enable_geo=enable_geo,
        cfg=cfg,
    )

    if only_collect:
        report = FinalReport(
            target=target,
            baseline=BaselineReport.from_baseline(baseline),
            candidates=[],
            collected_candidates=[c.model_dump() for c in candidates],
            notes=["Collection-only run; analysis and scoring were skipped."],
        )
        print_console_report(report, top=cfg.top)
        return report

    analyzed = analyze_candidates(target=target, baseline=baseline, candidates=candidates, timeout=cfg.timeout)
    scored = score_candidates(target=target, baseline=baseline, analyzed_results=analyzed)

    report = FinalReport(
        target=target,
        baseline=BaselineReport.from_baseline(baseline),
        candidates=scored,
        collected_candidates=[c.model_dump() for c in candidates],
        notes=[
            "This MVP is intended for local or explicitly authorized lab targets.",
            "Scores indicate candidate priority, not proof of a real backend origin.",
        ],
    )
    print_console_report(report, top=cfg.top)
    return report
