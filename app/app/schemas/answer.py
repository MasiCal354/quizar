from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AnswerBase(BaseModel):
    pass


class AnswerCreate(AnswerBase):
    answer_text: str
    is_correct: bool = False


class AnswerUpdate(AnswerBase):
    answer_text: Optional[str] = None
    is_correct: Optional[bool] = None


class Answer(AnswerBase):
    id: Optional[UUID] = None
    question_id: Optional[UUID] = None
    answer_text: Optional[str] = None
    point: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class AnswerInDB(Answer):
    pass
