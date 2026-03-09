from typing import List

HIGH_VALUE_KEYWORDS = [
    "origin",
    "direct",
    "backend",
    "admin",
    "manage",
    "internal",
]

NORMAL_SUBDOMAIN_KEYWORDS = [
    "www",
    "api",
    "app",
    "dev",
    "test",
    "mail",
    "staging",
]

def rank_source_list(sources: List[str]) -> float:
    """
    Higher = more valuable source provenance.
    """
    score = 0.0

    for src in sources:
        s = src.lower()

        if s.startswith("historical_dns:"):
            score += 18.0
        elif s.startswith("geo_dns:"):
            score += 6.0
        elif s.startswith("dns_current:target:"):
            score += 8.0
        elif s.startswith("dns_current:subdomain:"):
            score += 8.0

            if any(k in s for k in HIGH_VALUE_KEYWORDS):
                score += 10.0
            elif any(k in s for k in NORMAL_SUBDOMAIN_KEYWORDS):
                score += 2.0

    # 多来源重复命中
    if len(set(sources)) >= 2:
        score += 8.0
    if len(set(sources)) >= 3:
        score += 4.0

    return round(score, 2)