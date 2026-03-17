import os
from openai import OpenAI

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

반드시 아래 JSON 형식으로만 답하라:
{{
  "summary": "2~3문장. 무엇을 도입/확대/발표했는지, 어떤 업무에 연결되는지",
  "implication": "1문장. 보험업 실무 관점의 시사점",
  "tags": ["최대 4개", "예: 고객상담", "문서자동화", "보험금심사", "생성형AI"]
}}

기사 정보:
회사명: {article.company}
제목: {article.title}
URL: {article.url}

기사 본문:
{text[:8000]}
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
당신은 보험업 AI 동향 뉴스레터의 편집장이다.

아래 기사 요약들을 바탕으로 이번 주 뉴스레터 서론을 작성하라.

목표:
- 국내 보험사 중심으로 이번 주의 공통 흐름을 5문장 이내로 요약
- 단순 나열이 아니라 '이번 주에 무엇이 두드러졌는지'를 보여줄 것
- 고객상담, 문서자동화, 심사, 보험금지급, 설계사 생산성, 내부운영 중 어디가 두드러졌는지 반영
- 제도/혁신금융서비스 관련 내용이 있으면 별도 한 문장으로 반영
- 해외 사례는 국내 실무 참고 가치가 높을 때만 짧게 반영
- 과장 금지, 투자홍보 문구 금지

출력 형식:
- 완성된 5문장 이하의 한국어 문단만 출력

자료:
{joined[:14000]}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text.strip()
