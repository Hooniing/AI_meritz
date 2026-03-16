from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from datetime import date

from src.collect.http import fetch_html
from src.models import Article
from src.utils.dates import iso_now

DATE_RE = re.compile(r"(20\d{2}[./-]\d{1,2}[./-]\d{1,2})")

def _extract_links(list_url: str):
    html = fetch_html(list_url)
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.select("a[href]"):
        href = a.get("href", "").strip()
        text = " ".join(a.get_text(" ", strip=True).split())
        if not href or len(text) < 8:
            continue
        if href.startswith("javascript:"):
            continue
        full = urljoin(list_url, href)
        links.append((text, full))
    seen = set()
    results = []
    for title, url in links:
        key = (title, url)
        if key in seen:
            continue
        seen.add(key)
        results.append((title, url))
    return results[:50]

def _extract_article_text(url: str) -> str:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")
    for sel in ["article", ".article", ".content", ".contents", "#content", "body"]:
        node = soup.select_one(sel)
        if node:
            return node.get_text("\n", strip=True)[:8000]
    return soup.get_text("\n", strip=True)[:8000]

def collect_from_source(source: dict, start_date: date, end_date: date, min_article_length: int = 80):
    results = []
    links = _extract_links(source["list_url"])
    for title, url in links:
        try:
            text = _extract_article_text(url)
        except Exception:
            continue
        if len(text) < min_article_length:
            continue
        published = None
        m = DATE_RE.search(text) or DATE_RE.search(title)
        if m:
            published = m.group(1).replace(".", "-").replace("/", "-")
        else:
            published = start_date.isoformat()
        try:
            y, mo, d = [int(x) for x in published.split("-")]
            p = date(y, mo, d)
            if not (start_date <= p <= end_date):
                continue
        except Exception:
            pass

        results.append(Article(
            source_name=source["company"],
            source_type=source["source_type"],
            company=source["company"],
            country=source["country"],
            category=source["category"],
            title=title,
            url=url,
            published_at=published,
            collected_at=iso_now(),
            raw_text=text
        ))
    return results
