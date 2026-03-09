from collections import defaultdict
from modules.dns_resolver import collect_candidates
from modules.historical_dns import load_historical_dns

def collect_candidate_ips(target_domain: str, subdomains: bool = False, historical_file: str = None):
    raw = []

    dns_result = collect_candidates(target_domain, include_subdomains=subdomains)
    raw.extend(dns_result["candidates"])

    if historical_file:
        raw.extend(load_historical_dns(historical_file, target_domain))

    merged = defaultdict(lambda: {
        "ip": "",
        "sources": [],
        "tags": [],
        "first_seen": None,
        "last_seen": None,
        "duration_days": 0,
    })

    for item in raw:
        ip = item["ip"]
        merged[ip]["ip"] = ip
        merged[ip]["sources"].append(item["source"])

        if item.get("duration_days", 0) > merged[ip]["duration_days"]:
            merged[ip]["duration_days"] = item.get("duration_days", 0)
            merged[ip]["first_seen"] = item.get("first_seen")
            merged[ip]["last_seen"] = item.get("last_seen")

    return list(merged.values())