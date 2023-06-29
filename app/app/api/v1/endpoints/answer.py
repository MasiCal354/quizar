from typing import Annotated
from uuid import UUID

from app.api import deps
from app.core.config import settings
from app.crud import answer as answer_crud
from app.crud import question as question_crud
from app.crud import quiz as quiz_crud
from app.crud import submission as submission_crud
from app.models import Answer as AnswerModel
from app.models import User as UserModel
from app.schemas import Answer as AnswerSchema
from app.schemas import AnswerCreate, AnswerUpdate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/question/{question_id}", response_model=AnswerSchema)
async def add(
    db: Annotated[Session, Depends(deps.get_db)],
    answer_in: AnswerCreate,
    question_id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> AnswerModel:
    question = question_crud.get(db, question_id)
    quiz = quiz_crud.get(db, question.quiz_id)
    correct_answer_count = answer_crud.count_correct_by_question(
        db, question_id=question_id
    )
    incorrect_answer_count = answer_crud.count_incorrect_by_question(
        db, question_id=question_id
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if quiz.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the author of the quiz "
            "can add answer to this question",
        )
    if (
        correct_answer_count + incorrect_answer_count
        >= settings.MAX_ANSWER_PER_QUESTION
    ):
        raise HTTPException(
            status_code=400, detail="Cannot add more answers on this question"
        )
    if quiz.published:
        raise HTTPException(
            status_code=400,
            detail="Cannot add answer to question of published quiz",
        )
    answer = answer_crud.create_with_question_and_adjust_point(
        db=db, obj_in=answer_in, question_id=question_id
    )
    return answer


@router.get("/{id}", response_model=AnswerSchema)
async def read(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> AnswerModel:
    answer = answer_crud.get(db, id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    question = question_crud.get(db, answer.question_id)
    quiz = quiz_crud.get(db, question.quiz_id)
    submission_count = submission_crud.count_by_quiz_user(
        db, user_id=current_user.id, quiz_id=question.quiz_id
    )
    if quiz.author_id != current_user.id and submission_count == 0:
        raise HTTPException(
            status_code=403,
            detail="You have to start working on "
            "the quiz before accessing the answer",
        )
    return answer


@router.get("/question/{question_id}", response_model=list[AnswerSchema])
async def read_by_question(
    db: Annotated[Session, Depends(deps.get_db)],
    question_id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> AnswerModel:
    question = question_crud.get(db, question_id)
    quiz = quiz_crud.get(db, question.quiz_id)
    answers = answer_crud.get_multi_by_question(db, question_id=question_id)
    submission_count = submission_crud.count_by_quiz_user(
        db, user_id=current_user.id, quiz_id=question.quiz_id
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if quiz.author_id != current_user.id and submission_count == 0:
        raise HTTPException(
            status_code=403,
            detail="You have to start working on "
            "the question before accessing the answer",
        )
    return answers


@router.put("/{id}", response_model=AnswerSchema)
async def edit(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    answer_in: AnswerUpdate,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> AnswerModel:
    answer = answer_crud.get(db=db, id=id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    question = question_crud.get(db=db, id=answer.question_id)
    quiz = quiz_crud.get(db, question.quiz_id)
    if quiz.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the author can edit this answer"
        )
    if quiz.published:
        raise HTTPException(
            status_code=400,
            detail="Answer of question on published quiz cannot be edited",
        )
    answer = answer_crud.update(db=db, db_obj=answer, obj_in=answer_in)
    return answer


@router.delete("/{id}", response_model=AnswerSchema)
async def delete(
    db: Annotated[Session, Depends(deps.get_db)],
    id: UUID,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
) -> AnswerModel:
    answer = answer_crud.get(db=db, id=id)
    question = question_crud.get(db, answer.question_id)
    quiz = quiz_crud.get(db, question.quiz_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    if quiz.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the author can delete this answer"
        )
    if quiz.published:
        raise HTTPException(
            status_code=400,
            detail="Answer of question on published quiz cannot be deleted",
        )
    answer = answer_crud.delete(db, id=id)
    return answer
