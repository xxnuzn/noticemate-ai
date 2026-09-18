import os
import re
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

try:
    from openai import OpenAI
except Exception:  # openai package is optional at import time
    OpenAI = None

app = Flask(__name__)

SYSTEM_PROMPT = """
너는 대학생 공지/과제 안내문을 분석해주는 한국어 AI 비서다.
사용자가 붙여넣은 텍스트에서 핵심 요약, 마감일/일정, 준비물, 해야 할 일,
위험요소, 캘린더 등록용 문구를 뽑아라. 답변은 반드시 JSON으로만 출력한다.
JSON 스키마: {
  "summary": ["문장"],
  "deadlines": [{"date":"YYYY-MM-DD 또는 원문 날짜", "title":"일정명", "detail":"설명"}],
  "todos": [{"task":"할 일", "priority":"높음/보통/낮음"}],
  "materials": ["준비물"],
  "risks": ["주의할 점"],
  "calendar_text": "캘린더에 복사할 한 문장"
}
""".strip()

DATE_PATTERNS = [
    r"\d{4}[./-]\s*\d{1,2}[./-]\s*\d{1,2}",
    r"\d{1,2}\s*[./]\s*\d{1,2}\s*\(?[월화수목금토일]?\)?",
    r"\d{1,2}월\s*\d{1,2}일",
    r"오늘|내일|모레|이번 주|다음 주|마감|제출|발표|신청",
]


def fallback_analyze(text: str) -> dict:
    """API 키가 없을 때도 데모가 가능하도록 간단한 규칙 기반 분석을 제공한다."""
    clean = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?。])\s+|\n+", text)
    sentences = [s.strip(" -\t") for s in sentences if s.strip()]
    summary = sentences[:3] if sentences else [clean[:120] or "분석할 내용이 부족합니다."]

    dates = []
    for pattern in DATE_PATTERNS:
        for match in re.finditer(pattern, text):
            around = text[max(0, match.start() - 35): match.end() + 45].strip()
            dates.append({"date": match.group(0), "title": "확인 필요 일정", "detail": around})

    keywords = ["제출", "마감", "발표", "신청", "준비", "업로드", "등록", "작성", "확인"]
    todos = []
    for s in sentences:
        if any(k in s for k in keywords):
            todos.append({"task": s[:90], "priority": "높음" if any(k in s for k in ["마감", "제출", "발표"]) else "보통"})
    if not todos:
        todos = [{"task": "공지 내용을 다시 읽고 필요한 제출물과 마감일을 확인하기", "priority": "보통"}]

    materials = []
    for word in ["PPT", "PDF", "파일", "README", "GitHub", "URL", "링크", "신분증", "노트북"]:
        if word.lower() in text.lower():
            materials.append(word)

    risks = []
    if not dates:
        risks.append("명확한 날짜가 자동 추출되지 않았으므로 원문에서 마감일을 직접 확인해야 합니다.")
    if "제출" in text and "링크" not in text and "URL" not in text:
        risks.append("제출 방법 또는 제출 링크가 원문에 명확하지 않을 수 있습니다.")

    return {
        "summary": summary,
        "deadlines": dates[:8],
        "todos": todos[:8],
        "materials": materials or ["원문 공지", "제출 파일"],
        "risks": risks or ["마감 직전 업로드 실패를 피하기 위해 하루 전 테스트가 필요합니다."],
        "calendar_text": f"공지 확인 및 제출 준비: {summary[0][:60]}",
        "mode": "fallback"
    }


def ai_analyze(text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key or OpenAI is None:
        return fallback_analyze(text)

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text[:6000]},
        ],
        temperature=0.2,
    )
    output = getattr(response, "output_text", "").strip()
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        parsed = fallback_analyze(text)
        parsed["raw_ai_output"] = output
    parsed["mode"] = "ai"
    return parsed


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    if len(text) < 10:
        return jsonify({"error": "공지 내용을 10자 이상 입력해주세요."}), 400
    try:
        result = ai_analyze(text)
        result["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        return jsonify(result)
    except Exception as exc:
        fallback = fallback_analyze(text)
        fallback["mode"] = "error-fallback"
        fallback["error"] = str(exc)
        return jsonify(fallback)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
