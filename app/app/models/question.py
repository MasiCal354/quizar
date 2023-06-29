from app.db.base_class import Base
from sqlalchemy import Boolean, Column, ForeignKey, Interval, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Question(Base):
    __tablename__ = "questions"
    quiz_id = Column(UUID, ForeignKey("quizzes.id"), index=True)
    question_text = Column(String, nullable=False)
    duration = Column(Interval, nullable=True, default=None)
    resumable = Column(Boolean, nullable=False, default=False)
    quiz = relationship(
        "Quiz", back_populates="question", cascade="all, delete"
    )
    answer = relationship(
        "Answer", back_populates="question", cascade="all, delete"
    )
    attempt = relationship(
        "Attempt", back_populates="question", cascade="all, delete"
    )
