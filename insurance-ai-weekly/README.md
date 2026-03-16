# Insurance AI Weekly MVP

주간 보험 AI 뉴스레터를 생성하고 HTML 이메일로 발송하는 Python MVP입니다.

## 기능
- 국내 메이저 보험사 공식 보도자료 / 혁신금융서비스 / 선택적 해외 소스 수집
- 전주 월요일~일요일 기준 기사 수집
- 최대 30건 후보 선별 후, 스코어링으로 메인 10건 + 추가 20건 선정
- 이메일용 HTML / 웹용 HTML 동시 생성
- SMTP 이메일 발송
- SQLite 아카이브 저장
- GitHub Actions 주간 스케줄링

## 빠른 시작
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m src.main --dry-run
```

## 실행 옵션
```bash
python -m src.main --dry-run
python -m src.main --send
python -m src.main --issue-date 2026-03-16 --dry-run
```

## 네가 해야 하는 것
1. `config/sources.yaml`에서 비어 있는 보험사 보도자료 URL/selector 채우기
2. `.env` 또는 GitHub Secrets에 SMTP 값 넣기
3. 먼저 `--dry-run`으로 HTML 생성 확인
4. 테스트 발송 후 GitHub Actions 활성화

## 필수 환경변수
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASS
- NEWSLETTER_TO
- NEWSLETTER_FROM (선택)
- OPENAI_API_KEY (선택: 없으면 규칙기반 요약 사용)

## 출력물
- `data/archive/YYYY-MM-DD/newsletter_email.html`
- `data/archive/YYYY-MM-DD/newsletter_web.html`
- `data/archive/YYYY-MM-DD/articles.json`
- `data/archive/YYYY-MM-DD/summary.json`

## 참고
- 이메일용 HTML은 정적 링크 중심입니다.
- 웹용 HTML에서만 링크 복사 버튼이 활성화됩니다.
- 사이트 구조가 달라 source 설정/selector 튜닝은 추가 보강이 필요할 수 있습니다.
