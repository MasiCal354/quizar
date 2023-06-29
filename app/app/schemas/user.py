from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    old_password: Optional[str] = None
    new_password: Optional[str] = None


class User(UserBase):
    id: Optional[UUID] = None
    email: Optional[EmailStr] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str
