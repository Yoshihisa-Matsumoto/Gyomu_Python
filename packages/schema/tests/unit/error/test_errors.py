import pytest
from gyomu_schema.error.base import BaseError
from gyomu_schema.error.database import DatabaseError
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.error.validation import ValidationError


def test_error_can_preserve_cause() -> None:
    cause = ValueError("invalid configuration")

    with pytest.raises(GyomuIOError) as exc_info:
        try:
            raise cause
        except ValueError as error:
            raise GyomuIOError(
                "Invalid configuration",
                context="test",
            ).chain(error)

    assert exc_info.value.__cause__ is cause


def test_config_error_is_base_error() -> None:
    error = GyomuIOError("invalid configuration")

    assert isinstance(error, BaseError)
    assert isinstance(error, Exception)


def test_database_error_is_gyomu_io_error() -> None:
    error = DatabaseError("database error")

    assert isinstance(error, GyomuIOError)
    assert isinstance(error, BaseError)
    assert isinstance(error, Exception)


def test_validation_error_is_base_error() -> None:
    error = ValidationError("invalid value")

    assert isinstance(error, BaseError)


def test_gyomu_io_error_is_base_error() -> None:
    error = GyomuIOError("I/O error")

    assert isinstance(error, BaseError)
