from app.db.base_class import Base
from sqlalchemy import Boolean, Column, ForeignKey, Interval, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Quiz(Base):
    __tablename__ = "quizzes"
    author_id = Column(UUID, ForeignKey("users.id"), index=True)
    title = Column(String, nullable=False)
    published = Column(Boolean, nullable=False, default=False)
    resumable = Column(Boolean, nullable=False, default=False)
    description = Column(String, nullable=True, default=None)
    duration = Column(Interval, nullable=True, default=None)
    author = relationship("User", back_populates="quiz", cascade="all, delete")
    question = relationship(
        "Question", back_populates="quiz", cascade="all, delete"
    )
    attempt = relationship(
        "Submission", back_populates="quiz", cascade="all, delete"
    )
