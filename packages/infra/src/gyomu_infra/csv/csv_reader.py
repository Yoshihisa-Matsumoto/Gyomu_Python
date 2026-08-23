import codecs
import csv
from collections.abc import Iterator
from io import TextIOBase
from typing import BinaryIO, TextIO, cast

from gyomu_schema.convert import convert
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.error.validation import ValidationError
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_infra.csv.csv_options import (
    CsvHeaderMode,
    CsvIOOptions,
    CsvNoHeaderMode,
    CsvParseOptions,
    CsvReadOptions,
)
from gyomu_infra.stream.record_stream import RecordStream


class CsvReader[T: BaseModel]:
    def __init__(
        self,
        stream: BinaryIO | TextIO,
        *,
        schema: type[T],
        options: CsvReadOptions[T] | None = None,
    ) -> None:
        self.stream = stream
        self.schema = schema
        self.options = options

    def records(self) -> RecordStream[T, GyomuIOError | ValidationError]:
        raw = RecordStream(
            _parse_raw_records(
                self.stream,
                self.options,
            )
        )

        result = raw.map_result(lambda row: convert(self.schema, row))

        if self.options is not None and self.options.filter is not None:
            result = result.filter(self.options.filter)

        return result


class CsvRawReader:
    def __init__(
        self,
        stream: BinaryIO | TextIO,
        *,
        options: CsvReadOptions[dict[str, str]] | None = None,
    ) -> None:
        self.stream = stream
        self.options = options

    def records(
        self,
    ) -> RecordStream[dict[str, str], GyomuIOError]:

        return RecordStream(_parse_raw_records(self.stream, self.options))


def _parse_raw_records(
    stream: BinaryIO | TextIO,
    options: CsvIOOptions | None,
) -> Iterator[Result[dict[str, str], GyomuIOError]]:
    options = options or CsvIOOptions()

    try:
        for row in _parse_csv(
            _text_stream(
                stream,
                options.encoding,
                options.utf8_bom,
            ),
            options,
        ):
            if options.filter_raw is not None and not options.filter_raw(row):
                continue

            yield Success(row)

    except csv.Error as exc:
        error = GyomuIOError(message="Failed to parse CSV")
        error.__cause__ = exc
        yield Failure(error)


def _text_stream(stream: TextIO | BinaryIO, encoding: str, utf8_bom: bool) -> TextIO:
    if isinstance(stream, (TextIOBase, TextIO)):
        return stream

    target_encoding = "utf-8-sig" if utf8_bom else encoding
    return cast(TextIO, codecs.getreader(target_encoding)(stream))


def _parse_csv(
    stream: TextIO,
    options: CsvParseOptions,
) -> Iterator[dict[str, str]]:

    reader = csv.reader(
        stream,
        delimiter=options.delimiter,
        quotechar=options.quotechar,
        doublequote=options.doublequote,
        escapechar=options.escapechar,
        skipinitialspace=options.skipinitialspace,
        strict=options.strict,
    )

    if isinstance(options.columns, CsvHeaderMode):
        header = next(reader)

        header_index = {name: index for index, name in enumerate(header)}

        for row in reader:
            yield _map_header_row(row, header_index, options.columns)
    else:
        for row in reader:
            yield _map_index_row(row, options.columns)


def _map_header_row(
    row: list[str],
    header_index: dict[str, int],
    columns: CsvHeaderMode,
) -> dict[str, str]:
    if columns.fields is None:
        return {
            header: row[index]
            for header, index in header_index.items()
            if index < len(row)
        }

    return {
        field.name: row[header_index[field.header]]
        for field in columns.fields
        if field.header in header_index and header_index[field.header] < len(row)
    }


def _map_index_row(
    row: list[str],
    columns: CsvNoHeaderMode,
) -> dict[str, str]:
    if columns.fields is None:
        return {f"COLUMN{index}": value for index, value in enumerate(row)}

    return {
        field.name: row[field.index]
        for field in columns.fields
        if field.index < len(row)
    }
