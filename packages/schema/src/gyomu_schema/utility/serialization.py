from pydantic import BaseModel, TypeAdapter
from pydantic import ValidationError as PydanticValidationError
from returns.result import Failure, Result, Success

from gyomu_schema.error.validation import ValidationError

type JsonableType = BaseModel | list[BaseModel] | tuple[BaseModel, ...]


def dump_json[T](
    value: T,
    model_type: type[T],
    *,
    indent: int | None = None,
) -> str:
    return (
        TypeAdapter(model_type)
        .dump_json(
            value,
            indent=indent,
        )
        .decode()
    )


def validate_json[T](model_type: type[T], data: str) -> Result[T, ValidationError]:
    try:
        return Success(TypeAdapter(model_type).validate_json(data))
    except PydanticValidationError as error:
        return Failure(
            ValidationError(
                "Failed to validate JSON.",
                details={"errors": error.errors()},
                context="serialization.validate_json",
                input=data,
            ).chain(error)
        )


def _assert_json_round_trip[T](
    model_type: type[T],
    value: T,
) -> None:

    data = dump_json(value, model_type)
    result = validate_json(model_type, data)

    if isinstance(result, Failure):
        print(str(result.failure()))
        raise AssertionError(result.failure())

    assert isinstance(result, Success)
    assert result.unwrap() == value
