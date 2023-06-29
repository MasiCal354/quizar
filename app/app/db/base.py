# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa: F401
from app.models.answer import Answer  # noqa: F401
from app.models.attempt import Attempt  # noqa: F401
from app.models.question import Question  # noqa: F401
from app.models.quiz import Quiz  # noqa: F401
from app.models.solution import Solution  # noqa: F401
from app.models.submission import Submission  # noqa: F401
from app.models.user import User  # noqa: F401
