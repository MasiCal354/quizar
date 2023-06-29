from app.db.base_class import Base
from sqlalchemy import Column, Double, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Solution(Base):
    __tablename__ = "solutions"
    attempt_id = Column(UUID, ForeignKey("attempts.id"), index=True)
    answer_id = Column(UUID, ForeignKey("answers.id"), index=True)
    point = Column(Double, nullable=False)
    attempt = relationship(
        "Attempt", back_populates="solution", cascade="all, delete"
    )
    answer = relationship(
        "Answer", back_populates="solution", cascade="all, delete"
    )
    __table_args__ = (UniqueConstraint("answer_id", "attempt_id"),)
