def classify_node(result: dict) -> str:
    score = result.get("final_score", 0.0)
    scores = result.get("scores", {})

    edge_penalty = scores.get("edge_penalty", 0.0)
    body_score = scores.get("body_score", 0.0)
    hist_score = scores.get("historical_score", 0.0)
    source_score = scores.get("source_score", 0.0)
    header_score = scores.get("header_score", 0.0)
    tls_score = scores.get("tls_score", 0.0)
    favicon_score = scores.get("favicon_score", 0.0)

    if result.get("fetch_error"):
        return "unreachable_node"

    if edge_penalty >= 15:
        return "likely_edge_node"

    if hist_score >= 12 and body_score >= 8:
        return "historical_related_node"

    strong_similarity_hits = 0
    if body_score >= 12:
        strong_similarity_hits += 1
    if header_score >= 6:
        strong_similarity_hits += 1
    if tls_score >= 8:
        strong_similarity_hits += 1
    if favicon_score >= 8:
        strong_similarity_hits += 1

    if score >= 55 and strong_similarity_hits >= 2 and edge_penalty < 10:
        return "high_similarity_service_node"

    if source_score >= 10 or body_score >= 8 or header_score >= 5:
        return "related_service_node"

    return "weakly_related_node"