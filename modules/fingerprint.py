from __future__ import annotations

from dataclasses import dataclass, field

from modules.http_fetcher import HttpSnapshot
from utils.normalize import html_to_keywords


@dataclass(slots=True)
class PageFingerprint:
    title: str = ""
    server: str = ""
    x_powered_by: str = ""
    content_type: str = ""
    body_length: int = 0
    keywords: list[str] = field(default_factory=list)
    dom_hint: str = ""


def extract_page_fingerprint(http: HttpSnapshot) -> PageFingerprint:
    headers = http.headers or {}
    body = http.body or ""
    return PageFingerprint(
        title=http.title or "",
        server=headers.get("Server", ""),
        x_powered_by=headers.get("X-Powered-By", ""),
        content_type=headers.get("Content-Type", ""),
        body_length=len(body),
        keywords=html_to_keywords(body, limit=15),
        dom_hint=(body[:200] if body else ""),
    )
