# NoticeMate AI

SCNU OSS·AI 해커톤용 MVP 프로젝트입니다. 대학생이 공지사항, 과제 안내문, 대회 제출 안내문을 붙여넣으면 AI가 핵심 요약, 마감일, 준비물, 해야 할 일을 정리해주는 웹서비스입니다.

## 문제 정의

대학생은 학사 공지, 과제 안내, 비교과 프로그램, 해커톤 제출 안내를 여러 채널에서 받습니다. 안내문이 길거나 제출물이 많으면 마감일과 준비물을 놓치기 쉽습니다. NoticeMate AI는 긴 안내문을 실행 가능한 체크리스트로 바꿔 일정 누락을 줄이는 것을 목표로 합니다.

## 주요 기능

- 공지/과제 안내문 입력
- 핵심 요약 자동 생성
- 마감일/일정 추출
- 해야 할 일과 우선순위 정리
- 준비물 및 주의사항 정리
- 최근 분석 기록 브라우저 저장
- API 키가 없어도 동작하는 기본 분석 모드 제공

## 기술 스택

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- AI: OpenAI API 선택 연동, API 키 미설정 시 규칙 기반 fallback
- Open Source: MIT License

## 실행 방법

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# AI 분석을 쓰고 싶을 때만 설정
# Windows PowerShell
$env:OPENAI_API_KEY="본인_API_KEY"
# macOS/Linux
export OPENAI_API_KEY="본인_API_KEY"

python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 폴더 구조

```text
noticemate-ai/
├─ app.py
├─ requirements.txt
├─ templates/
│  └─ index.html
├─ static/
│  ├─ app.js
│  └─ style.css
├─ README.md
├─ LICENSE
└─ .gitignore
```

## 향후 개선 계획

- PDF/이미지 공지 업로드 기능
- Google Calendar / iCal 내보내기
- 팀별 공유 링크 생성
- 순천대학교 공지 페이지 자동 수집 기능
- 모바일 UI 개선

## 팀

- 팀명: code zero
- 팀장: 안유진
- 팀원: 이영민
