from pathlib import Path
import json
import sqlite3
from dataclasses import asdict

def ensure_db(db_path: str = "data/newsletter.db"):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            issue_date TEXT,
            title TEXT,
            company TEXT,
            country TEXT,
            url TEXT PRIMARY KEY,
            published_at TEXT,
            score REAL,
            summary TEXT,
            implication TEXT,
            selected_main INTEGER
        )
    """)
    con.commit()
    return con

def save_issue(issue, archive_dir: str):
    Path(archive_dir).mkdir(parents=True, exist_ok=True)
    articles = [asdict(a) for a in issue.main_articles + issue.extra_articles]
    Path(f"{archive_dir}/articles.json").write_text(json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(f"{archive_dir}/summary.json").write_text(json.dumps({
        "title": issue.title,
        "issue_date": issue.issue_date,
        "period_start": issue.period_start,
        "period_end": issue.period_end,
        "intro_summary": issue.intro_summary,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    con = ensure_db()
    cur = con.cursor()
    for a in issue.main_articles + issue.extra_articles:
        cur.execute("""
            INSERT OR REPLACE INTO articles
            (issue_date, title, company, country, url, published_at, score, summary, implication, selected_main)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            issue.issue_date, a.title, a.company, a.country, a.url, a.published_at,
            a.score, a.summary, a.implication, int(a.selected_main)
        ))
    con.commit()
    con.close()
