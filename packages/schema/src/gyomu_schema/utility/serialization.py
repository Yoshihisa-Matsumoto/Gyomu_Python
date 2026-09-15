from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from returns.result import Failure, Result, Success

from gyomu_schema.error.validation import ValidationError


def dump_json(
    value: BaseModel,
    *,
    indent: int | None = None,
) -> str:
    return value.model_dump_json(indent=indent)


def validate_json[T: BaseModel](
    model_type: type[T], data: str
) -> Result[T, ValidationError]:
    try:
        return Success(model_type.model_validate_json(data))
    except PydanticValidationError as error:
        return Failure(
            ValidationError(
                "Failed to validate JSON.",
                details={"errors": error.errors()},
                context="serialization.validate_json",
                input=data,
            ).chain(error)
        )


def _assert_json_round_trip[T: BaseModel](
    model_type: type[T],
    value: T,
) -> None:

    data = dump_json(value)
    result = validate_json(model_type, data)

    if isinstance(result, Failure):
        print(str(result.failure()))
        raise AssertionError(result.failure())

    assert isinstance(result, Success)
    assert result.unwrap() == value
