from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Article:
    source_name: str
    source_type: str
    company: str
    country: str
    category: str
    title: str
    url: str
    published_at: str
    collected_at: str
    raw_text: str
    tags: List[str] = field(default_factory=list)
    score: float = 0.0
    summary: Optional[str] = None
    implication: Optional[str] = None
    duplicate_group: Optional[str] = None
    selected_main: bool = False

@dataclass
class NewsletterIssue:
    title: str
    issue_date: str
    period_start: str
    period_end: str
    intro_summary: str
    main_articles: List[Article]
    extra_articles: List[Article]
