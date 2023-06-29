from uuid import uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql.functions import now


@as_declarative()
class Base:
    id = Column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    created_at = Column(
        DateTime(timezone=True), index=True, server_default=now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        index=True,
        server_default=now(),
        onupdate=now(),
    )
    __name__: str
