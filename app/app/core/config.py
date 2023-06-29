from typing import Any, Optional

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "quizar"
    API_V1_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SECRET_KEY: str

    MIN_QUESTIONS_PER_QUIZ: int = 1
    MAX_QUESTIONS_PER_QUIZ: int = 10
    MIN_ANSWER_PER_QUESTION: int = 1
    MAX_ANSWER_PER_QUESTION: int = 5
    MAX_SUBMISSION_PER_QUIZ: int = 1

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        postgres_db = values.get("POSTGRES_DB") or ""
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{postgres_db}",
        )

    class Config:
        case_sensitive = True


settings = Settings()
