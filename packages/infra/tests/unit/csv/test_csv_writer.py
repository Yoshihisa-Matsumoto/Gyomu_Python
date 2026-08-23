from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel

from gyomu_infra.csv.csv_options import CsvWriteOptions
from gyomu_infra.csv.csv_write import CsvWriter, csv_to_file, csv_to_string


class Customer(BaseModel):
    name: str
    country: str
    age: int


class CustomerWithDate(BaseModel):
    name: str
    age: int


class TestCsvWriter:
    def test_writes_all_fields_by_default(self) -> None:
        writer = CsvWriter(
            schema=Customer,
        )

        records = [
            Customer(name="John", country="UK", age=30),
            Customer(name="Jane", country="US", age=25),
        ]

        result = b"".join(writer.stream(records))

        assert result == (b"name,country,age\r\nJohn,UK,30\r\nJane,US,25\r\n")

    def test_writes_selected_fields_with_mapped_headers(self) -> None:
        options = CsvWriteOptions(
            columns={
                "名前": "name",
                "年齢": "age",
            },
            lineterminator="\r\n",
        )

        writer = CsvWriter(
            schema=Customer,
            options=options,
        )

        records = [
            Customer(name="John", country="UK", age=30),
            Customer(name="Jane", country="US", age=25),
        ]

        result = b"".join(writer.stream(records))

        assert result == ("名前,年齢\r\nJohn,30\r\nJane,25\r\n").encode()

    def test_ignores_fields_not_in_mapping(self) -> None:
        options = CsvWriteOptions(
            columns={
                "名前": "name",
                "年齢": "age",
            },
            lineterminator="\r\n",
        )

        writer = CsvWriter(
            schema=Customer,
            options=options,
        )

        result = b"".join(
            writer.stream(
                [
                    Customer(
                        name="John",
                        country="UK",
                        age=30,
                    )
                ]
            )
        )

        assert result == ("名前,年齢\r\nJohn,30\r\n").encode()

    def test_writes_header_for_empty_records(self) -> None:
        writer = CsvWriter(
            schema=Customer,
        )

        result = b"".join(writer.stream([]))

        assert result == b"name,country,age\r\n"

    def test_writes_mapped_header_for_empty_records(self) -> None:
        options = CsvWriteOptions(
            columns={
                "名前": "name",
                "年齢": "age",
            },
            lineterminator="\r\n",
        )

        writer = CsvWriter(
            schema=Customer,
            options=options,
        )

        result = b"".join(writer.stream([]))
        assert result == ("名前,年齢\r\n").encode()

    def test_writes_utf8_bom(self) -> None:
        options = CsvWriteOptions(
            utf8_bom=True,
            lineterminator="\r\n",
        )

        writer = CsvWriter(
            schema=Customer,
            options=options,
        )

        result = b"".join(
            writer.stream(
                [
                    Customer(
                        name="John",
                        country="UK",
                        age=30,
                    )
                ]
            )
        )

        assert result == (b"\xef\xbb\xbfname,country,age\r\nJohn,UK,30\r\n")

    def test_does_not_write_utf8_bom_by_default(self) -> None:
        writer = CsvWriter(
            schema=Customer,
        )

        result = b"".join(
            writer.stream(
                [
                    Customer(
                        name="John",
                        country="UK",
                        age=30,
                    )
                ]
            )
        )

        assert not result.startswith(b"\xef\xbb\xbf")

    def test_uses_custom_delimiter(self) -> None:
        options = CsvWriteOptions(
            delimiter=";",
            lineterminator="\r\n",
        )

        writer = CsvWriter(
            schema=Customer,
            options=options,
        )

        result = b"".join(
            writer.stream(
                [
                    Customer(
                        name="John",
                        country="UK",
                        age=30,
                    )
                ]
            )
        )

        assert result == (b"name;country;age\r\nJohn;UK;30\r\n")

    def test_quotes_values_when_required(self) -> None:
        writer = CsvWriter(
            schema=Customer,
        )

        result = b"".join(
            writer.stream(
                [
                    Customer(
                        name="John, Jr.",
                        country="UK",
                        age=30,
                    )
                ]
            )
        )

        assert result == (b'name,country,age\r\n"John, Jr.",UK,30\r\n')

    def test_uses_custom_quotechar(self) -> None:
        options = CsvWriteOptions(
            quotechar="'",
            lineterminator="\r\n",
        )

        writer = CsvWriter(
            schema=Customer,
            options=options,
        )

        result = b"".join(
            writer.stream(
                [
                    Customer(
                        name="John, Jr.",
                        country="UK",
                        age=30,
                    )
                ]
            )
        )

        assert result == (b"name,country,age\r\n'John, Jr.',UK,30\r\n")

    def test_uses_custom_encoding(self) -> None:
        writer = CsvWriter(
            schema=Customer,
            options=CsvWriteOptions(
                encoding="utf-16",
                lineterminator="\r\n",
            ),
        )

        result = b"".join(
            writer.stream(
                [
                    Customer(
                        name="山田太郎",
                        country="JP",
                        age=30,
                    )
                ]
            )
        )

        expected = ("name,country,age\r\n山田太郎,JP,30\r\n").encode("utf-16")

        assert result == expected

    def test_stream_is_lazy(self) -> None:
        consumed: list[int] = []

        def records() -> Iterator[Customer]:
            for index in range(3):
                consumed.append(index)

                yield Customer(
                    name=f"Customer{index}",
                    country="JP",
                    age=index,
                )

        writer = CsvWriter(
            schema=Customer,
        )

        stream = writer.stream(records())

        # Generator creation alone must not consume input records.
        assert consumed == []

        first = next(stream)

        # The header is emitted before the first record.
        assert first == b"name,country,age\r\n"
        assert consumed == []

        second = next(stream)

        assert second == b"Customer0,JP,0\r\n"
        assert consumed == [0]

        third = next(stream)

        assert third == b"Customer1,JP,1\r\n"
        assert consumed == [0, 1]

    def test_preserves_record_order(self) -> None:
        writer = CsvWriter(
            schema=Customer,
        )

        records = (
            Customer(name=f"Customer{i}", country="JP", age=i) for i in range(100)
        )

        result = b"".join(writer.stream(records))

        lines = result.decode("utf-8").splitlines()

        assert lines[0] == "name,country,age"
        assert lines[1] == "Customer0,JP,0"
        assert lines[50] == "Customer49,JP,49"
        assert lines[100] == "Customer99,JP,99"

    def test_uses_json_mode_for_serialization(self) -> None:
        from datetime import date

        class CustomerWithDate(BaseModel):
            name: str
            birthday: date

        writer = CsvWriter(
            schema=CustomerWithDate,
        )

        result = b"".join(
            writer.stream(
                [
                    CustomerWithDate(
                        name="John",
                        birthday=date(2026, 8, 23),
                    )
                ]
            )
        )

        assert result == (b"name,birthday\r\nJohn,2026-08-23\r\n")


