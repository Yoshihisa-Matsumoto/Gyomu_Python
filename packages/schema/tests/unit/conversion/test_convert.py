from gyomu_schema.convert import convert, convert_json
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.error.validation import ValidationError
from pydantic import BaseModel


class Customer(BaseModel):
    name: str
    age: int


class TestConvert:
    def test_converts_object_to_schema(self) -> None:
        result = convert(
            Customer,
            {
                "name": "John",
                "age": "30",
            },
        )

        assert result.unwrap() == Customer(
            name="John",
            age=30,
        )

    def test_returns_validation_error_for_invalid_input(self) -> None:
        result = convert(
            Customer,
            {
                "name": "John",
                "age": "invalid",
            },
        )

        assert result.failure() is not None
        error = result.failure()

        assert isinstance(error, ValidationError)
        assert error.input == {
            "name": "John",
            "age": "invalid",
        }

    def test_preserves_pydantic_validation_details(self) -> None:
        result = convert(
            Customer,
            {
                "name": "John",
                "age": "invalid",
            },
        )

        error = result.failure()

        assert isinstance(error, ValidationError)
        assert error.details is not None
        assert "issues" in error.details

        issues = error.details["issues"]

        assert isinstance(issues, list)
        assert len(issues) == 1
        assert issues[0]["loc"] == ("age",)
        assert issues[0]["type"] == "int_parsing"


class TestConvertJson:
    def test_converts_json_to_schema(self) -> None:
        result = convert_json(
            Customer,
            '{"name": "John", "age": 30}',
        )

        assert result.unwrap() == Customer(
            name="John",
            age=30,
        )

    def test_applies_pydantic_type_conversion(self) -> None:
        result = convert_json(
            Customer,
            '{"name": "John", "age": "30"}',
        )

        assert result.unwrap() == Customer(
            name="John",
            age=30,
        )

    def test_returns_validation_error_for_invalid_schema(self) -> None:
        result = convert_json(
            Customer,
            '{"name": "John", "age": "invalid"}',
        )

        error = result.failure()

        assert isinstance(error, ValidationError)

    def test_returns_io_error_for_invalid_json(self) -> None:
        result = convert_json(
            Customer,
            '{"name": "John", "age":',
        )

        error = result.failure()

        assert isinstance(error, GyomuIOError)

    def test_invalid_json_preserves_original_exception_as_cause(self) -> None:
        result = convert_json(
            Customer,
            '{"name": "John", "age":',
        )

        error = result.failure()

        assert isinstance(error, GyomuIOError)
        assert error.__cause__ is not None
        assert isinstance(error.__cause__, ValueError)
