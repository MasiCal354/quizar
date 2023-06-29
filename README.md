# Quiz Builder API

## Flow

- [Demo Video](https://drive.google.com/file/d/15i6UgvEw1ivcI02Y8FQsC2I6ZCXuMk7R/view?usp=sharing)

### Quiz Creation

1. User Register
2. User Login
3. User Create Quiz
4. User Create Questions for quiz
5. User Create Answers for each question
6. User Publish Quiz

### Submission

1. User Register
2. User Login
3. User Create Submission Draft for quiz
4. User Create Attempt for each question
5. User Create Solution
6. User Undraft Submission

## Requirements

- Python: 3.10.10
- Poetry: 1.4.2
- Docker: 20.10.22
- Docker Compose: v2.15.1

## Execution

### Setup .env file

1. Create new file `.env`
2. Copy the content from `template.env`
3. Run `openssl rand -hex 32` to generate `POSTGRES_PASSWORD` and put the value there. Adjust the value on the `SQLALCHEMY_URL`.
4. Run `python` and run below script
```python
from secrets import token_urlsafe
print(token_urlsafe(64))
```
5. Copy the output and put it on `SECRET_KEY`

### Deploy Locally

```console
$ docker-compose up --build
$ docker-compose down
```

### Test Use Case

```console
$ python tests/usecase/main.py
```
