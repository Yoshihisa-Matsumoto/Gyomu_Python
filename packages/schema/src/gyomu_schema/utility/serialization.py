from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from returns.result import Failure, Result, Success

from gyomu_schema.error.validation import ValidationError


def dump_json(value: BaseModel) -> str:
    return value.model_dump_json()


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
