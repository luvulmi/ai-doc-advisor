from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Doc Advisor API"
    DATABASE_URL: str

    # .env 파일을 자동으로 읽어오도록 설정
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# 프로젝트 전역에서 사용할 settings 인스턴스
settings = Settings()