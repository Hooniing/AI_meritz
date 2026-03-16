import re

def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"\s+", "", title)
    title = re.sub(r"[^\w가-힣]", "", title)
    return title

def dedupe_articles(articles):
    seen_urls = set()
    seen_titles = set()
    out = []
    for a in articles:
        if a.url in seen_urls:
            continue
        nt = normalize_title(a.title)
        if nt in seen_titles:
            continue
        seen_urls.add(a.url)
        seen_titles.add(nt)
        out.append(a)
    return out
