from pydantic import BaseModel, TypeAdapter
from pydantic import ValidationError as PydanticValidationError
from returns.result import Failure, Result, Success

from gyomu_schema.error.validation import ValidationError

type JsonableType = BaseModel | list[BaseModel] | tuple[BaseModel, ...]
"""   Type alias representing a Pydantic BaseModel or a collection of BaseModels."""


def dump_json[T](
    value: T,
    model_type: type[T],
    *,
    indent: int | None = None,
) -> str:
    """Serializes a value to a JSON string using Pydantic's TypeAdapter.

    Args:
        value (T): The value to serialize.
        model_type (type[T]): The model type of the value.
        indent (int | None): Optional indentation for formatting the JSON output.

    Returns:
        str: The JSON string representation of the value.
    """
    return (
        TypeAdapter(model_type)
        .dump_json(
            value,
            indent=indent,
        )
        .decode()
    )


def validate_json[T](model_type: type[T], data: str) -> Result[T, ValidationError]:
    """Validates JSON data against a given model type.

    Args:
        model_type (type[T]): The model type to validate against.
        data (str): The JSON string data to validate.

    Returns:
        Result[T, ValidationError]: A Result containing the validated model instance on
            success or a ValidationError on failure.
    """
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
    """Asserts that a value can be successfully serialized to JSON and deserialized back
    to an equivalent value.

    Args:
        model_type (type[T]): The model type of the value.
        value (T): The value to test in the round trip.
    """

    data = dump_json(value, model_type)
    result = validate_json(model_type, data)

    if isinstance(result, Failure):
        print(str(result.failure()))
        raise AssertionError(result.failure())

    assert isinstance(result, Success)
    assert result.unwrap() == value
