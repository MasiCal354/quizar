from datetime import datetime, timezone

from app.crud.base import CRUDBase
from app.models.attempt import Attempt
from app.schemas.attempt import AttemptCreate, AttemptUpdate
from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from sqlalchemy.sql import func


class CRUDAttempt(CRUDBase[Attempt, AttemptCreate, AttemptUpdate]):
    def create_with_question_submission(
        self,
        db: Session,
        *,
        obj_in: AttemptCreate,
        submission_id: UUID,
        question_id: UUID
    ) -> Attempt:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data, submission_id=submission_id, question_id=question_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_submission(
        self,
        db: Session,
        *,
        submission_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Attempt]:
        return (
            db.query(self.model)
            .filter(Attempt.submission_id == submission_id)
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
        limit: int = 100
    ) -> list[Attempt]:
        return (
            db.query(self.model)
            .filter(Attempt.question_id == question_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_submission_question(
        self,
        db: Session,
        *,
        submission_id: UUID,
        question_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Attempt:
        return (
            db.query(self.model.score)
            .filter(
                Attempt.submission_id == submission_id,
                Attempt.question_id == question_id,
            )
            .offset(skip)
            .limit(limit)
            .first()
        )

    def get_multi_draft_by_submission(
        self, db: Session, *, submission_id: UUID
    ) -> list[Attempt]:
        return (
            db.query(self.model)
            .filter(Attempt.submission_id == submission_id, Attempt.draft)
            .all()
        )

    def submit_multi_by_submission_no_commit(
        self, db: Session, *, submission_id: UUID, scores: dict[UUID, float]
    ) -> None:
        attempts = self.get_multi_draft_by_submission(
            db, submission_id=submission_id
        )
        for attempt in attempts:
            if attempt.time_remaining:
                time_remaining = attempt.time_remaining - (
                    datetime.now(tz=timezone.utc) - attempt.updated_at
                )
            else:
                time_remaining = None
            setattr(attempt, "time_remaining", time_remaining)
            setattr(attempt, "draft", False)
            setattr(attempt, "score", scores[attempt.id])
            db.add(attempt)

    def sum_score_by_submission(
        self, db: Session, *, submission_id: UUID
    ) -> float:
        return db.query(
            func.sum(self.model.score).filter(
                Attempt.submission_id == submission_id
            )
        ).scalar()

    def skip(self, db: Session, *, db_obj: Attempt) -> Attempt:
        if db_obj.time_remaining:
            time_remaining = db_obj.time_remaining - (
                datetime.now(tz=timezone.utc) - db_obj.updated_at
            )
        else:
            time_remaining = None
        return self.update(
            db,
            db_obj=db_obj,
            obj_in={"time_remaining": time_remaining, "skipped": True},
        )

    def resume(self, db: Session, *, db_obj: Attempt) -> Attempt:
        return self.update(db, db_obj=db_obj, obj_in={"skipped": False})

    def submit(self, db: Session, *, db_obj: Attempt, score: float) -> Attempt:
        if db_obj.time_remaining:
            time_remaining = db_obj.time_remaining - (
                datetime.now(tz=timezone.utc) - db_obj.updated_at
            )
        else:
            time_remaining = None
        return self.update(
            db,
            db_obj=db_obj,
            obj_in={
                "time_remaining": time_remaining,
                "draft": False,
                "score": score,
            },
        )


attempt = CRUDAttempt(Attempt)
