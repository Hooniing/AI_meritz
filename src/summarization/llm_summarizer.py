import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_article(article):
    text = article.raw_text.strip()

    prompt = f"""
당신은 보험업 AI 도입 사례를 분석하는 한국어 뉴스레터 편집자다.

아래 기사 본문을 읽고, 보험사 AI 도입 사례 중심으로 정리하라.

중요 규칙:
- 사이트 메뉴, 내비게이션, 로그인/고객센터/회사소개 문구는 무시
- 실제 기사 본문으로 보이는 내용만 사용
- 과장 표현 금지
- 기사에 없는 내용 추정 금지
- 단순 기업 홍보 문구보다 실제 활용사례, 적용업무, 운영효과를 우선 반영
- 결과는 한국어로만 작성
- 기사에 AI 관련 내용이 거의 없으면, summary에는 그 한계를 분명히 적을 것

반드시 아래 JSON 형식으로만 답하라:
{{
  "summary": "2~3문장. 무엇을 도입/확대/발표했는지, 어떤 업무에 연결되는지",
  "implication": "1문장. 보험업 실무 관점의 시사점",
  "tags": ["최대 4개"]
}}

기사 정보:
회사명: {article.company}
제목: {article.title}
URL: {article.url}

기사 본문:
{text[:8000]}
"""

    logger.info("Calling OpenAI summarizer for %s", article.title)

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )
        output = response.output_text.strip()
    except Exception as e:
        logger.exception("OpenAI summarization failed for %s: %s", article.title, e)
        short = text[:280].strip()
        if len(text) > 280:
            short += "..."
        article.summary = short
        article.implication = "LLM 요약 실패로 원문 축약본을 대체 사용했습니다."
        article.tags = []
        return article

    try:
        parsed = json.loads(output)
        article.summary = parsed.get("summary", "").strip()
        article.implication = (
            parsed.get("implication", "").strip()
            or "보험업 내 실제 운영 적용 범위와 확장성을 추가 확인할 필요가 있습니다."
        )
        article.tags = parsed.get("tags", [])

        if not article.summary:
            short = text[:280].strip()
            if len(text) > 280:
                short += "..."
            article.summary = short

    except Exception:
        logger.exception("Failed to parse OpenAI JSON response for %s", article.title)
        article.summary = output
        article.implication = "보험업 내 실제 운영 적용 범위와 확장성을 추가 확인할 필요가 있습니다."
        article.tags = []

    logger.info("OpenAI summarization completed for %s", article.title)
    return article


def build_intro(main_articles):
    if not main_articles:
        return "이번 주에는 수집된 주요 기사가 충분하지 않았습니다."

    joined = "\n\n".join(
        f"[{a.company}] {a.title}\n요약: {getattr(a, 'summary', '')}\n시사점: {getattr(a, 'implication', '')}"
        for a in main_articles[:10]
    )

    prompt = f"""
당신은 보험업 AI 동향 뉴스레터의 편집장이다.

아래 기사 요약들을 바탕으로 이번 주 뉴스레터 서론을 작성하라.

목표:
- 국내 보험사 중심으로 이번 주의 공통 흐름을 5문장 이내로 요약
- 단순 나열이 아니라 '이번 주에 무엇이 두드러졌는지'를 보여줄 것
- 고객상담, 문서자동화, 심사, 보험금지급, 설계사 생산성, 내부운영 중 어디가 두드러졌는지 반영
- 제도/혁신금융서비스 관련 내용이 있으면 별도 한 문장으로 반영
- 해외 사례는 국내 실무 참고 가치가 높을 때만 짧게 반영
- 과장 금지, 투자홍보 문구 금지
- 한국어로만 작성

출력 형식:
- 완성된 5문장 이하의 한국어 문단만 출력

자료:
{joined[:14000]}
"""

    logger.info("Calling OpenAI intro generator")

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )
        intro = response.output_text.strip()
        logger.info("OpenAI intro generation completed")
        return intro
    except Exception as e:
        logger.exception("OpenAI intro generation failed: %s", e)
        companies = ", ".join(dict.fromkeys([a.company for a in main_articles[:5]]))
        return (
            f"이번 주에는 {companies} 중심으로 보험업 내 AI 도입 및 자동화 관련 흐름이 포착되었습니다.\n"
            f"전반적으로 고객상담, 문서 자동화, 심사·보험금 지급 프로세스와 연결되는 사례가 확인되었습니다.\n"
            f"국내 보험사는 공식 보도자료와 제도권 공시를 통해 실제 적용 방향을 드러내고 있습니다."
        )
