from typing import Any

from app.crud.base import CRUDBase
from app.models.answer import Answer
from app.schemas.answer import AnswerCreate, AnswerUpdate
from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session


class CRUDAnswer(CRUDBase[Answer, AnswerCreate, AnswerUpdate]):
    def create_with_question_and_adjust_point(
        self, db: Session, *, obj_in: AnswerCreate, question_id: UUID
    ) -> Answer:
        obj_in_data: dict[str, Any] = jsonable_encoder(obj_in)
        is_correct = obj_in_data.pop("is_correct")
        if is_correct:
            answers = self.get_correct_by_question(db, question_id=question_id)
            total_point = 1
        else:
            answers = self.get_incorrect_by_question(
                db, question_id=question_id
            )
            total_point = -1
        obj_in_data["point"] = total_point / (len(answers) + 1)
        db_obj = self.model(**obj_in_data, question_id=question_id)
        db.add(db_obj)
        for answer in answers:
            setattr(answer, "point", obj_in_data["point"])
            db.add(answer)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_correct_by_question(
        self,
        db: Session,
        *,
        question_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Answer]:
        return (
            db.query(self.model)
            .filter(Answer.question_id == question_id, Answer.point > 0)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_incorrect_by_question(
        self,
        db: Session,
        *,
        question_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Answer]:
        return (
            db.query(self.model)
            .filter(Answer.question_id == question_id, Answer.point < 0)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_question(
        self,
        db: Session,
        *,
        question_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Answer]:
        return (
            db.query(self.model)
            .filter(Answer.question_id == question_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_question(self, db: Session, *, question_id: UUID) -> int:
        return (
            db.query(self.model)
            .filter(Answer.question_id == question_id)
            .count()
        )

    def count_correct_by_question(
        self, db: Session, *, question_id: UUID
    ) -> int:
        return (
            db.query(self.model)
            .filter(Answer.question_id == question_id, Answer.point > 0)
            .count()
        )

    def count_incorrect_by_question(
        self, db: Session, *, question_id: UUID
    ) -> int:
        return (
            db.query(self.model)
            .filter(Answer.question_id == question_id, Answer.point < 0)
            .count()
        )


answer = CRUDAnswer(Answer)
