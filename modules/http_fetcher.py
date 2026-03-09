import re
from typing import Dict, Optional, List

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "close",
}


def _build_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    return session


def _build_headers(host: Optional[str] = None) -> Dict[str, str]:
    headers = BROWSER_HEADERS.copy()
    if host:
        headers["Host"] = host
    return headers


def _looks_like_bad_default_encoding(encoding: Optional[str]) -> bool:
    if not encoding:
        return True
    enc = encoding.lower().strip()
    return enc in {"iso-8859-1", "latin-1", "ascii"}


def _decode_text(resp: requests.Response) -> str:
    try:
        if not _looks_like_bad_default_encoding(resp.encoding):
            text = resp.text
            if text:
                return text
    except Exception:
        pass

    try:
        apparent = getattr(resp, "apparent_encoding", None)
        if apparent:
            resp.encoding = apparent
            text = resp.text
            if text:
                return text
    except Exception:
        pass

    content = resp.content or b""

    for enc in ("utf-8", "gb18030", "gbk", "big5"):
        try:
            text = content.decode(enc, errors="replace")
            if text:
                return text
        except Exception:
            continue

    try:
        return resp.text or ""
    except Exception:
        return ""


def _extract_title(text: str) -> str:
    if not text:
        return ""

    try:
        soup = BeautifulSoup(text, "html.parser")
        if soup.title and soup.title.string:
            return soup.title.string.strip()
    except Exception:
        pass

    try:
        match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
    except Exception:
        pass

    return ""


def _is_meaningful_response(status: int, text: str, content: bytes) -> bool:
    if status not in (200, 401, 403):
        return False
    if text and text.strip():
        return True
    if content and len(content) > 0:
        return True
    return False


def fetch_url(
    url: str,
    host: Optional[str] = None,
    timeout: int = 6,
    allow_redirects: bool = True,
) -> Dict:
    headers = _build_headers(host=host)
    session = _build_session()

    try:
        resp = session.get(
            url,
            headers=headers,
            timeout=(max(2, timeout // 2), timeout),
            verify=False,
            allow_redirects=allow_redirects,
            proxies={"http": None, "https": None},
        )

        text = _decode_text(resp)
        title = _extract_title(text)

        return {
            "ok": True,
            "url": resp.url,
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "text": text,
            "title": title,
            "content": resp.content,
            "content_length": len(resp.content or b""),
            "history": [r.url for r in resp.history],
            "encoding": resp.encoding,
            "apparent_encoding": getattr(resp, "apparent_encoding", None),
            "mode": {
                "url": url,
                "host": host,
                "allow_redirects": allow_redirects,
            },
        }
    except requests.exceptions.TooManyRedirects as e:
        return {"ok": False, "error": f"TooManyRedirects: {e}", "url": url}
    except requests.exceptions.ProxyError as e:
        return {"ok": False, "error": f"ProxyError: {e}", "url": url}
    except requests.exceptions.ConnectTimeout as e:
        return {"ok": False, "error": f"ConnectTimeout: {e}", "url": url}
    except requests.exceptions.ReadTimeout as e:
        return {"ok": False, "error": f"ReadTimeout: {e}", "url": url}
    except requests.exceptions.ConnectionError as e:
        return {"ok": False, "error": f"ConnectionError: {e}", "url": url}
    except Exception as e:
        return {"ok": False, "error": str(e), "url": url}
    finally:
        session.close()


def _normalize_success_result(result: Dict, attempts: List[Dict]) -> Dict:
    result["attempts"] = attempts
    result["text"] = (result.get("text") or "").strip()
    result["title"] = (result.get("title") or "").strip()
    return result


def fetch_candidate_http(ip: str, domain: str, timeout: int = 6) -> Dict:
    attempts: List[Dict] = []

    modes = [
        {"url": f"https://{ip}", "host": domain, "allow_redirects": True, "timeout": timeout},
        {"url": f"http://{ip}", "host": domain, "allow_redirects": True, "timeout": timeout},
        {"url": f"https://{ip}", "host": domain, "allow_redirects": False, "timeout": timeout},
        {"url": f"http://{ip}", "host": domain, "allow_redirects": False, "timeout": timeout},
        {"url": f"https://{ip}", "host": None, "allow_redirects": True, "timeout": timeout},
        {"url": f"http://{ip}", "host": None, "allow_redirects": True, "timeout": timeout},
        {"url": f"https://{ip}", "host": domain, "allow_redirects": True, "timeout": timeout + 3},
        {"url": f"http://{ip}", "host": domain, "allow_redirects": True, "timeout": timeout + 3},
    ]

    for mode in modes:
        r = fetch_url(
            mode["url"],
            host=mode["host"],
            timeout=mode["timeout"],
            allow_redirects=mode["allow_redirects"],
        )
        attempts.append(r)

        if r.get("ok"):
            status = r.get("status_code", 0)
            text = (r.get("text") or "").strip()
            content = r.get("content") or b""

            if _is_meaningful_response(status, text, content):
                return _normalize_success_result(r, attempts)

    return {
        "ok": False,
        "error": "All HTTP/HTTPS fetch strategies failed",
        "attempts": attempts,
    }


def fetch_baseline_http(domain: str, timeout: int = 6) -> Dict:
    attempts: List[Dict] = []

    modes = [
        {"url": f"https://{domain}", "host": None, "allow_redirects": True, "timeout": timeout},
        {"url": f"http://{domain}", "host": None, "allow_redirects": True, "timeout": timeout},
        {"url": f"https://{domain}", "host": None, "allow_redirects": False, "timeout": timeout},
        {"url": f"http://{domain}", "host": None, "allow_redirects": False, "timeout": timeout},
        {"url": f"https://{domain}", "host": None, "allow_redirects": True, "timeout": timeout + 3},
        {"url": f"http://{domain}", "host": None, "allow_redirects": True, "timeout": timeout + 3},
    ]

    for mode in modes:
        r = fetch_url(
            mode["url"],
            host=mode["host"],
            timeout=mode["timeout"],
            allow_redirects=mode["allow_redirects"],
        )
        attempts.append(r)

        if r.get("ok"):
            status = r.get("status_code", 0)
            text = (r.get("text") or "").strip()
            content = r.get("content") or b""

            if _is_meaningful_response(status, text, content):
                return _normalize_success_result(r, attempts)

    return {
        "ok": False,
        "error": "Baseline fetch failed",
        "attempts": attempts,
    }