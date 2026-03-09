import dns.resolver
from typing import Dict, List, Set

COMMON_SUBDOMAINS = [
    "www",
    "origin",
    "direct",
    "api",
    "app",
    "mail",
    "dev",
    "test",
    "staging",
    "admin",
    "backend",
]

def resolve_a_records(hostname: str) -> List[str]:
    ips: Set[str] = set()
    try:
        answers = dns.resolver.resolve(hostname, "A")
        for rdata in answers:
            ips.add(rdata.to_text())
    except Exception:
        pass
    return sorted(list(ips))

def collect_candidates(target_domain: str, include_subdomains: bool = False) -> Dict:
    discovered = []
    seen_pairs: Set[str] = set()

    target_ips = resolve_a_records(target_domain)
    for ip in target_ips:
        key = f"{ip}|target:{target_domain}"
        if key not in seen_pairs:
            discovered.append({
                "ip": ip,
                "source": f"dns_current:target:{target_domain}",
                "evidence_type": "dns_current"
            })
            seen_pairs.add(key)

    if include_subdomains:
        for sub in COMMON_SUBDOMAINS:
            subdomain = f"{sub}.{target_domain}"
            sub_ips = resolve_a_records(subdomain)
            for ip in sub_ips:
                key = f"{ip}|subdomain:{subdomain}"
                if key not in seen_pairs:
                    discovered.append({
                        "ip": ip,
                        "source": f"dns_current:subdomain:{subdomain}",
                        "evidence_type": "dns_current"
                    })
                    seen_pairs.add(key)

    return {
        "target": target_domain,
        "candidates": discovered
    }