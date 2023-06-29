from pydantic import PydanticValueError
from pydantic.validators import str_validator
from pytimeparse.timeparse import timeparse


class InvalidIntervalStr(PydanticValueError):
    msg_template = "invalid interval string"


class IntervalStr(str):
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        if timeparse(v) is None:
            raise InvalidIntervalStr
        return cls(v)
