import requests

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InsuranceAIWeekly/1.0)"
}

def fetch_html(url: str, timeout: int = 20) -> str:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    return resp.text
