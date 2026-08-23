from io import StringIO

from gyomu_schema.error.validation import ValidationError
from pydantic import BaseModel

from gyomu_infra.csv.csv_options import (
    CsvReadOptions,
)
from gyomu_infra.csv.csv_reader import CsvReader


class Customer(BaseModel):
    name: str
    age: int


class TestCsvReader:
    def test_reads_and_converts_records(self) -> None:
        stream = StringIO("name,age\nJohn,30\nJane,25\n")

        reader = CsvReader(
            stream,
            schema=Customer,
        )

        results = reader.records().collect()

        assert results[0].unwrap() == Customer(
            name="John",
            age=30,
        )

        assert results[1].unwrap() == Customer(
            name="Jane",
            age=25,
        )

    def test_converts_string_values_to_schema_types(self) -> None:
        stream = StringIO("name,age\nJohn,30\n")

        reader = CsvReader(
            stream,
            schema=Customer,
        )

        result = reader.records().collect()[0]

        customer = result.unwrap()

        assert customer.name == "John"
        assert customer.age == 30
        assert isinstance(customer.age, int)

    def test_returns_validation_error_for_invalid_record(self) -> None:
        stream = StringIO("name,age\nJohn,invalid\n")

        reader = CsvReader(
            stream,
            schema=Customer,
        )

        results = reader.records().collect()

        assert len(results) == 1

        error = results[0].failure()

        assert isinstance(error, ValidationError)

    def test_continues_after_validation_failure(self) -> None:
        stream = StringIO("name,age\nJohn,30\nInvalid,xxx\nJane,25\n")

        reader = CsvReader(
            stream,
            schema=Customer,
        )

        results = reader.records().collect()

        assert len(results) == 3

        assert results[0].unwrap() == Customer(
            name="John",
            age=30,
        )

        assert isinstance(
            results[1].failure(),
            ValidationError,
        )

        assert results[2].unwrap() == Customer(
            name="Jane",
            age=25,
        )

    def test_filter_filters_converted_records(self) -> None:
        stream = StringIO("name,age\nJohn,30\nJane,25\nBob,20\n")

        reader = CsvReader(
            stream,
            schema=Customer,
            options=CsvReadOptions(
                filter=lambda row: row.age >= 25,
            ),
        )

        results = reader.records().collect()

        assert [result.unwrap().name for result in results] == [
            "John",
            "Jane",
        ]

    def test_filter_preserves_validation_failure(self) -> None:
        stream = StringIO("name,age\nJohn,30\nInvalid,not-a-number\nJane,25\n")

        reader = CsvReader(
            stream,
            schema=Customer,
            options=CsvReadOptions(
                filter=lambda row: row.age >= 25,
            ),
        )

        results = reader.records().collect()

        assert len(results) == 3

        assert results[0].unwrap().name == "John"
        assert results[1].failure()  # ValidationError
        assert results[2].unwrap().name == "Jane"

    def test_filter_raw_is_applied_before_conversion(self) -> None:
        stream = StringIO("name,age\nJohn,30\nJane,25\n")

        reader = CsvReader(
            stream,
            schema=Customer,
            options=CsvReadOptions(
                filter_raw=lambda row: row["age"] == "30",
            ),
        )

        results = reader.records().collect()

        assert len(results) == 1
        assert results[0].unwrap() == Customer(
            name="John",
            age=30,
        )
