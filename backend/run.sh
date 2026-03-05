#!/bin/bash
# backend/run.sh

echo "========================================="
echo "🚀 AI-Doc Advisor FastAPI 서버를 시작합니다"
echo "========================================="

# uv 환경에서 uvicorn 실행 (코드 변경 시 자동 재시작 옵션 포함)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload