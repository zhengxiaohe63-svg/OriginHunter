from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


SAFE_DOMAIN_SUFFIXES = (".local", ".test", ".internal", ".example")
SAFE_EXACT_DOMAINS = ("localhost",)
COMMON_SUBDOMAINS = (
    "www",
    "origin",
    "direct",
    "api",
    "app",
    "mail",
    "dev",
    "test",
    "staging",
)


@dataclass(slots=True)
class AppConfig:
    timeout: int = 5
    top: int = 20
    common_subdomains: Sequence[str] = field(default_factory=lambda: COMMON_SUBDOMAINS)
    safe_domain_suffixes: Sequence[str] = field(default_factory=lambda: SAFE_DOMAIN_SUFFIXES)
    safe_exact_domains: Sequence[str] = field(default_factory=lambda: SAFE_EXACT_DOMAINS)


def is_authorized_target_domain(domain: str, cfg: AppConfig | None = None) -> bool:
    cfg = cfg or AppConfig()
    host = domain.strip().lower()
    return host in cfg.safe_exact_domains or any(host.endswith(sfx) for sfx in cfg.safe_domain_suffixes)
