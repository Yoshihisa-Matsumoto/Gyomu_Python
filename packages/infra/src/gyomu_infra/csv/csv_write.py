import codecs
import csv
from collections.abc import Iterable, Iterator
from io import StringIO
from pathlib import Path

from pydantic import BaseModel

from gyomu_infra.csv.csv_options import CsvWriteOptions
from gyomu_infra.stream.stream_io import stream_to_file


class CsvWriter[T: BaseModel]:
    def __init__(
        self,
        *,
        schema: type[T],
        options: CsvWriteOptions | None = None,
    ) -> None:
        self.schema = schema
        self.options = options

    def stream(
        self,
        records: Iterable[T],
    ) -> Iterator[bytes]:
        options = self.options or CsvWriteOptions()
        encoder = codecs.getincrementalencoder(options.encoding)()

        field_names, headers = self._columns(options)

        if options.utf8_bom:
            yield b"\xef\xbb\xbf"

        if headers is not None:
            yield encoder.encode(
                self._csv_row(
                    headers,
                    options,
                ),
                final=False,
            )

        for record in records:
            row = record.model_dump(mode="json")

            values = [row[field_name] for field_name in field_names]

            yield encoder.encode(
                self._csv_row(
                    values,
                    options,
                ),
                final=False,
            )

    def _columns(
        self,
        options: CsvWriteOptions,
    ) -> tuple[list[str], list[str] | None]:
        fields = options.columns

        if fields is None:
            field_names = list(self.schema.model_fields.keys())
            return field_names, field_names

        field_names = list(fields.values())
        headers = list(fields.keys())

        return field_names, headers

    @staticmethod
    def _csv_row(
        row: list[object] | list[str],
        options: CsvWriteOptions,
    ) -> str:
        buffer = StringIO()

        writer = csv.writer(
            buffer,
            delimiter=options.delimiter,
            quotechar=options.quotechar,
            doublequote=options.doublequote,
            escapechar=options.escapechar,
            lineterminator=options.lineterminator,
        )

        writer.writerow(row)

        return buffer.getvalue()


def csv_to_string[T: BaseModel](
    records: Iterable[T],
    schema: type[T],
    options: CsvWriteOptions | None = None,
) -> str:
    options = options or CsvWriteOptions()
    writer = CsvWriter(schema=schema, options=options)
    return b"".join(writer.stream(records)).decode(options.encoding)


def csv_to_file[T: BaseModel](
    records: Iterable[T],
    schema: type[T],
    file_path: Path,
    options: CsvWriteOptions | None = None,
) -> None:
    writer = CsvWriter(
        schema=schema,
        options=options,
    )

    stream_to_file(
        writer.stream(records),
        file_path,
    )
