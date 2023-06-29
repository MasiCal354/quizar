from typing import Annotated
from uuid import UUID

from app.api import deps
from app.core.config import settings
from app.crud import answer as answer_crud
from app.crud import question as question_crud
from app.crud import quiz as quiz_crud
from app.models import Quiz as QuizModel
from app.models import User as UserModel
from app.schemas import Quiz as QuizSchema
from app.schemas import QuizCreate, QuizUpdate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=QuizSchema)
async def create(
    db: Annotated[Session, Depends(deps.get_db)],
    quiz_in: QuizCreate,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> QuizModel:
    quiz = quiz_crud.create_with_author(
        db=db, obj_in=quiz_in, author_id=current_user.id
    )
    return quiz


@router.get("/{id}", response_model=QuizSchema)
async def read(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> QuizModel:
    quiz = quiz_crud.get(db, id=id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.author_id != current_user.id and not quiz.published:
        raise HTTPException(
            status_code=400, detail="Only the author can edit unpublished quiz"
        )
    return quiz


@router.get("/", response_model=list[QuizSchema])
async def read_quizzes(
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> list[QuizModel]:
    quizzes = quiz_crud.get_multi_by_author(db, author_id=current_user.id)
    return quizzes


@router.get("/_/me", response_model=list[QuizSchema])
async def read_by_author(
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> list[QuizModel]:
    quizzes = quiz_crud.get_multi_by_author(db, author_id=current_user.id)
    return quizzes


@router.get("/_/published", response_model=list[QuizSchema])
async def read_published(
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> list[QuizModel]:
    quizzes = quiz_crud.get_multi_published(db)
    return quizzes


@router.put("/{id}", response_model=QuizSchema)
async def edit(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    quiz_in: QuizUpdate,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> QuizModel:
    quiz = quiz_crud.get(db=db, id=id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.author_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Only the author can edit this quiz"
        )
    if quiz.published:
        raise HTTPException(
            status_code=400, detail="Published quiz cannot be edited"
        )
    quiz = quiz_crud.update(db=db, db_obj=quiz, obj_in=quiz_in)
    return quiz


@router.put("/publish/{id}", response_model=QuizSchema)
async def publish(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> QuizModel:
    quiz = quiz_crud.get(db=db, id=id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    question_count = question_crud.count_by_quiz(db, quiz_id=id)
    questions = question_crud.get_multi_by_quiz(db, quiz_id=id)
    for question in questions:
        answer_count = answer_crud.count_by_question(
            db, question_id=question.id
        )
        if answer_count < settings.MIN_ANSWER_PER_QUESTION:
            raise HTTPException(
                status_code=400,
                detail="Cannot publish quiz that have question with "
                f"less than {settings.MIN_ANSWER_PER_QUESTION} answers",
            )
        if answer_count > settings.MAX_ANSWER_PER_QUESTION:
            raise HTTPException(
                status_code=400,
                detail="Cannot publish quiz that have question with "
                f"more than {settings.MAX_ANSWER_PER_QUESTION} answers",
            )
    if question_count < settings.MIN_QUESTIONS_PER_QUIZ:
        raise HTTPException(
            status_code=400,
            detail="Cannot publish quiz with less than "
            f"{settings.MIN_QUESTIONS_PER_QUIZ} question",
        )
    if question_count > settings.MAX_QUESTIONS_PER_QUIZ:
        raise HTTPException(
            status_code=400,
            detail="Cannot publish quiz with more than "
            f"{settings.MAX_QUESTIONS_PER_QUIZ} questions",
        )
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.author_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Only the author can publish this quiz"
        )
    if quiz.published:
        raise HTTPException(status_code=400, detail="Quiz already published")
    quiz = quiz_crud.publish(db=db, db_obj=quiz)
    return quiz


@router.delete("/{id}", response_model=QuizSchema)
async def delete(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> QuizModel:
    quiz = quiz_crud.get(db=db, id=id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.author_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Only the author can delete this quiz"
        )
    quiz = quiz_crud.delete(db, id=id)
    return quiz
