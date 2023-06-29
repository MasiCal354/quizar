from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AttemptBase(BaseModel):
    pass


class AttemptCreate(AttemptBase):
    pass


class AttemptUpdate(AttemptBase):
    pass


class Attempt(AttemptBase):
    id: Optional[UUID] = None
    question_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    draft: Optional[bool] = None
    time_remaining: Optional[timedelta] = None
    score: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class AttemptInDB(Attempt):
    pass
