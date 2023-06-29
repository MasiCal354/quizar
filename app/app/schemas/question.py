from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.schemas.common import IntervalStr
from pydantic import BaseModel


class QuestionBase(BaseModel):
    pass


class QuestionCreate(QuestionBase):
    question_text: str
    duration: Optional[IntervalStr] = None
    resumable: Optional[bool] = None


class QuestionUpdate(QuestionBase):
    question_text: Optional[str] = None
    duration: Optional[IntervalStr] = None
    resumable: Optional[bool] = None


class Question(QuestionBase):
    id: Optional[UUID] = None
    quiz_id: Optional[UUID] = None
    question_text: Optional[str] = None
    duration: Optional[timedelta] = None
    resumable: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class QuestionInDB(Question):
    pass
