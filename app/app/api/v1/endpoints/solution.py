from typing import Annotated
from uuid import UUID

from app.api import deps
from app.crud import answer as answer_crud
from app.crud import attempt as attempt_crud
from app.crud import question as question_crud
from app.crud import quiz as quiz_crud
from app.crud import solution as solution_crud
from app.crud import submission as submission_crud
from app.models import Solution as SolutionModel
from app.models import User as UserModel
from app.schemas import Solution as SolutionSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/attempt/{attempt_id}/answer/{answer_id}", response_model=SolutionSchema
)
async def add(
    db: Annotated[Session, Depends(deps.get_db)],
    attempt_id: UUID,
    answer_id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> SolutionModel:
    attempt = attempt_crud.get(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    answer = answer_crud.get(db, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    if attempt.question_id != answer.question_id:
        raise HTTPException(
            status_code=400,
            detail="Can only solution to answer "
            "on the same question as the attempt",
        )
    question = question_crud.get(db, answer.question_id)
    quiz = quiz_crud.get(db, question.quiz_id)
    if quiz.author_id != current_user.id and not quiz.published:
        raise HTTPException(
            status_code=403,
            detail="You cannot solution to answer "
            "of other people unpublished question",
        )
    obj_in = {"point": answer.point}
    solution = solution_crud.create_with_answer_attempt(
        db=db, obj_in=obj_in, answer_id=answer_id, attempt_id=attempt_id
    )
    return solution


@router.get("/{id}", response_model=SolutionSchema)
async def read(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> SolutionModel:
    solution = solution_crud.get(db, id=id)
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    attempt = attempt_crud.get(db, solution.attempt_id)
    answer = answer_crud.get(db, solution.answer_id)
    question = question_crud.get(db, answer.question_id)
    quiz = quiz_crud.get(db, question.quiz_id)
    submission = submission_crud.get(db, attempt.submission_id)
    if current_user.id not in {submission.user_id, quiz.author_id}:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to see this solution",
        )
    if current_user.id != submission.user_id and submission.draft:
        raise HTTPException(
            status_code=403,
            detail="The submission of this solution is still in draft",
        )
    return solution


@router.get("/attempt/{attempt_id}", response_model=list[SolutionSchema])
async def read_by_attempt(
    db: Annotated[Session, Depends(deps.get_db)],
    attempt_id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> list[SolutionModel]:
    attempt = attempt_crud.get(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    question = question_crud.get(db, attempt.question_id)
    quiz = quiz_crud.get(db, question.quiz_id)
    submission = submission_crud.get(db, attempt.submission_id)
    if current_user.id not in {submission.user_id, quiz.author_id}:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to see this solution",
        )
    if current_user.id != submission.user_id and submission.draft:
        raise HTTPException(
            status_code=403,
            detail="The submission of this solution is still in draft",
        )
    solutions = solution_crud.get_multi_by_attempt(db, attempt_id=attempt_id)
    return solutions


@router.delete("/{id}", response_model=SolutionSchema)
async def delete(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> SolutionModel:
    solution = solution_crud.get(db=db, id=id)
    if not solution:
        raise HTTPException(status_code=404, detail="Quiz not found")
    attempt = attempt_crud.get(db, solution.attempt_id)
    submission = submission_crud.get(db, attempt.submission_id)
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Only the author can delete this solution"
        )
    quiz = quiz_crud.delete(db, id=id)
    return quiz
