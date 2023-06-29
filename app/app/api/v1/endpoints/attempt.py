from typing import Annotated
from uuid import UUID

from app.api import deps
from app.crud import attempt as attempt_crud
from app.crud import question as question_crud
from app.crud import quiz as quiz_crud
from app.crud import solution as solution_crud
from app.crud import submission as submission_crud
from app.models import Attempt as AttemptModel
from app.models import User as UserModel
from app.schemas import Attempt as AttemptSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/submission/{submission_id}/question/{question_id}",
    response_model=AttemptSchema,
)
async def draft(
    db: Annotated[Session, Depends(deps.get_db)],
    submission_id: UUID,
    question_id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> AttemptModel:
    submission = submission_crud.get(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    question = question_crud.get(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if submission.quiz_id != question.quiz_id:
        raise HTTPException(
            status_code=400,
            detail="Can only attempt to question "
            "on the same quiz as the submission",
        )
    quiz = quiz_crud.get(db, question.quiz_id)
    if quiz.author_id != current_user.id and not quiz.published:
        raise HTTPException(
            status_code=403,
            detail="You cannot attempt to question "
            "of other people unpublished quiz",
        )
    attempt = attempt_crud.get_by_submission_question(
        db=db, question_id=question_id, submission_id=submission_id
    )
    if attempt:
        raise HTTPException(
            status_code=403, detail="You already attempt to this question"
        )
    obj_in = {
        "time_remaining": str(question.duration) if question.duration else None
    }
    attempt = attempt_crud.create_with_question_submission(
        db=db,
        obj_in=obj_in,
        question_id=question_id,
        submission_id=submission_id,
    )
    return attempt


@router.get("/{id}", response_model=AttemptSchema)
async def read(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> AttemptModel:
    attempt = attempt_crud.get(db, id=id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    submission = submission_crud.get(db, attempt.submission_id)
    question = question_crud.get(db, attempt.question_id)
    quiz = quiz_crud.get(db, question.quiz_id)
    if current_user.id not in {submission.user_id, quiz.author_id}:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to see this attempt",
        )
    if current_user.id != submission.user_id and submission.draft:
        raise HTTPException(
            status_code=403, detail="This attempt is still in draft"
        )
    return attempt


@router.get("/submission/{submission_id}", response_model=list[AttemptSchema])
async def read_by_submission(
    db: Annotated[Session, Depends(deps.get_db)],
    submission_id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> list[AttemptModel]:
    submission = submission_crud.get(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    quiz = quiz_crud.get(db, submission.quiz_id)
    if current_user.id not in {submission.user_id, quiz.author_id}:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to see this attempt",
        )
    if current_user.id != submission.user_id and submission.draft:
        raise HTTPException(
            status_code=403, detail="This attempt is still in draft"
        )
    attempts = attempt_crud.get_multi_by_submission(
        db, submission_id=submission_id
    )
    return attempts


@router.put("/skip/{id}", response_model=AttemptSchema)
async def skip(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> AttemptModel:
    attempt = attempt_crud.get(db=db, id=id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if not attempt.draft:
        raise HTTPException(
            status_code=400, detail="This attempt is not draft"
        )
    if attempt.skipped:
        raise HTTPException(
            status_code=400, detail="This attempt already skipped"
        )
    submission = submission_crud.get(db, attempt.submission_id)
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You don't have permission to skip the attempt",
        )
    question = question_crud.get(db, attempt.question_id)
    if not question.resumable:
        raise HTTPException(
            status_code=400, detail="This question is not resumable/skippable"
        )
    attempt = attempt_crud.skip(db=db, db_obj=attempt)
    return attempt


@router.put("/resume/{id}", response_model=AttemptSchema)
async def resume(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> AttemptModel:
    attempt = attempt_crud.get(db=db, id=id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if not attempt.draft:
        raise HTTPException(
            status_code=400, detail="This attempt is not draft"
        )
    if not attempt.skipped:
        raise HTTPException(
            status_code=400, detail="This attempt is not skipped"
        )
    submission = submission_crud.get(db, attempt.submission_id)
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You don't have permission to resume the attempt",
        )
    attempt = attempt_crud.resume(db, db_obj=attempt)
    return attempt


@router.put("/submit/{id}", response_model=AttemptSchema)
async def submit(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> AttemptModel:
    attempt = attempt_crud.get(db=db, id=id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if not attempt.draft:
        raise HTTPException(status_code=400, detail="Already submitted")
    if attempt.skipped:
        raise HTTPException(
            status_code=400, detail="Please submit before submitting"
        )
    submission = submission_crud.get(db, attempt.submission_id)
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You have no permission to submit this draft",
        )
    score = solution_crud.sum_point_by_attempt(db, attempt_id=id)
    attempt = attempt_crud.submit(db, db_obj=attempt, score=score)
    return attempt
