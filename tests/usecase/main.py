from collections import OrderedDict
from logging import INFO, Formatter, Logger, StreamHandler, getLogger
from uuid import UUID

from faker import Faker
from requests import HTTPError, Session

logger: Logger = getLogger(__name__)
handler: StreamHandler = StreamHandler()
fmt: Formatter = Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(fmt)
handler.setLevel(INFO)
logger.addHandler(handler)
logger.setLevel(INFO)


class UseCaseTest:
    def __init__(
        self,
        host: str = "localhost",
        port: str | int = "8080",
        *,
        session: Session | None = None,
    ) -> None:
        self.faker = Faker()
        self.base_url = f"http://{host}:{port}/api/v1"
        self.email_passwords = {}
        self.session = session or Session()
        self.headers = {"accept": "application/json"}

    def add_users(self, n: int, password_length: int = 16) -> None:
        for _ in range(n):
            payload = {
                "email": self.faker.email(),
                "password": self.faker.password(password_length),
            }
            self.email_passwords[payload["email"]] = payload["password"]
            self.session.post(f"{self.base_url}/user/register", json=payload)

    def login(self, email: str) -> None:
        payload = {
            "grant_type": "",
            "username": email,
            "password": self.email_passwords[email],
            "scope": "",
            "client_id": "",
            "client_secret": "",
        }
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = self.session.post(
            f"{self.base_url}/user/login", data=payload, headers=headers
        )
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error(payload)
            logger.error(response.text)
            raise
        access_token = response.json()["access_token"]
        self.headers["Authorization"] = f"Bearer {access_token}"

    def generate_quizzes(self, n: int):
        for _ in range(n):
            duration = self.faker.random_choices(
                OrderedDict(
                    {
                        None: 0.8,
                        f"""{self.faker.pyfloat(
                    positive=True,
                    right_digits=2,
                    min_value=0.5,
                    max_value=6
                )} HOURS""": 0.2,
                    }
                )
            )[0]
            payload = {
                "title": self.faker.sentence(3),
                "resumable": self.faker.pybool(),
                "description": self.faker.sentence(16),
                "duration": duration,
            }
            response = self.session.post(
                f"{self.base_url}/quiz/", json=payload, headers=self.headers
            )
            try:
                response.raise_for_status()
            except HTTPError:
                logger.error(payload)
                logger.error(response.text)
                raise
            yield response.json()

    def generate_questions(self, quiz_id: UUID, n: int = 10):
        for _ in range(n):
            duration = self.faker.random_choices(
                OrderedDict(
                    {
                        None: 0.8,
                        f"""{self.faker.pyfloat(
                    positive=True,
                    right_digits=2,
                    min_value=0.1,
                    max_value=0.5
                )} HOURS""": 0.2,
                    }
                )
            )[0]
            payload = {
                "question_text": self.faker.sentence(16),
                "duration": duration,
                "resumable": self.faker.pybool(),
            }
            response = self.session.post(
                f"{self.base_url}/question/quiz/{quiz_id}",
                json=payload,
                headers=self.headers,
            )
            try:
                response.raise_for_status()
            except HTTPError:
                logger.error(payload)
                logger.error(response.text)
                raise
            yield response.json()

    def generate_answers(self, question_id: UUID, n: int = 5):
        for _ in range(n):
            payload = {
                "answer_text": self.faker.sentence(3),
                "is_correct": self.faker.pybool(),
            }
            response = self.session.post(
                f"{self.base_url}/answer/question/{question_id}",
                json=payload,
                headers=self.headers,
            )
            try:
                response.raise_for_status()
            except HTTPError:
                logger.error(payload)
                logger.error(response.text)
                raise
            yield response.json()

    def publish_quizzes(self, quiz_ids: list[UUID]):
        quizzes = []
        for quiz_id in quiz_ids:
            response = self.session.put(
                f"{self.base_url}/quiz/publish/{quiz_id}", headers=self.headers
            )
            try:
                response.raise_for_status()
            except HTTPError:
                logger.error(response.text)
                raise
            quizzes.append(response.json())
        return quizzes

    def generate_submission(self, quiz_id: UUID):
        response = self.session.post(
            f"{self.base_url}/submission/quiz/{quiz_id}", headers=self.headers
        )
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error(response.text)
            raise
        submission = response.json()
        return submission

    def generate_attempt(self, submission_id: UUID, question_id: UUID):
        response = self.session.post(
            f"{self.base_url}/attempt/submission/"
            f"{submission_id}/question/{question_id}",
            headers=self.headers,
        )
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error(response.text)
            raise
        attempt = response.json()
        return attempt

    def generate_solution(self, attempt_id: UUID, answer_id: UUID):
        response = self.session.post(
            f"{self.base_url}/solution/attempt/"
            f"{attempt_id}/answer/{answer_id}",
            headers=self.headers,
        )
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error(response.text)
            raise
        solution = response.json()
        return solution

    def submit_attempt(self, attempt_id: UUID):
        response = self.session.put(
            f"{self.base_url}/attempt/submit/{attempt_id}",
            headers=self.headers,
        )
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error(response.text)
            raise
        attempt = response.json()
        return attempt

    def submit_submission(self, submission_id: UUID):
        response = self.session.put(
            f"{self.base_url}/submission/submit/{submission_id}",
            headers=self.headers,
        )
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error(response.text)
            raise
        submission = response.json()
        return submission


