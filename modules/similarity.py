from difflib import SequenceMatcher
from typing import List

def text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return round(SequenceMatcher(None, a, b).ratio(), 4)

def exact_match_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return 1.0 if a.strip().lower() == b.strip().lower() else 0.0

def header_similarity_score(target_headers: dict, candidate_headers: dict) -> float:
    keys = ["Server", "X-Powered-By", "Content-Type"]
    matched = 0
    possible = 0

    for k in keys:
        tv = target_headers.get(k)
        cv = candidate_headers.get(k)
        if tv:
            possible += 1
            if str(tv).strip().lower() == str(cv).strip().lower():
                matched += 1

    if possible == 0:
        return 0.0

    return round(matched / possible, 4)

def content_length_similarity(a_text: str, b_text: str) -> float:
    if not a_text or not b_text:
        return 0.0
    la = len(a_text)
    lb = len(b_text)
    if la == 0 or lb == 0:
        return 0.0
    ratio = min(la, lb) / max(la, lb)
    return round(ratio, 4)

def jaccard_san_overlap(a_list: List[str], b_list: List[str]) -> float:
    a = {x.lower() for x in (a_list or [])}
    b = {x.lower() for x in (b_list or [])}
    if not a or not b:
        return 0.0
    return round(len(a & b) / len(a | b), 4)