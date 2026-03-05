# AI Doc Advisor

AI 기반 문서 분석 시스템

## 기술 스택

- **PostgreSQL + pgvector**: 벡터 데이터베이스
- **Redis**: LLM 응답 캐싱 및 세션 관리
- **RabbitMQ**: 문서 파싱 및 벡터화 비동기 처리

## 시작하기

### 필수 요구사항

- Docker
- Docker Compose

### 실행 방법

```bash
# 모든 서비스 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### 접속 정보

- **PostgreSQL**: `localhost:5432`
  - 사용자: `admin`
  - 비밀번호: `adminpassword`
  - 데이터베이스: `doc_advisor`

- **Redis**: `localhost:6379`

- **RabbitMQ**:
  - AMQP: `localhost:5672`
  - 관리 UI: `http://localhost:15672`
    - 사용자: `guest`
    - 비밀번호: `guest`

## 라이선스

MIT
