# Train to Church — Commute Picker (FastAPI)

간단한 설명
- 이 프로젝트는 `FastAPI`로 구현된 작은 백엔드 서비스입니다. `/commute` 엔드포인트로 HTTP GET 요청을 받아 `data/timetable.json`에 정의된 출발 시각을 기반으로 다음 운행 시간을 반환합니다.

요구사항
- Python 3.11+
- 의존성: `fastapi`, `uvicorn` (프로젝트 루트의 `pyproject.toml` 참고)

로컬 실행 방법
1. 가상환경 생성 및 활성화 (권장)

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
\.venv\Scripts\activate      # Windows (PowerShell/CMD)
```

2. 의존성 설치

```bash
# 옵션 A: 간단히 필요한 패키지 설치
python -m pip install "fastapi>=0.121.1" "uvicorn>=0.38.0"

# 옵션 B: 프로젝트 패키지 설치(선호)
python -m pip install -e .
```

3. 서버 실행

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API 사용 예시
- 기본 호출 (서버 시간 사용)

```bash
curl http://127.0.0.1:8000/commute
```

- 특정 시각 기준(예: 07:10)으로 요청

```bash
curl "http://127.0.0.1:8000/commute?now=07:10"
```

예상 응답 예시

```json
{
  "timestamp": "07:10",
  "routes": {
    "route1": {
      "name": "백석→종로3가→둔촌동",
      "next": ["07:19", "07:30", "07:42"]
    },
    "route2": {
      "name": "당산→종합운동장(급행)",
      "next_30": ["07:40", "08:00", "08:20"],
      "next_40": ["07:40", "08:00", "08:20"],
      "next_50": ["07:40", "08:00", "08:20"]
    }
  }
}
```

추가 정보
- API 문서: FastAPI가 제공하는 자동 문서 UI는 `/docs` (Swagger UI)와 `/redoc`에서 확인 가능합니다.
- 데이터 파일 `data/timetable.json`은 코드(`main.py`)에서 상대 경로로 읽어옵니다. 레거시 경로 문제를 피하려면 저장소 루트에서 서버를 실행하세요.

테스트 방법 (수동/간단한 자동화)
- 수동: 위 `curl` 예시로 정상 응답 확인.
- 간단한 자동화(예: `pytest` 없이) — 파이썬 스크립트로 요청 보내기:

```python
import requests
resp = requests.get("http://127.0.0.1:8000/commute?now=07:10")
print(resp.status_code, resp.json())
```

Render에 배포하는 방법 (간단 가이드)
1. 코드를 GitHub에 푸시합니다.
2. Render에서 새 Web Service를 생성:
   - 서비스 종류: Web Service
   - 리포지토리 연결: GitHub 리포지토리 선택
   - 브랜치: 보통 `master` 또는 `main`
   - 빌드 커맨드(선택적): `pip install -r requirements.txt` 또는 `python -m pip install -e .`
   - 시작 커맨드(필수): `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Render가 빌드-배포를 수행하면 공개 URL로 서비스가 올라옵니다. 해당 URL로 `/commute` 요청을 보내면 됩니다.

팁 및 문제해결
- 포트: Render는 환경 변수 `PORT`를 사용합니다. 반드시 시작 커맨드에서 `$PORT`를 사용하세요.
- 종종 의존성 충돌이 발생하면 로컬에서 `pip freeze > requirements.txt`로 고정한 뒤 Render에 올리는 것이 안정적입니다.
- FastAPI의 자동 문서(`/docs`)로 엔드포인트 동작을 빠르게 확인하세요.

라이센스 / 저자
- 간단한 개인용 프로젝트 템플릿입니다. 필요 시 라이센스/저자 정보를 추가하세요.


