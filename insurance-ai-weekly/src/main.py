import argparse
from pathlib import Path
from datetime import date
from dotenv import load_dotenv

from src.utils.config import load_yaml
from src.utils.logger import get_logger
from src.utils.dates import previous_week_range
from src.collect.official_insurer import collect_from_source
from src.collect.sandbox import collect_sandbox
from src.processing.cleaner import clean_text
from src.processing.dedupe import dedupe_articles
from src.processing.scorer import score_article, sort_and_limit
from src.processing.selector import select_main_and_extra
from src.summarization.llm_summarizer import summarize_article, build_intro
from src.models import NewsletterIssue
from src.render.email_renderer import render_issue
from src.delivery.archive_writer import save_issue
from src.delivery.gmail_sender import send_html_email

load_dotenv()

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--issue-date", type=str, default=None)
    return ap.parse_args()

def main():
    args = parse_args()
    logger = get_logger()

    settings = load_yaml("config/settings.yaml")
    scoring = load_yaml("config/scoring.yaml")
    source_cfg = load_yaml("config/sources.yaml")

    issue_date = date.fromisoformat(args.issue_date) if args.issue_date else date.today()
    period_start, period_end = previous_week_range(issue_date)

    logger.info("Collecting articles for %s ~ %s", period_start, period_end)
    articles = []

    for source in source_cfg["sources"]:
        if not source.get("enabled") or not source.get("list_url"):
            continue
        try:
            if source["source_type"] == "sandbox":
                items = collect_sandbox(source, period_start, period_end, settings["min_article_length"])
            else:
                items = collect_from_source(source, period_start, period_end, settings["min_article_length"])
            logger.info("Collected %s items from %s", len(items), source["company"])
            articles.extend(items)
        except Exception as e:
            logger.exception("Failed source %s: %s", source["company"], e)

    for a in articles:
        a.raw_text = clean_text(a.raw_text)
        score_article(a, scoring)

    articles = dedupe_articles(articles)
    articles = sort_and_limit(articles, settings["max_candidates"])

    for a in articles:
        summarize_article(a)

    main_articles, extra_articles = select_main_and_extra(
        articles,
        settings["main_article_count"],
        settings["extra_article_count"],
        scoring["caps"]
    )

    issue = NewsletterIssue(
        title=settings["newsletter_title"],
        issue_date=issue_date.isoformat(),
        period_start=period_start.isoformat(),
        period_end=period_end.isoformat(),
        intro_summary=build_intro(main_articles),
        main_articles=main_articles,
        extra_articles=extra_articles
    )

    archive_dir = Path("data/archive") / issue.issue_date
    archive_dir.mkdir(parents=True, exist_ok=True)

    email_html_path = archive_dir / "newsletter_email.html"
    web_html_path = archive_dir / "newsletter_web.html"

    email_html = render_issue(issue, "email_newsletter.html.j2", str(email_html_path))
    render_issue(issue, "web_newsletter.html.j2", str(web_html_path))
    save_issue(issue, str(archive_dir))

    logger.info("Generated newsletter: %s", email_html_path)
    logger.info("Generated newsletter web view: %s", web_html_path)

    if args.send:
        subject = f"[보험 AI Weekly] {issue.period_start}–{issue.period_end}"
        send_html_email(subject, email_html)
        logger.info("Email sent successfully")

if __name__ == "__main__":
    main()
