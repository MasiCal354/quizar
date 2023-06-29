from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.schemas.common import IntervalStr
from pydantic import BaseModel


class QuizBase(BaseModel):
    pass


class QuizCreate(QuizBase):
    title: str
    resumable: bool = False
    description: Optional[str] = None
    duration: Optional[IntervalStr] = None


class QuizUpdate(QuizBase):
    title: Optional[str] = None
    resumable: Optional[bool] = None
    description: Optional[str] = None
    duration: Optional[IntervalStr] = None


class Quiz(QuizBase):
    id: Optional[UUID] = None
    author_id: Optional[UUID] = None
    title: Optional[str] = None
    published: Optional[bool] = None
    resumable: Optional[bool] = None
    description: Optional[str] = None
    duration: Optional[timedelta] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class QuizInDB(Quiz):
    pass
