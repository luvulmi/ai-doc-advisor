import logging
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.database import get_db
from app.core.config import settings

# 로깅 설정 (uvicorn과 같은 포맷으로 콘솔 출력)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class RequestLogMiddleware(BaseHTTPMiddleware):
    """요청마다 메서드/경로를 안내 로그로 출력"""

    async def dispatch(self, request, call_next):
        logger.info("%s %s", request.method, request.scope.get("path", ""))
        response = await call_next(request)
        return response


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="사내 문서 AI 어드바이저 백엔드",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 API 문서 안내 로그"""
    logger.info("========================================")
    logger.info("API 문서 (Swagger): http://localhost:8000/docs")
    logger.info("ReDoc:              http://localhost:8000/redoc")
    logger.info("========================================")


# 요청 로깅은 CORS보다 먼저 등록 (가장 바깥에서 먼저 실행되도록)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "ok",
        "message": "서버 연결 완료.",
    }


@app.get("/db-test", tags=["System"])
async def db_test(db: Session = Depends(get_db)):
    """
    DB 연결 상태를 간단히 확인하는 엔드포인트.
    """
    try:
        # 간단한 쿼리 실행
        result = db.execute(text("SELECT 1")).scalar()
        return {"status": "success", "message": f"DB 연결 완료. (응답: {result})"}
    except Exception as e:
        logger.exception("DB 연결 테스트 실패")
        return {
            "status": "error",
            "message": f"{e.__class__.__name__}: DB 연결 중 오류가 발생했습니다.",
        }
