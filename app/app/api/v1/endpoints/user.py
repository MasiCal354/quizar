from datetime import timedelta
from typing import Annotated

from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import user as user_crud
from app.models import User as UserModel
from app.schemas import Token
from app.schemas import User as UserSchema
from app.schemas import UserCreate, UserUpdate
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/register", response_model=UserSchema)
async def register(
    db: Annotated[Session, Depends(deps.get_db)],
    user_in: UserCreate,
) -> UserModel:
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user = user_crud.create(db, obj_in=user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    db: Annotated[Session, Depends(deps.get_db)],
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    user = user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect email or password"
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.put("/password", response_model=UserSchema)
async def update_password(
    db: Annotated[Session, Depends(deps.get_db)],
    user_in: UserUpdate,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> UserModel:
    user = user_crud.update_password(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=UserSchema)
async def read_user(
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> UserModel:
    return current_user
