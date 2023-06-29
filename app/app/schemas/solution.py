from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SolutionBase(BaseModel):
    pass


class SolutionCreate(SolutionBase):
    point: float


class SolutionUpdate(SolutionBase):
    point: Optional[float] = None


class Solution(SolutionBase):
    id: Optional[UUID] = None
    attempt_id: Optional[UUID] = None
    answer_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SolutionInDB(Solution):
    pass
