from gyomu_schema.error.validation import ValidationError
from gyomu_schema.utility.serialization import dump_json, validate_json
from pydantic import BaseModel
from returns.result import Failure, Success


class User(BaseModel):
    id: int
    name: str


def test_dump_json() -> None:
    user = User(id=1, name="Alice")

    result = dump_json(user)

    assert result == '{"id":1,"name":"Alice"}'


def test_validate_json() -> None:
    data = '{"id":1,"name":"Alice"}'

    result = validate_json(User, data)

    assert isinstance(result, Success)
    assert result.unwrap() == User(id=1, name="Alice")


def test_validate_json_preserves_model_type() -> None:
    data = '{"id":1,"name":"Alice"}'

    result = validate_json(User, data)

    assert isinstance(result, Success)
    assert isinstance(result.unwrap(), User)


def test_validate_json_raises_validation_error() -> None:
    data = '{"id":"invalid","name":"Alice"}'

    result = validate_json(User, data)

    assert isinstance(result, Failure)
    detail = result.failure().details
    assert detail is not None
    assert "errors" in detail


def test_validate_json_does_not_expose_pydantic_validation_error() -> None:
    data = '{"id":"invalid","name":"Alice"}'

    result = validate_json(User, data)

    assert isinstance(result, Failure)
    assert isinstance(result.failure(), ValidationError)
