import json

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from returns.result import Failure, Result, Success

from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.error.validation import ValidationError


def convert[T: BaseModel](
    schema: type[T],
    value: object,
) -> Result[T, ValidationError]:
    """Converts and validates an input value against a Pydantic model.

    Validates and converts a value into a Pydantic BaseModel instance.

    Args:
        schema (type[T]): The Pydantic model class to validate and convert into.
        value (object): The input value to validate.

    Returns:
        Result[T, ValidationError]: A Success containing the validated model instance,
            or a Failure containing a ValidationError if validation fails.
    """
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


def convert_json[T: BaseModel](
    schema: type[T],
    content: str,
) -> Result[T, GyomuIOError | ValidationError]:
    """Converts and validates a JSON string against a Pydantic model.

    Parses a JSON string and validates the resulting data against a Pydantic BaseModel
    instance.

    Args:
        schema (type[T]): The Pydantic model class to validate and convert into.
        content (str): The JSON string content to parse and validate.

    Returns:
        Result[T, GyomuIOError | ValidationError]: A Success containing the validated
            model instance, or a Failure containing a GyomuIOError or ValidationError if
            parsing or validation fails.
    """
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        return Failure(
            GyomuIOError(
                message="Fail to load JSON",
                layer=IOLayer.STREAM,
                operation=IOOperation.TRANSFORM,
                context="gyomu_schema.utility.searialization.convert_json",
            ).chain(exc)
        )

    return convert(schema, value)
