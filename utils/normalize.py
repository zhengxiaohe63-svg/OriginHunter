import re
from bs4 import BeautifulSoup

def extract_title(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return ""

def html_to_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")

    # remove script/style for cleaner body similarity
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

def headers_subset(headers: dict) -> dict:
    keep = ["Server", "X-Powered-By", "Content-Type", "Location"]
    return {k: str(v) for k, v in headers.items() if k in keep}