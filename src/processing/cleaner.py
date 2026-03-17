import re

BAD_PATTERNS = [
    r"좌측메뉴 바로가기",
    r"메인메뉴 바로가기",
    r"본문 바로가기",
    r"푸터 바로가기",
    r"로그인",
    r"회원가입",
    r"사이트맵",
    r"개인정보처리방침",
    r"이용약관",
]

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    for p in BAD_PATTERNS:
        text = re.sub(p, " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text