if __name__ == "__main__":
    test = UseCaseTest()
    logger.info("Add 10 users")
    test.add_users(10)
    logger.info("Login as the first user to be a quiz maker")
    quiz_maker = list(test.email_passwords.items())[0][0]
    test.login(quiz_maker)
    logger.info("Generate 5 Quizzes")
    published_quizzes = []
    quiz_generator = test.generate_quizzes(5)
    quizzes = []
    questions = {}
    answers = {}
    for quiz in quiz_generator:
        quizzes.append(quiz)
        logger.info("Quiz ID: %s" % quiz["id"])
        question_number = test.faker.random_int(5, 10)
        logger.info("Generate %d for quiz %s" % (question_number, quiz["id"]))
        question_generator = test.generate_questions(
            quiz["id"], question_number
        )
        for question in question_generator:
            if quiz["id"] in questions:
                questions[quiz["id"]].append(question)
            else:
                questions[quiz["id"]] = [question]
            logger.info("Question ID: %s" % question["id"])
            answer_number = test.faker.random_int(3, 5)
            logger.info(
                "Generate %d for quiz %s" % (answer_number, question["id"])
            )
            answer_generator = test.generate_answers(
                question["id"], answer_number
            )
            for answer in answer_generator:
                if quiz["id"] in answers:
                    if question["id"] in answers[quiz["id"]]:
                        answers[quiz["id"]][question["id"]].append(answer)
                    else:
                        answers[quiz["id"]][question["id"]] = [answer]
                else:
                    answers[quiz["id"]] = {question["id"]: [answer]}
                logger.info("Answer ID: %s" % answer["id"])
        if test.faker.pybool():
            published_quizzes.append(quiz["id"])
    test.publish_quizzes(published_quizzes)
    for email in test.email_passwords.keys():
        logger.info("Login as %s" % email)
        test.login(email)
        for quiz_id in published_quizzes:
            logger.info(
                "%s make a draft submission to quiz %s" % (email, quiz_id)
            )
            submission = test.generate_submission(quiz_id)
            for question in questions[quiz_id]:
                logger.info(
                    "%s attempt to question %s" % (email, question["id"])
                )
                attempt = test.generate_attempt(
                    submission["id"], question["id"]
                )
                for answer in answers[quiz_id][question["id"]]:
                    if test.faker.pybool():
                        logger.info(
                            "%s answer with %s" % (email, answer["id"])
                        )
                        solution = test.generate_solution(
                            attempt["id"], answer["id"]
                        )
                attempt = test.submit_attempt(attempt["id"])
                logger.info(
                    "%s submitted attempt %s with score %.2f"
                    % (email, attempt["id"], attempt["score"] or 0)
                )
            submission = test.submit_submission(submission["id"])
            logger.info(
                "%s submitted to quiz %s with score %.2f"
                % (email, quiz_id, submission["score"] or 0)
            )
