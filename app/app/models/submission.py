from app.db.base_class import Base
from sqlalchemy import Boolean, Column, Double, ForeignKey, Interval, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Submission(Base):
    __tablename__ = "submissions"
    quiz_id = Column(UUID, ForeignKey("quizzes.id"), index=True)
    user_id = Column(UUID, ForeignKey("users.id"), index=True)
    draft = Column(String, nullable=False, default=True)
    paused = Column(Boolean, nullable=False, default=False)
    score = Column(Double, nullable=True, default=None)
    time_remaining = Column(Interval, nullable=True, default=None)
    quiz = relationship(
        "Quiz", back_populates="attempt", cascade="all, delete"
    )
    user = relationship(
        "User", back_populates="submission", cascade="all, delete"
    )
    attempt = relationship(
        "Attempt", back_populates="submission", cascade="all, delete"
    )
