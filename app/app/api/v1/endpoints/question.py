from typing import Annotated
from uuid import UUID

from app.api import deps
from app.core.config import settings
from app.crud import question as question_crud
from app.crud import quiz as quiz_crud
from app.crud import submission as submission_crud
from app.models import Question as QuestionModel
from app.models import User as UserModel
from app.schemas import Question as QuestionSchema
from app.schemas import QuestionCreate, QuestionUpdate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/quiz/{quiz_id}", response_model=QuestionSchema)
async def add(
    db: Annotated[Session, Depends(deps.get_db)],
    question_in: QuestionCreate,
    quiz_id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> QuestionModel:
    quiz = quiz_crud.get(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the author can add question to this quiz",
        )
    question_count = question_crud.count_by_quiz(db, quiz_id=quiz_id)
    if question_count >= settings.MAX_QUESTIONS_PER_QUIZ:
        raise HTTPException(
            status_code=400, detail="Cannot add more questions on this quiz"
        )
    if quiz.published:
        raise HTTPException(
            status_code=400, detail="Cannot add question to published quiz"
        )
    question = question_crud.create_with_quiz(
        db=db, obj_in=question_in, quiz_id=quiz_id
    )
    return question


@router.get("/{id}", response_model=QuestionSchema)
async def read(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> QuestionModel:
    question = question_crud.get(db, id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    quiz = quiz_crud.get(db, question.quiz_id)
    submission_count = submission_crud.count_by_quiz_user(
        db, user_id=current_user.id, quiz_id=question.quiz_id
    )
    if quiz.author_id != current_user.id and submission_count == 0:
        raise HTTPException(
            status_code=400,
            detail="You have to start working on "
            "the quiz before accessing the question",
        )
    return question


@router.get("/quiz/{quiz_id}", response_model=list[QuestionSchema])
async def read_by_quiz(
    db: Annotated[Session, Depends(deps.get_db)],
    quiz_id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> QuestionModel:
    quiz = quiz_crud.get(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    questions = question_crud.get_multi_by_quiz(db, quiz_id=quiz_id)
    submission_count = submission_crud.count_by_quiz_user(
        db, user_id=current_user.id, quiz_id=quiz_id
    )
    if quiz.author_id != current_user.id and submission_count == 0:
        raise HTTPException(
            status_code=400,
            detail="You have to start working on "
            "the quiz before accessing the question",
        )
    return questions


@router.put("/{id}", response_model=QuestionSchema)
async def edit(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    question_in: QuestionUpdate,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> QuestionModel:
    question = question_crud.get(db=db, id=id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    quiz = quiz_crud.get(db=db, id=question.quiz_id)
    if quiz.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the author can edit this question"
        )
    if quiz.published:
        raise HTTPException(
            status_code=400,
            detail="Question on published quiz cannot be edited",
        )
    question = question_crud.update(db=db, db_obj=question, obj_in=question_in)
    return question


@router.delete("/{id}", response_model=QuestionSchema)
async def delete(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> QuestionModel:
    question = question_crud.get(db=db, id=id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    quiz = quiz_crud.get(db, question.quiz_id)
    if quiz.author_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Only the author can delete this question"
        )
    if quiz.published:
        raise HTTPException(
            status_code=400,
            detail="Question on published quiz cannot be deleted",
        )
    question = question_crud.delete(db, id=id)
    return question
