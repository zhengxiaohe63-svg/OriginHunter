import json
from pathlib import Path


def _collect_clusters(results: list) -> list:
    seen = set()
    clusters = []

    for item in results:
        summary = item.get("cluster_summary")
        if not summary:
            continue
        cluster_id = summary.get("cluster_id")
        if cluster_id in seen:
            continue
        seen.add(cluster_id)
        clusters.append(summary)

    clusters.sort(
        key=lambda c: (-c.get("avg_final_score", 0.0), -c.get("member_count", 0), c.get("cluster_id", 0))
    )
    return clusters


def build_report(target: str, baseline: dict, results: list) -> dict:
    best = results[0] if results else None
    clusters = _collect_clusters(results)

    return {
        "report_type": "service_node_similarity_audit",
        "target": target,
        "baseline": {
            "title": baseline.get("title") or "<title unavailable (dynamic site)>",
            "favicon_hash": baseline.get("favicon_hash"),
            "tls_san": baseline.get("tls_san", []),
        },
        "top_ranked_service_node": best,
        "clusters": clusters,
        "candidates": results,
        "notes": [
            "This report is a service node similarity audit.",
            "High scores indicate stronger similarity to the target service profile, not proof of a backend/origin server.",
            "Tie-breakers and clustering are used to reduce over-interpretation when multiple nodes look alike."
        ]
    }


def print_console_report(target: str, baseline: dict, results: list, top_n: int = 10):
    clusters = _collect_clusters(results)

    print(f"\nTarget: {target}")
    print("\nService Node Similarity Audit")
    print("Note: high scores indicate stronger resemblance to the target service profile.")
    print("Note: this does not confirm origin/backend identity.")

    print("\nBaseline:")
    print(f"  Title: {baseline.get('title') or '<unavailable>'}")
    print(f"  Favicon Hash: {baseline.get('favicon_hash') or '<unavailable>'}")
    print(f"  TLS SAN Count: {len(baseline.get('tls_san', []))}")

    if results:
        best = results[0]
        print("\nTop Ranked Service Node:")
        print(f"  IP: {best['ip']}")
        print(f"  Final Score: {best['final_score']}")
        print(f"  Similarity Score: {best.get('similarity_score', 0.0)}")
        print(f"  Context Score: {best.get('context_score', 0.0)}")
        print(f"  Tie-Break Score: {best.get('tie_break_score', 0.0)}")
        print(f"  Evidence Confidence: {best.get('evidence_confidence', best.get('confidence', 'low'))}")
        print(f"  Edge Risk: {best.get('edge_risk', 'unknown')}")
        print(f"  Service Node Type: {best['node_type']}")
        print(f"  Cluster ID: {best.get('cluster_id', '-')}")
        print(f"  Sources: {', '.join(best['candidate'].get('sources', []))}")
        print("  Why:")
        for reason in best.get("evidence", [])[:8]:
            print(f"    + {reason}")
        print(f"  Assessment: {best.get('assessment_note', '')}")

    if clusters:
        print("\nClusters:")
        for cluster in clusters:
            print("-" * 60)
            print(f"Cluster ID: {cluster['cluster_id']}")
            print(f"Node Type: {cluster['node_type']}")
            print(f"Member Count: {cluster['member_count']}")
            print(f"Average Final Score: {cluster['avg_final_score']}")
            print(f"Average Similarity Score: {cluster['avg_similarity_score']}")
            print(f"Shared Traits: {', '.join(cluster.get('shared_traits', []))}")
            print("Members:")
            for ip in cluster.get("members", []):
                print(f"  - {ip}")

    print("\nTop Candidates:")
    for item in results[:top_n]:
        print("-" * 60)
        print(f"Rank: {item['rank']}")
        print(f"IP: {item['ip']}")
        print(f"Final Score: {item['final_score']}")
        print(f"Similarity Score: {item.get('similarity_score', 0.0)}")
        print(f"Context Score: {item.get('context_score', 0.0)}")
        print(f"Tie-Break Score: {item.get('tie_break_score', 0.0)}")
        print(f"Evidence Confidence: {item.get('evidence_confidence', item.get('confidence', 'low'))}")
        print(f"Edge Risk: {item.get('edge_risk', 'unknown')}")
        print(f"Service Node Type: {item['node_type']}")
        print(f"Cluster ID: {item.get('cluster_id', '-')}")
        print(f"Sources: {', '.join(item['candidate'].get('sources', []))}")
        print("Why:")
        for reason in item.get("evidence", [])[:8]:
            print(f"  + {reason}")
        print(f"Assessment: {item.get('assessment_note', '')}")


def write_json_report(path: str, report: dict):
    Path(path).write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )