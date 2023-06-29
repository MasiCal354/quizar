from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SubmissionBase(BaseModel):
    pass


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionUpdate(SubmissionBase):
    pass


class Submission(SubmissionBase):
    id: Optional[UUID] = None
    quiz_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    draft: Optional[bool] = None
    score: Optional[float] = None
    time_remaining: Optional[timedelta] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SubmissionInDB(Submission):
    pass
