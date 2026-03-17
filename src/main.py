import logging
from pathlib import Path

from src.collect.official_insurer import collect_from_source
from src.collect.sandbox import collect_sandbox
from src.delivery.archive_writer import write_issue_archive
from src.delivery.gmail_sender import send_newsletter_email
from src.models import NewsletterIssue
from src.processing.cleaner import clean_text
from src.processing.scorer import score_article
from src.processing.selector import select_main_and_extra
from src.render.email_renderer import render_email_html
from src.render.web_renderer import render_web_html
from src.summarization.llm_summarizer import summarize_article, build_intro
from src.utils.config import load_settings, load_sources, load_scoring
from src.utils.dates import get_last_week_range
from src.utils.logger import setup_logging


def main(send: bool = False):
    setup_logging()
    logger = logging.getLogger(__name__)

    settings = load_settings()
    sources = load_sources()
    scoring = load_scoring()

    period_start, period_end, issue_date = get_last_week_range()
    logger.info("Collecting articles for %s ~ %s", period_start, period_end)

    articles = []

    for source in sources:
        if not source.get("enabled", False):
            continue

        try:
            if source["source_type"] == "sandbox":
                items = collect_sandbox(
                    source,
                    period_start,
                    period_end,
                    settings["min_article_length"],
                )
            else:
                items = collect_from_source(
                    source,
                    period_start,
                    period_end,
                    settings["min_article_length"],
                )

            logger.info("Collected %s items from %s", len(items), source["company"])
            articles.extend(items)

        except Exception as e:
            logger.exception("Failed source %s: %s", source["company"], e)

    # 정제
    for a in articles:
        a.raw_text = clean_text(a.raw_text)

    # 스코어링
    for a in articles:
        a.score = score_article(a, scoring)

    # 점수순 정렬
    articles = sorted(articles, key=lambda x: x.score, reverse=True)

    # 최대 후보 수 제한
    max_candidates = settings.get("max_candidates", 30)
    articles = articles[:max_candidates]

    # 먼저 메인/추가 기사 분리
    main_articles, extra_articles = select_main_and_extra(
        articles,
        settings["main_article_count"],
        settings["extra_article_count"],
        scoring["caps"],
    )

    logger.info(
        "Selected %s main articles and %s extra articles",
        len(main_articles),
        len(extra_articles),
    )

    # 메인 10건만 LLM 요약
    for a in main_articles:
        summarize_article(a)

    # 추가 20건은 표용이므로 summary/implication 비움
    for a in extra_articles:
        if not getattr(a, "summary", None):
            a.summary = ""
        if not getattr(a, "implication", None):
            a.implication = ""
        if not getattr(a, "tags", None):
            a.tags = []

    intro_summary = build_intro(main_articles)

    issue = NewsletterIssue(
        issue_date=issue_date,
        period_start=period_start,
        period_end=period_end,
        intro_summary=intro_summary,
        key_insights=[],
        main_articles=main_articles,
        extra_articles=extra_articles,
        email_html_path="",
        web_html_path="",
    )

    archive_dir = Path("data/archive") / str(issue_date)
    archive_dir.mkdir(parents=True, exist_ok=True)

    email_html = render_email_html(issue)
    web_html = render_web_html(issue)

    email_html_path = archive_dir / "newsletter_email.html"
    web_html_path = archive_dir / "newsletter_web.html"

    email_html_path.write_text(email_html, encoding="utf-8")
    web_html_path.write_text(web_html, encoding="utf-8")

    issue.email_html_path = str(email_html_path)
    issue.web_html_path = str(web_html_path)

    logger.info("Generated newsletter: %s", email_html_path)
    logger.info("Generated newsletter web view: %s", web_html_path)

    write_issue_archive(issue, archive_dir)

    if send:
        send_newsletter_email(issue, email_html)
        logger.info("Email sent successfully")
    else:
        logger.info("Dry run completed; email not sent")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args()

    main(send=args.send)
