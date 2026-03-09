# AI Doc Advisor

도커로 띄운 인프라 위에서, FastAPI 백엔드를 개발/실행하는 프로젝트입니다.

## 구성 요소

- **PostgreSQL + pgvector**: 문서 임베딩/검색을 위한 벡터 저장소
- **Redis**: 캐시/세션 등 빠른 KV 저장소(예정)
- **RabbitMQ**: 문서 파싱/벡터화 등 비동기 처리 큐(예정)
- **FastAPI 백엔드**: `backend/` 디렉토리 (Swagger 문서 제공)

## 디렉토리 구조(요약)

- `docker-compose.yml`: 인프라 컨테이너(Postgres/Redis/RabbitMQ)
- `backend/`: FastAPI 서버(로컬 실행 기준)
  - `backend/app/main.py`: 엔트리포인트 (`/docs`, `/health`, `/db-test`)
  - `backend/.env`: 환경변수 예시/로컬 설정(커밋 제외)

## 빠른 시작 (인프라 + 백엔드)

### 1. 인프라 컨테이너 실행

프로젝트 루트에서:

```bash
docker compose up -d
```

구버전 Docker 환경이면:

```bash
docker-compose up -d
```

상태/로그 확인:

```bash
docker compose ps
docker compose logs -f
```

중지/정리:

```bash
docker compose down
```

### 2. 백엔드 실행 (로컬)

필수 요구사항:

- Docker Desktop
- Python 3.12+
- `uv`(권장) 또는 일반 `pip` 환경

`backend/`로 이동 후 실행:

```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### `run.sh`로 실행하기 (WSL/Git Bash)

`backend/run.sh`는 bash 스크립트라서 **Windows PowerShell/CMD에서는 그대로 실행되지 않습니다.**  
대신 **WSL** 또는 **Git Bash**에서 아래처럼 실행하세요.

```bash
cd backend
chmod +x run.sh
./run.sh
```

서버가 뜨면:

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`
- DB 연결 테스트: `http://localhost:8000/db-test`

## 접속 정보 (로컬 기준)

`docker-compose.yml` 기준으로 호스트에서 접근하는 포트는 아래와 같습니다.

- **PostgreSQL**: `localhost:5433` *(로컬 PostgreSQL과의 충돌 방지로 5433 사용, 아래 트러블슈팅 참고)*
  - 사용자: `admin`
  - 비밀번호: `adminpassword`
  - 데이터베이스: `doc_advisor`
- **Redis**: `localhost:6379`
- **RabbitMQ**
  - AMQP: `localhost:5672`
  - 관리 UI: `http://localhost:15672` (기본 계정 `guest` / `guest`)

## 환경 변수

백엔드는 `backend/app/core/config.py`에서 `.env`를 읽습니다.

예시(`backend/.env`):

- `PROJECT_NAME`
- `DATABASE_URL` 예: `postgresql+pg8000://admin:adminpassword@localhost:5433/doc_advisor`

## 개발 메모

- `/docs` 접속 시 요청 로그가 콘솔에 찍히도록 요청 로깅 미들웨어가 포함되어 있습니다.
- GitHub 업로드/브랜치 워크플로우는 `docs/github-workflow.md`를 참고하세요.

## 트러블슈팅

### `/db-test` 엔드포인트 연결 실패

#### 증상 1: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb8`

**원인**: `psycopg2`는 내부적으로 Windows C 라이브러리를 통해 에러 메시지를 가져오는데, **한국어 Windows 환경**에서는 해당 메시지가 CP949(EUC-KR)로 인코딩되어 반환됩니다. `psycopg2`가 이를 UTF-8로 디코딩하려다 실패합니다.

**해결**: DB 드라이버를 순수 Python으로 구현된 `pg8000`으로 교체합니다.

`backend/.env`:
```
DATABASE_URL="postgresql+pg8000://admin:adminpassword@localhost:5433/doc_advisor"
```

---

#### 증상 2: `28P01` / `auth_failed` — 비밀번호 인증 실패

**원인 A — 로컬 PostgreSQL과 포트 충돌**

`localhost:5432`에 Windows 서비스로 설치된 로컬 PostgreSQL이 이미 실행 중이면, Docker 컨테이너보다 먼저 연결을 가로챕니다. 해당 로컬 DB에는 `admin` 계정이 없어 인증에 실패합니다.

포트 점유 상태 확인:
```powershell
netstat -ano | findstr ":5432"
tasklist /fi "PID eq <확인된_PID>"
```
`postgres.exe`가 떠 있다면 로컬 PostgreSQL이 설치된 것입니다.

**해결 (권장)**: Docker 포트를 `5433`으로 변경해 충돌을 회피합니다.

`docker-compose.yml`:
```yaml
ports:
  - "5433:5432"
```

`backend/.env`:
```
DATABASE_URL="postgresql+pg8000://admin:adminpassword@localhost:5433/doc_advisor"
```

**해결 (대안)**: 로컬 PostgreSQL을 다른 프로젝트에서 사용하지 않는다면 서비스를 중지해도 됩니다.
```powershell
Stop-Service postgresql*
```

---

**원인 B — Docker 볼륨에 이전 비밀번호가 남아있는 경우**

PostgreSQL Docker 이미지는 **볼륨이 존재하면 `POSTGRES_PASSWORD` 환경변수를 무시**하고 기존 데이터를 그대로 사용합니다. `docker-compose.yml`에서 비밀번호를 변경해도 반영되지 않습니다.

**해결**: 볼륨을 삭제하고 컨테이너를 재생성합니다. (기존 데이터가 모두 삭제되니 주의)
```bash
docker compose down -v
docker compose up -d db
```

---

#### 증상 3: `.env` 수정 후에도 에러가 지속되는 경우

`uvicorn --reload`는 Python 파일 변경만 감지하며, `.env` 파일 변경은 자동으로 반영되지 않습니다. `.env` 수정 후에는 **서버를 수동으로 재시작**해야 합니다.