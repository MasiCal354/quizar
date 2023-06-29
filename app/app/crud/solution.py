from app.crud.base import CRUDBase
from app.models.solution import Solution
from app.schemas.solution import SolutionCreate, SolutionUpdate
from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from sqlalchemy.sql import func


class CRUDSolution(CRUDBase[Solution, SolutionCreate, SolutionUpdate]):
    def create_with_answer_attempt(
        self,
        db: Session,
        *,
        obj_in: SolutionCreate,
        attempt_id: UUID,
        answer_id: UUID
    ) -> Solution:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data, attempt_id=attempt_id, answer_id=answer_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_attempt(
        self, db: Session, *, attempt_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Solution]:
        return (
            db.query(self.model)
            .filter(Solution.attempt_id == attempt_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def sum_point_by_attempt(self, db: Session, *, attempt_id: UUID) -> float:
        return db.query(
            func.sum(self.model.point).filter(
                Solution.attempt_id == attempt_id
            )
        ).scalar()


solution = CRUDSolution(Solution)
