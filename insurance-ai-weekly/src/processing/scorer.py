AI_KEYWORDS = ["AI", "인공지능", "생성형 AI", "OCR", "챗봇", "자동심사", "언더라이팅", "보험금", "상담", "음성인식", "문서 자동화"]
INSURANCE_KEYWORDS = ["보험", "보험금", "심사", "청구", "언더라이팅", "고객센터", "상담", "설계사", "문서", "계약"]
STRATEGIC_KEYWORDS = ["혁신금융서비스", "지정", "확대", "출시", "도입", "고도화", "실증", "자동화"]

def score_article(article, scoring_cfg: dict) -> float:
    w = scoring_cfg["weights"]
    title_text = f"{article.title} {article.raw_text[:1500]}"

    source_trust = 30 if article.source_type in {"official_pr", "sandbox", "official_global"} else 20
    ai_relevance = min(w["ai_relevance"], sum(1 for k in AI_KEYWORDS if k.lower() in title_text.lower()) * 5)
    insurance_relevance = min(w["insurance_relevance"], sum(1 for k in INSURANCE_KEYWORDS if k.lower() in title_text.lower()) * 4)
    strategic_importance = min(w["strategic_importance"], sum(1 for k in STRATEGIC_KEYWORDS if k.lower() in title_text.lower()) * 4)

    if article.country == "KR" and article.company != "금융규제샌드박스":
        domestic_priority = 10
    elif article.country == "KR":
        domestic_priority = 7
    else:
        domestic_priority = 3

    article.score = round(source_trust + ai_relevance + insurance_relevance + strategic_importance + domestic_priority, 2)
    return article.score

def sort_and_limit(articles, max_candidates: int):
    return sorted(articles, key=lambda x: x.score, reverse=True)[:max_candidates]
