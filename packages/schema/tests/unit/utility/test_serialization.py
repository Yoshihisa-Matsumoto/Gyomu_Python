from gyomu_schema.error.validation import ValidationError
from gyomu_schema.utility.serialization import (
    _assert_json_round_trip,
    dump_json,
    validate_json,
)
from pydantic import BaseModel
from returns.result import Failure, Success


class User(BaseModel):
    id: int
    name: str


def test_dump_json() -> None:
    user = User(id=1, name="Alice")

    result = dump_json(user, User)

    assert result == '{"id":1,"name":"Alice"}'


def test_dump_json_array() -> None:
    user = User(id=1, name="Alice")
    user2 = User(id=2, name="Matt")

    result = dump_json([user, user2], list[User])

    assert result == '[{"id":1,"name":"Alice"},{"id":2,"name":"Matt"}]'

    _assert_json_round_trip(list[User], [user, user2])


def test_dump_json_tuple() -> None:
    user = User(id=1, name="Alice")
    user2 = User(id=2, name="Matt")

    result = dump_json((user, user2), tuple[User, ...])

    assert result == '[{"id":1,"name":"Alice"},{"id":2,"name":"Matt"}]'
    _assert_json_round_trip(tuple[User, ...], (user, user2))


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
