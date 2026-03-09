from urllib.parse import urljoin
from bs4 import BeautifulSoup
from modules.http_fetcher import fetch_url
from utils.hashing import sha256_bytes

def find_favicon_url(base_url: str, html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    icon = soup.find("link", rel=lambda x: x and "icon" in str(x).lower())
    if icon and icon.get("href"):
        return urljoin(base_url, icon["href"])
    return urljoin(base_url, "/favicon.ico")

def fetch_favicon_hash(base_url: str, html: str, host: str = None, timeout: int = 6):
    favicon_url = find_favicon_url(base_url, html)
    result = fetch_url(favicon_url, host=host, timeout=timeout, allow_redirects=True)
    if not result.get("ok"):
        return None
    return sha256_bytes(result["content"])