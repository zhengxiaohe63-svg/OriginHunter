from modules.http_fetcher import fetch_candidate_http, fetch_baseline_http
from modules.similarity import (
    text_similarity,
    exact_match_score,
    header_similarity_score,
    content_length_similarity,
    jaccard_san_overlap,
)
from modules.favicon import fetch_favicon_hash
from modules.tls_checker import get_cert_san_names
from modules.asn_checker import analyze_provider
from modules.source_ranker import rank_source_list
from modules.historical_dns import historical_score_for_candidate
from utils.normalize import extract_title, html_to_text, headers_subset

def build_baseline(target_domain: str, timeout: int = 6) -> dict:
    baseline_http = fetch_baseline_http(target_domain, timeout=timeout)

    baseline = {
        "title": "",
        "body_text": "",
        "headers_subset": {},
        "favicon_hash": None,
        "tls_san": [],
        "http_ok": False,
    }

    if baseline_http.get("ok"):
        baseline["http_ok"] = True
        baseline["title"] = extract_title(baseline_http.get("text", ""))
        baseline["body_text"] = html_to_text(baseline_http.get("text", ""))
        baseline["headers_subset"] = headers_subset(baseline_http.get("headers", {}))

        try:
            baseline["favicon_hash"] = fetch_favicon_hash(
                f"https://{target_domain}",
                baseline_http.get("text", ""),
                host=None,
                timeout=timeout,
            )
        except Exception:
            baseline["favicon_hash"] = None

    tls_info = get_cert_san_names(target_domain, sni_host=target_domain, timeout=timeout)
    if tls_info.get("ok"):
        baseline["tls_san"] = tls_info.get("san", [])

    return baseline

def analyze_candidate(target_domain: str, candidate: dict, baseline: dict, timeout: int = 6) -> dict:
    candidate_ip = candidate["ip"]
    sources = candidate.get("sources", [])

    candidate_http = fetch_candidate_http(candidate_ip, target_domain, timeout=timeout)

    result = {
        "candidate": candidate,
        "ip": candidate_ip,
        "evidence": [],
        "scores": {},
        "raw": {},
    }

    # 来源分
    source_score = rank_source_list(sources)
    result["scores"]["source_score"] = source_score
    if source_score > 0:
        result["evidence"].append(f"Source score contributed: {source_score}")

    # 历史分
    hist_score = historical_score_for_candidate(candidate)
    result["scores"]["historical_score"] = hist_score
    if hist_score > 0:
        result["evidence"].append(f"Historical duration score contributed: {hist_score}")

    # 默认分数
    title_score = 0.0
    body_score = 0.0
    header_score = 0.0
    content_len_score = 0.0
    favicon_score = 0.0
    tls_score = 0.0

    result["raw"]["http_fetch"] = candidate_http

    # HTTP 内容证据
    if candidate_http.get("ok"):
        candidate_title = extract_title(candidate_http.get("text", ""))
        candidate_text = html_to_text(candidate_http.get("text", ""))
        candidate_headers = headers_subset(candidate_http.get("headers", {}))

        baseline_title = baseline.get("title", "")
        baseline_text = baseline.get("body_text", "")
        baseline_headers = baseline.get("headers_subset", {})

        title_sim = exact_match_score(baseline_title, candidate_title)
        body_sim = text_similarity(baseline_text, candidate_text)
        hdr_sim = header_similarity_score(baseline_headers, candidate_headers)
        len_sim = content_length_similarity(baseline_text, candidate_text)

        title_score = 10.0 * title_sim
        body_score = 25.0 * body_sim
        header_score = 8.0 * hdr_sim
        content_len_score = 6.0 * len_sim

        if title_score > 0:
            result["evidence"].append("Title matched target")

        if body_sim >= 0.8:
            result["evidence"].append("High body similarity with target")
        elif body_sim >= 0.5:
            result["evidence"].append("Medium body similarity with target")

        if header_score > 0:
            result["evidence"].append("Header similarity with target")

        if content_len_score >= 4:
            result["evidence"].append("Similar content length to target")

        result["raw"]["candidate_title"] = candidate_title
        result["raw"]["candidate_body_len"] = len(candidate_text)
        result["raw"]["candidate_headers_subset"] = candidate_headers
    else:
        result["evidence"].append("HTTP fetch failed or timed out")
        result["raw"]["candidate_title"] = ""
        result["raw"]["candidate_body_len"] = 0
        result["raw"]["candidate_headers_subset"] = {}

    # favicon
    try:
        candidate_favicon = fetch_favicon_hash(
            f"http://{candidate_ip}",
            candidate_http.get("text", ""),
            host=target_domain,
            timeout=timeout,
        )
        if baseline.get("favicon_hash") and candidate_favicon and baseline["favicon_hash"] == candidate_favicon:
            favicon_score = 15.0
            result["evidence"].append("Favicon matched")
        result["raw"]["candidate_favicon_hash"] = candidate_favicon
    except Exception:
        result["raw"]["candidate_favicon_hash"] = None

    # TLS
    tls_info = get_cert_san_names(candidate_ip, sni_host=target_domain, timeout=timeout)
    candidate_san = tls_info.get("san", []) if tls_info.get("ok") else []
    baseline_san = baseline.get("tls_san", [])

    overlap = jaccard_san_overlap(baseline_san, candidate_san)
    tls_score = 15.0 * overlap
    if overlap > 0:
        result["evidence"].append("Candidate certificate SAN overlaps target SAN set")

    result["raw"]["candidate_tls_san"] = candidate_san

    # 基础设施 / 负向证据
    provider = analyze_provider(
        candidate_ip,
        headers=result["raw"]["candidate_headers_subset"],
        cert_names=candidate_san,
    )
    result["raw"]["provider"] = provider
    result["scores"]["infrastructure_score"] = provider.get("infra_score", 0.0)
    result["scores"]["edge_penalty"] = provider.get("edge_penalty", 0.0)

    for ev in provider.get("evidence", []):
        result["evidence"].append(ev)

    # 汇总原始分项
    result["scores"]["title_score"] = round(title_score, 2)
    result["scores"]["body_score"] = round(body_score, 2)
    result["scores"]["header_score"] = round(header_score, 2)
    result["scores"]["content_length_score"] = round(content_len_score, 2)
    result["scores"]["favicon_score"] = round(favicon_score, 2)
    result["scores"]["tls_score"] = round(tls_score, 2)

    return result