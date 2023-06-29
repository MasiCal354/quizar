from datetime import datetime, timezone

from app.crud.base import CRUDBase
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionUpdate
from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session


class CRUDSubmission(CRUDBase[Submission, SubmissionCreate, SubmissionUpdate]):
    def create_with_quiz_user(
        self,
        db: Session,
        *,
        obj_in: SubmissionCreate,
        user_id: UUID,
        quiz_id: UUID
    ) -> Submission:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id, quiz_id=quiz_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def count_by_quiz_user(
        self, db: Session, *, user_id: UUID, quiz_id: UUID
    ) -> int:
        return (
            db.query(self.model)
            .filter(
                Submission.user_id == user_id, Submission.quiz_id == quiz_id
            )
            .count()
        )

    def get_multi_by_quiz_user(
        self,
        db: Session,
        *,
        user_id: UUID,
        quiz_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Submission]:
        return (
            db.query(self.model)
            .filter(
                Submission.user_id == user_id, Submission.quiz_id == quiz_id
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_user(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Submission]:
        return (
            db.query(self.model)
            .filter(Submission.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_nondraft_multi_by_quiz(
        self, db: Session, *, quiz_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Submission]:
        return (
            db.query(self.model)
            .filter(Submission.quiz_id == quiz_id, not Submission.draft)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def pause(self, db: Session, *, db_obj: Submission):
        if db_obj.time_remaining:
            time_remaining = db_obj.time_remaining - (
                datetime.now(tz=timezone.utc) - db_obj.updated_at
            )
        else:
            time_remaining = None
        return self.update(
            db,
            db_obj=db_obj,
            obj_in={"time_remaining": time_remaining, "paused": True},
        )

    def resume(self, db: Session, *, db_obj: Submission):
        return self.update(db, db_obj=db_obj, obj_in={"paused": False})

    def submit(
        self, db: Session, *, db_obj: Submission, score: float
    ) -> Submission:
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
                "score": score,
                "time_remaining": time_remaining,
                "draft": False,
            },
        )


submission = CRUDSubmission(Submission)
