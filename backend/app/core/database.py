from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings


# 1. DB 엔진 생성 (커넥션 풀 관리)
engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True, # 끊어진 연결을 자동으로 다시 맺어주는 옵션
    pool_size=5,        # 기본 커넥션 풀 크기
    max_overflow=10     # 트래픽이 몰릴 때 추가로 허용할 커넥션 수
)

# 2. 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 모든 ORM 모델이 상속받을 Base 클래스
Base = declarative_base()


# 4. FastAPI 의존성 주입을 위한 제너레이터 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # 요청이 끝나면 반드시 세션을 반환 
