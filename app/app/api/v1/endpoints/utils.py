from datetime import datetime, timezone
from typing import Annotated

from app.api import deps
from app.models import User as UserModel
from app.schemas import Health, ServerTime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/health", response_model=Health)
async def healthcheck(
    db: Annotated[Session, Depends(deps.get_db)],
) -> UserModel:
    return {"condition": "Healthy"}


@router.get("/time", response_model=ServerTime)
async def server_time(
    db: Annotated[Session, Depends(deps.get_db)],
) -> dict[str, str]:
    return {"server_time": datetime.now(tz=timezone.utc)}
