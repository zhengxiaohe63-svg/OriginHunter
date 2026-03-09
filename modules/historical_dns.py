import json
from pathlib import Path
from typing import Dict, List

def load_historical_dns(path: str, target: str) -> List[Dict]:
    """
    Load historical DNS evidence from a local JSON file.

    Example schema:
    {
      "example.com": [
        {
          "domain": "www.example.com",
          "ip": "1.2.3.4",
          "first_seen": "2024-01-01",
          "last_seen": "2024-06-01",
          "duration_days": 150
        }
      ]
    }
    """
    p = Path(path)
    if not p.exists():
        return []

    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get(target, [])
    results = []

    for item in items:
        results.append({
            "ip": item["ip"],
            "source": f"historical_dns:{item.get('domain', target)}",
            "evidence_type": "dns_historical",
            "first_seen": item.get("first_seen"),
            "last_seen": item.get("last_seen"),
            "duration_days": item.get("duration_days", 0),
        })

    return results

def historical_score_for_candidate(candidate: dict) -> float:
    duration = candidate.get("duration_days", 0) or 0

    score = 0.0
    if duration > 0:
        score += 8.0
    if duration >= 30:
        score += 6.0
    if duration >= 90:
        score += 4.0
    if duration >= 180:
        score += 4.0

    return round(score, 2)