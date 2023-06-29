from app.api.v1.endpoints.answer import router as answer_router
from app.api.v1.endpoints.attempt import router as attempt_router
from app.api.v1.endpoints.question import router as question_router
from app.api.v1.endpoints.quiz import router as quiz_router
from app.api.v1.endpoints.solution import router as solution_router
from app.api.v1.endpoints.submission import router as submission_router
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.utils import router as utils_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(answer_router, prefix="/answer", tags=["answer"])
api_router.include_router(attempt_router, prefix="/attempt", tags=["attempt"])
api_router.include_router(
    question_router, prefix="/question", tags=["question"]
)
api_router.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
api_router.include_router(
    submission_router, prefix="/submission", tags=["submission"]
)
api_router.include_router(
    solution_router, prefix="/solution", tags=["solution"]
)
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(utils_router, tags=["utils"])
