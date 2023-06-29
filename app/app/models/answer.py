from app.db.base_class import Base
from sqlalchemy import Column, Double, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Answer(Base):
    __tablename__ = "answers"
    question_id = Column(UUID, ForeignKey("questions.id"), index=True)
    answer_text = Column(String, nullable=False)
    point = Column(Double, nullable=False)
    question = relationship(
        "Question", back_populates="answer", cascade="all, delete"
    )
    solution = relationship(
        "Solution", back_populates="answer", cascade="all, delete"
    )
