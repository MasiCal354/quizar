from typing import Annotated
from uuid import UUID

from app.api import deps
from app.core.config import settings
from app.crud import attempt as attempt_crud
from app.crud import quiz as quiz_crud
from app.crud import solution as solution_crud
from app.crud import submission as submission_crud
from app.models import Submission as SubmissionModel
from app.models import User as UserModel
from app.schemas import Submission as SubmissionSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/quiz/{quiz_id}", response_model=SubmissionSchema)
async def draft(
    db: Annotated[Session, Depends(deps.get_db)],
    quiz_id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> SubmissionModel:
    quiz = quiz_crud.get(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.author_id != current_user.id and not quiz.published:
        raise HTTPException(
            status_code=403,
            detail="You cannot submit to other people unpublished quiz",
        )
    submission_count = submission_crud.count_by_quiz_user(
        db=db, quiz_id=quiz_id, user_id=current_user.id
    )
    if submission_count >= settings.MAX_SUBMISSION_PER_QUIZ:
        raise HTTPException(
            status_code=403,
            detail="You cannot make a submission more than "
            f"{settings.MAX_SUBMISSION_PER_QUIZ} to this quiz",
        )
    obj_in = {"time_remaining": str(quiz.duration) if quiz.duration else None}
    submission = submission_crud.create_with_quiz_user(
        db=db, obj_in=obj_in, quiz_id=quiz_id, user_id=current_user.id
    )
    return submission


@router.get("/{id}", response_model=SubmissionSchema)
async def read(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> SubmissionModel:
    submission = submission_crud.get(db, id=id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    quiz = quiz_crud.get(db, submission.quiz_id)
    if current_user.id not in {submission.user_id, quiz.author_id}:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to see this submission",
        )
    if quiz.author_id == current_user.id and submission.draft:
        raise HTTPException(
            status_code=403, detail="This submission still in draft"
        )
    return submission


@router.get("/_/me", response_model=list[SubmissionSchema])
async def read_submissions(
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> list[SubmissionModel]:
    submissions = submission_crud.get_multi_by_user(
        db, user_id=current_user.id
    )
    return submissions


@router.get("/quiz/{quiz_id}", response_model=list[SubmissionSchema])
async def read_by_quiz(
    db: Annotated[Session, Depends(deps.get_db)],
    quiz_id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> list[SubmissionModel]:
    quiz = quiz_crud.get(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.author_id == current_user.id:
        submissions = submission_crud.get_nondraft_multi_by_quiz(
            db, quiz_id == quiz_id
        )
    elif not quiz.published:
        raise HTTPException(
            status_code=403, detail="Cannot access unpublished quiz"
        )
    else:
        submissions = submission_crud.get_multi_by_quiz_user(
            db, quiz_id=quiz_id, user_id=current_user.id
        )
    return submissions


@router.put("/pause/{id}", response_model=SubmissionSchema)
async def pause(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> SubmissionModel:
    submission = submission_crud.get(db=db, id=id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if not submission.draft:
        raise HTTPException(
            status_code=400, detail="This submission is not draft"
        )
    if submission.paused:
        raise HTTPException(
            status_code=400, detail="This submission already paused"
        )
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You don't have permission to pause the submission",
        )
    quiz = quiz_crud.get(db, submission.quiz_id)
    if not quiz.resumable:
        raise HTTPException(
            status_code=400, detail="This quiz is not resumable/pausable"
        )
    submission = submission_crud.pause(db=db, db_obj=submission)
    return submission


@router.put("/resume/{id}", response_model=SubmissionSchema)
async def resume(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> SubmissionModel:
    submission = submission_crud.get(db=db, id=id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if not submission.draft:
        raise HTTPException(
            status_code=400, detail="This submission is not draft"
        )
    if not submission.paused:
        raise HTTPException(
            status_code=400, detail="This submission is not paused"
        )
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You don't have permission to resume the submission",
        )
    submission = submission_crud.resume(db, db_obj=submission)
    return submission


@router.put("/submit/{id}", response_model=SubmissionSchema)
async def submit(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> SubmissionModel:
    submission = submission_crud.get(db=db, id=id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if not submission.draft:
        raise HTTPException(status_code=400, detail="Already submitted")
    if submission.paused:
        raise HTTPException(
            status_code=400, detail="Please submit before submitting"
        )
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You have no permission to submit this draft",
        )
    attempts = attempt_crud.get_multi_draft_by_submission(db, submission_id=id)
    scores = {}
    for attempt in attempts:
        scores[attempt.id] = solution_crud.sum_point_by_attempt(
            db, attempt_id=attempt.id
        )
    attempt_crud.submit_multi_by_submission_no_commit(
        db, submission_id=id, scores=scores
    )
    score = attempt_crud.sum_score_by_submission(db, submission_id=id)
    submission = submission_crud.submit(db, db_obj=submission, score=score)
    return submission
