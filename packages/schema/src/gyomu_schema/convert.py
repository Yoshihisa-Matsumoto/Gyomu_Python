import json
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from returns.result import Failure, Result, Success

from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.error.validation import ValidationError

T = TypeVar("T", bound=BaseModel)


def convert(
    schema: type[T],
    value: object,
) -> Result[T, ValidationError]:
    try:
        return Success(schema.model_validate(value))
    except PydanticValidationError as exc:
        return Failure(
            ValidationError(
                message="Schema validation failed",
                input=value,
                details={
                    "issues": exc.errors(),
                },
            ).chain(exc)
        )


def convert_json(
    schema: type[T],
    content: str,
) -> Result[T, GyomuIOError | ValidationError]:
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        return Failure(GyomuIOError("Fail to load JSON").chain(exc))

    return convert(schema, value)