class TestCsvToFile:
    def test_csv_to_file_writes_csv(
        self,
        tmp_path: Path,
    ) -> None:
        file_path = tmp_path / "customers.csv"

        csv_to_file(
            records=[
                Customer(name="John", country="UK", age=30),
                Customer(name="Jane", country="US", age=25),
            ],
            schema=Customer,
            file_path=file_path,
        )

        assert file_path.read_bytes() == (
            b"name,country,age\r\nJohn,UK,30\r\nJane,US,25\r\n"
        )

    def test_csv_to_file_uses_column_mapping(
        self,
        tmp_path: Path,
    ) -> None:
        file_path = tmp_path / "customers.csv"

        csv_to_file(
            records=[
                Customer(name="John", country="UK", age=30),
            ],
            schema=Customer,
            file_path=file_path,
            options=CsvWriteOptions(
                columns={
                    "名前": "name",
                    "年齢": "age",
                }
            ),
        )

        assert file_path.read_bytes() == ("名前,年齢\r\nJohn,30\r\n").encode()


class TestCsvToString:
    def test_csv_to_string_writes_csv(self) -> None:
        result = csv_to_string(
            records=[
                Customer(name="John", country="UK", age=30),
                Customer(name="Jane", country="US", age=25),
            ],
            schema=Customer,
        )

        assert result == ("name,country,age\r\nJohn,UK,30\r\nJane,US,25\r\n")

    def test_csv_to_string_uses_column_mapping(self) -> None:
        result = csv_to_string(
            records=[
                Customer(name="John", country="UK", age=30),
            ],
            schema=Customer,
            options=CsvWriteOptions(
                columns={
                    "名前": "name",
                    "年齢": "age",
                }
            ),
        )

        assert result == ("名前,年齢\r\nJohn,30\r\n")

    def test_csv_to_string_writes_header_for_empty_records(self) -> None:
        result = csv_to_string(
            records=[],
            schema=Customer,
        )

        assert result == "name,country,age\r\n"

    def test_csv_to_string_includes_utf8_bom(self) -> None:
        result = csv_to_string(
            records=[
                Customer(name="John", country="UK", age=30),
            ],
            schema=Customer,
            options=CsvWriteOptions(
                utf8_bom=True,
            ),
        )

        assert result == ("\ufeffname,country,age\r\nJohn,UK,30\r\n")
