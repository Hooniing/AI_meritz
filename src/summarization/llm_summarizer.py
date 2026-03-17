import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_article(article):
    text = article.raw_text.strip()

    prompt = f"""
다음 보험 관련 기사 본문을 읽고 한국어로 정리해줘.

요구사항:
1. 헤드라인성 요약 2~3문장
2. 보험사 AI 도입 관점의 시사점 1문장
3. 과장 없이 사실 중심
4. 불필요한 메뉴/네비게이션 텍스트는 무시
5. 출력 형식:
SUMMARY: ...
IMPLICATION: ...

기사 본문:
{text[:6000]}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    output = response.output_text.strip()

    summary = output
    implication = ""

    if "IMPLICATION:" in output:
        parts = output.split("IMPLICATION:", 1)
        summary = parts[0].replace("SUMMARY:", "").strip()
        implication = parts[1].strip()
    else:
        summary = output.replace("SUMMARY:", "").strip()

    article.summary = summary
    article.implication = implication or "보험업 내 실제 운영 적용 범위와 확장성을 추가 확인할 필요가 있습니다."
    return article


def build_intro(main_articles):
    joined = "\n\n".join(
        f"[{a.company}] {a.title}\n{a.summary}" for a in main_articles[:10]
    )

    prompt = f"""
다음 주간 보험 AI 기사 요약들을 바탕으로
뉴스레터 서론 5문장을 한국어로 써줘.

조건:
- 국내 보험사 중심
- 이번 주 흐름을 총평하는 문장
- 업무 효율화/자동화/도입 시사점 포함
- 과장 없이 담백하게

자료:
{joined[:12000]}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text.strip()
