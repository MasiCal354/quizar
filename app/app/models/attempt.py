from app.db.base_class import Base
from sqlalchemy import (
    Boolean,
    Column,
    Double,
    ForeignKey,
    Interval,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Attempt(Base):
    __tablename__ = "attempts"
    question_id = Column(UUID, ForeignKey("questions.id"), index=True)
    submission_id = Column(UUID, ForeignKey("submissions.id"), index=True)
    draft = Column(Boolean, nullable=False, default=True)
    skipped = Column(Boolean, nullable=False, default=False)
    time_remaining = Column(Interval, nullable=True, default=None)
    score = Column(Double, nullable=True, default=None)
    question = relationship(
        "Question", back_populates="attempt", cascade="all, delete"
    )
    submission = relationship(
        "Submission", back_populates="attempt", cascade="all, delete"
    )
    solution = relationship(
        "Solution", back_populates="attempt", cascade="all, delete"
    )
    __table_args__ = (UniqueConstraint("question_id", "submission_id"),)
