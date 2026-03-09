from modules.node_classifier import classify_node


def compute_final_score(result: dict) -> float:
    s = result["scores"]

    similarity_total = (
        s.get("title_score", 0.0)
        + s.get("body_score", 0.0)
        + s.get("header_score", 0.0)
        + s.get("content_length_score", 0.0)
        + s.get("favicon_score", 0.0)
        + s.get("tls_score", 0.0)
    )

    context_total = (
        s.get("source_score", 0.0)
        + s.get("historical_score", 0.0)
        + s.get("infrastructure_score", 0.0)
    )

    total = similarity_total + context_total - s.get("edge_penalty", 0.0)

    result["similarity_score"] = round(similarity_total, 2)
    result["context_score"] = round(context_total, 2)
    result["final_score"] = round(total, 2)

    if total >= 70:
        result["confidence"] = "high"
    elif total >= 45:
        result["confidence"] = "medium"
    else:
        result["confidence"] = "low"

    result["evidence_confidence"] = result["confidence"]

    edge_penalty = s.get("edge_penalty", 0.0)
    if edge_penalty >= 15:
        result["edge_risk"] = "high"
    elif edge_penalty >= 8:
        result["edge_risk"] = "medium"
    else:
        result["edge_risk"] = "low"

    result["node_type"] = classify_node(result)
    result["assessment_note"] = (
        "High scores indicate stronger similarity to the target service profile. "
        "They do not confirm origin/backend identity."
    )
    return result["final_score"]


def compute_tie_break_score(result: dict) -> float:
    s = result["scores"]
    candidate = result.get("candidate", {})
    sources = candidate.get("sources", [])

    tie = 0.0
    tie += s.get("source_score", 0.0) * 1.2
    tie += s.get("historical_score", 0.0) * 1.5
    tie += s.get("body_score", 0.0) * 1.1
    tie += s.get("header_score", 0.0) * 0.9
    tie += s.get("tls_score", 0.0) * 0.8
    tie -= s.get("edge_penalty", 0.0) * 1.3

    source_blob = " ".join(sources).lower()
    for kw in ["api", "app", "service", "node", "legacy", "history"]:
        if kw in source_blob:
            tie += 2.0

    result["tie_break_score"] = round(tie, 2)
    return result["tie_break_score"]


def _build_cluster_key(result: dict):
    s = result.get("scores", {})
    body_bucket = int(s.get("body_score", 0.0) // 4)
    header_bucket = int(s.get("header_score", 0.0) // 4)
    tls_bucket = int(s.get("tls_score", 0.0) // 4)
    favicon_bucket = 1 if s.get("favicon_score", 0.0) > 0 else 0
    node_type = result.get("node_type", "unknown")
    return (
        node_type,
        body_bucket,
        header_bucket,
        tls_bucket,
        favicon_bucket,
    )


def _assign_clusters(results: list) -> list:
    clusters = {}
    ordered_cluster_keys = []

    for result in results:
        key = _build_cluster_key(result)
        if key not in clusters:
            clusters[key] = {
                "cluster_id": len(clusters) + 1,
                "members": [],
            }
            ordered_cluster_keys.append(key)

        clusters[key]["members"].append(result)

    cluster_summaries = []

    for key in ordered_cluster_keys:
        cluster = clusters[key]
        members = cluster["members"]
        cluster_id = cluster["cluster_id"]

        for item in members:
            item["cluster_id"] = cluster_id

        cluster_summaries.append(
            {
                "cluster_id": cluster_id,
                "node_type": members[0].get("node_type", "unknown"),
                "member_count": len(members),
                "members": [m.get("ip") for m in members],
                "avg_final_score": round(
                    sum(m.get("final_score", 0.0) for m in members) / max(len(members), 1), 2
                ),
                "avg_similarity_score": round(
                    sum(m.get("similarity_score", 0.0) for m in members) / max(len(members), 1), 2
                ),
                "shared_traits": _cluster_traits(members),
            }
        )

    cluster_summaries.sort(
        key=lambda c: (-c.get("avg_final_score", 0.0), -c.get("member_count", 0), c.get("cluster_id", 0))
    )
    return cluster_summaries


def _cluster_traits(members: list) -> list:
    traits = []
    if not members:
        return traits

    first = members[0]
    first_scores = first.get("scores", {})

    if first_scores.get("body_score", 0.0) >= 12:
        traits.append("similar page body")
    if first_scores.get("header_score", 0.0) >= 6:
        traits.append("similar headers")
    if first_scores.get("tls_score", 0.0) >= 8:
        traits.append("similar TLS profile")
    if first_scores.get("favicon_score", 0.0) > 0:
        traits.append("same favicon hash")
    if first_scores.get("historical_score", 0.0) >= 8:
        traits.append("historical linkage signals")

    if not traits:
        traits.append("weak shared signals")

    return traits


def sort_results(results: list) -> list:
    for r in results:
        compute_final_score(r)
        compute_tie_break_score(r)

    results.sort(
        key=lambda r: (
            -r.get("final_score", 0.0),
            -r.get("tie_break_score", 0.0),
            r.get("node_type", ""),
            r.get("ip", "")
        )
    )

    for idx, r in enumerate(results, start=1):
        r["rank"] = idx

    cluster_summaries = _assign_clusters(results)
    for r in results:
        r["cluster_summary"] = next(
            (c for c in cluster_summaries if c["cluster_id"] == r.get("cluster_id")),
            None
        )

    return results