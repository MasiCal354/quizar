from datetime import datetime

from pydantic import BaseModel


class Health(BaseModel):
    condition: str


class ServerTime(BaseModel):
    server_time: datetime
