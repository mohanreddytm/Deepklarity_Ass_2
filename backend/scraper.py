from typing import Tuple
import requests
from bs4 import BeautifulSoup


def scrape_wikipedia(url: str) -> Tuple[str, str]:
    """
    Returns (title, article_text) for a Wikipedia URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AI-Quiz-Generator/1.0)"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Title
    title_el = soup.find(id="firstHeading")
    title = title_el.get_text(strip=True) if title_el else (soup.title.get_text(strip=True) if soup.title else "Wikipedia Article")

    # Main content
    content_el = soup.find("div", id="mw-content-text")
    paragraphs = []
    if content_el:
        for p in content_el.find_all("p"):
            text = p.get_text(" ", strip=True)
            if text:
                paragraphs.append(text)
    article_text = "\n\n".join(paragraphs)

    # Fallback if extraction fails
    if not article_text:
        article_text = soup.get_text(" ", strip=True)

    return title, article_text

