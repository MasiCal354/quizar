from app.db.base_class import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    quiz = relationship("Quiz", back_populates="author", cascade="all, delete")
    submission = relationship(
        "Submission", back_populates="user", cascade="all, delete"
    )
