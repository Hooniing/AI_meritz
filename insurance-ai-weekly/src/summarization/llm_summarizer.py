def summarize_article(article):
    text = article.raw_text.strip()
    short = text[:280].strip()
    if len(text) > 280:
        short += "..."
    article.summary = f"{short}\n\n핵심은 {article.company} 관련 AI 도입/활용 흐름이 기사 본문에서 확인된다는 점입니다."
    article.implication = "단순 홍보성 언급보다 실제 업무 적용 범위와 운영 효율화 연결 가능성을 확인할 필요가 있습니다."
    return article

def build_intro(main_articles):
    if not main_articles:
        return "이번 주에는 수집된 주요 기사가 충분하지 않았습니다."
    companies = ", ".join(dict.fromkeys([a.company for a in main_articles[:5]]))
    return (
        f"이번 주에는 {companies} 중심으로 보험업 내 AI 도입 및 자동화 관련 흐름이 포착되었습니다.\n"
        "전반적으로 고객상담, 문서 자동화, 심사·보험금 지급 프로세스 고도화와 연결되는 사례가 많았습니다.\n"
        "국내 보험사는 공식 보도자료와 제도권 공시를 통해 실제 적용 방향을 드러내고 있습니다.\n"
        "혁신금융서비스 관련 항목은 제도 기반 실증·확대 신호로 해석할 수 있습니다.\n"
        "해외 사례는 선택적으로 반영해 국내 실무에 참고할 만한 내용만 추렸습니다."
    )
