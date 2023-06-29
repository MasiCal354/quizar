from app.crud.base import CRUDBase
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate
from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session


class CRUDQuestion(CRUDBase[Question, QuestionCreate, QuestionUpdate]):
    def create_with_quiz(
        self, db: Session, *, obj_in: QuestionCreate, quiz_id: UUID
    ) -> Question:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, quiz_id=quiz_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_quiz(
        self, db: Session, *, quiz_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Question]:
        return (
            db.query(self.model)
            .filter(Question.quiz_id == quiz_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_quiz(self, db: Session, *, quiz_id: UUID) -> int:
        return db.query(self.model).filter(Question.quiz_id == quiz_id).count()


question = CRUDQuestion(Question)
