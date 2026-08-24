from io import StringIO

from gyomu_schema.error.io import GyomuIOError

from gyomu_infra.csv.csv_options import (
    CsvHeaderField,
    CsvHeaderMode,
    CsvIndexField,
    CsvNoHeaderMode,
    CsvReadOptions,
)
from gyomu_infra.csv.csv_reader import CsvRawReader


class TestCsvRawReader:
    def test_reads_csv_records(self) -> None:
        stream = StringIO("name,age\nJohn,30\nJane,25\n")

        reader = CsvRawReader(stream)

        results = reader.records().collect()

        assert len(results) == 2

        assert results[0].unwrap() == {
            "name": "John",
            "age": "30",
        }

        assert results[1].unwrap() == {
            "name": "Jane",
            "age": "25",
        }

    def test_supports_custom_delimiter(self) -> None:
        stream = StringIO("name;age\nJohn;30\nJane;25\n")

        reader = CsvRawReader(
            stream,
            options=CsvReadOptions(delimiter=";"),
        )

        results = reader.records().collect()

        assert results[0].unwrap() == {
            "name": "John",
            "age": "30",
        }

    def test_supports_quoted_fields(self) -> None:
        stream = StringIO('name,address\n"John","Tokyo, Japan"\n')

        reader = CsvRawReader(stream)

        results = reader.records().collect()

        assert results[0].unwrap() == {
            "name": "John",
            "address": "Tokyo, Japan",
        }

    def test_returns_io_error_for_invalid_csv(self) -> None:
        stream = StringIO('name,age\n"John,30\n')

        reader = CsvRawReader(stream)

        results = reader.records().collect()

        assert len(results) == 1

        error = results[0].failure()

        assert isinstance(error, GyomuIOError)
        assert error.__cause__ is not None

    def test_header_mode_without_fields_uses_all_columns(self) -> None:
        stream = StringIO("名前,国,年齢\nJohn,UK,30\nJane,US,25\n")

        reader = CsvRawReader(
            stream,
            options=CsvReadOptions(
                columns=CsvHeaderMode(),
            ),
        )

        results = reader.records().collect()

        assert results[0].unwrap() == {
            "名前": "John",
            "国": "UK",
            "年齢": "30",
        }

        assert results[1].unwrap() == {
            "名前": "Jane",
            "国": "US",
            "年齢": "25",
        }

    def test_header_mode_with_fields_maps_selected_columns(self) -> None:
        stream = StringIO("名前,国,年齢\nJohn,UK,30\nJane,US,25\n")

        reader = CsvRawReader(
            stream,
            options=CsvReadOptions(
                columns=CsvHeaderMode(
                    fields=(
                        CsvHeaderField(
                            header="名前",
                            name="name",
                        ),
                        CsvHeaderField(
                            header="年齢",
                            name="age",
                        ),
                    ),
                ),
            ),
        )

        results = reader.records().collect()

        assert results[0].unwrap() == {
            "name": "John",
            "age": "30",
        }

        assert results[1].unwrap() == {
            "name": "Jane",
            "age": "25",
        }

    def test_no_header_mode_with_fields_maps_by_index(self) -> None:
        stream = StringIO("John,UK,30\nJane,US,25\n")

        reader = CsvRawReader(
            stream,
            options=CsvReadOptions(
                columns=CsvNoHeaderMode(
                    fields=(
                        CsvIndexField(
                            index=0,
                            name="name",
                        ),
                        CsvIndexField(
                            index=2,
                            name="age",
                        ),
                    ),
                ),
            ),
        )

        results = reader.records().collect()

        assert results[0].unwrap() == {
            "name": "John",
            "age": "30",
        }

        assert results[1].unwrap() == {
            "name": "Jane",
            "age": "25",
        }

    def test_no_header_mode_without_fields_uses_default_column_names(self) -> None:
        stream = StringIO("John,UK,30\nJane,US,25\n")

        reader = CsvRawReader(
            stream,
            options=CsvReadOptions(
                columns=CsvNoHeaderMode(),
            ),
        )

        results = reader.records().collect()

        assert results[0].unwrap() == {
            "COLUMN0": "John",
            "COLUMN1": "UK",
            "COLUMN2": "30",
        }

        assert results[1].unwrap() == {
            "COLUMN0": "Jane",
            "COLUMN1": "US",
            "COLUMN2": "25",
        }

    def test_header_mode_with_fields_ignores_unmapped_columns(self) -> None:
        stream = StringIO(
            "名前,国,部署,年齢\nJohn,UK,Sales,30\nJane,US,Engineering,25\n"
        )

        reader = CsvRawReader(
            stream,
            options=CsvReadOptions(
                columns=CsvHeaderMode(
                    fields=(
                        CsvHeaderField("名前", "name"),
                        CsvHeaderField("年齢", "age"),
                    ),
                ),
            ),
        )

        results = reader.records().collect()

        assert results[0].unwrap() == {
            "name": "John",
            "age": "30",
        }

        assert results[1].unwrap() == {
            "name": "Jane",
            "age": "25",
        }

    def test_filter_raw_filters_records(self) -> None:
        stream = StringIO("name,age\nJohn,30\nJane,25\nBob,20\n")

        reader = CsvRawReader(
            stream,
            options=CsvReadOptions(
                filter_raw=lambda row: int(row["age"]) >= 25,
            ),
        )

        results = reader.records().collect()

        assert len(results) == 2

        assert results[0].unwrap() == {
            "name": "John",
            "age": "30",
        }

        assert results[1].unwrap() == {
            "name": "Jane",
            "age": "25",
        }

    def test_filter_raw_receives_raw_string_values(self) -> None:
        stream = StringIO("name,age\nJohn,30\nJane,25\n")

        received: list[dict[str, str]] = []

        def filter_raw(row: dict[str, str]) -> bool:
            received.append(row)
            return True

        reader = CsvRawReader(
            stream,
            options=CsvReadOptions(
                filter_raw=filter_raw,
            ),
        )

        results = reader.records().collect()

        assert len(results) == 2
        assert received == [
            {"name": "John", "age": "30"},
            {"name": "Jane", "age": "25"},
        ]
