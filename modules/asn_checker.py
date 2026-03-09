import socket
from typing import Dict, List

EDGE_KEYWORDS = [
    "cloudflare",
    "akamai",
    "fastly",
    "cloudfront",
    "edgekey",
    "edgesuite",
    "cdn77",
    "incapsula",
    "imperva",
    "stackpath",
]

PUBLIC_CLOUD_KEYWORDS = [
    "amazon",
    "aws",
    "google",
    "gcp",
    "azure",
    "aliyun",
    "alibaba",
    "tencent",
    "huawei",
]

def reverse_dns(ip: str) -> str:
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host.lower()
    except Exception:
        return ""

def _hits(text: str, keywords: List[str]) -> List[str]:
    text = (text or "").lower()
    return [kw for kw in keywords if kw in text]

def analyze_provider(ip: str, headers: dict = None, cert_names: list = None) -> Dict:
    headers = headers or {}
    cert_names = cert_names or []

    rdns = reverse_dns(ip)
    header_blob = " ".join([f"{k}: {v}" for k, v in headers.items()])
    cert_blob = " ".join(cert_names)
    combined = " ".join([rdns, header_blob, cert_blob]).lower()

    edge_hits = _hits(combined, EDGE_KEYWORDS)
    cloud_hits = _hits(combined, PUBLIC_CLOUD_KEYWORDS)

    evidence = []
    infra_score = 0.0
    edge_penalty = 0.0
    label = "unknown_public"

    if edge_hits:
        label = "likely_edge"
        edge_penalty = 18.0
        evidence.append(f"Likely edge/provider traits: {', '.join(sorted(set(edge_hits)))}")
    elif cloud_hits:
        label = "public_cloud"
        edge_penalty = 8.0
        evidence.append(f"Public cloud traits: {', '.join(sorted(set(cloud_hits)))}")
    else:
        label = "unknown_public"
        infra_score = 3.0  # 给未知公网一点轻微区分度

    return {
        "ip": ip,
        "reverse_dns": rdns,
        "label": label,
        "infra_score": infra_score,
        "edge_penalty": edge_penalty,
        "evidence": evidence,
    }