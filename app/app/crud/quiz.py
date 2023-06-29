from app.crud.base import CRUDBase
from app.models.quiz import Quiz
from app.schemas.quiz import QuizCreate, QuizUpdate
from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session


class CRUDQuiz(CRUDBase[Quiz, QuizCreate, QuizUpdate]):
    def create_with_author(
        self, db: Session, *, obj_in: QuizCreate, author_id: UUID
    ) -> Quiz:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, author_id=author_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_author(
        self, db: Session, *, author_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Quiz]:
        return (
            db.query(self.model)
            .filter(Quiz.author_id == author_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_published(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Quiz]:
        return (
            db.query(self.model)
            .filter(Quiz.published)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def publish(self, db: Session, db_obj: Quiz) -> Quiz:
        return self.update(db, db_obj=db_obj, obj_in={"published": True})


quiz = CRUDQuiz(Quiz)
