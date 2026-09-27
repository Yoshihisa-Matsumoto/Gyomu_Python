from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class CsvHeaderField:
    """Represents a mapping between a CSV header name and a target field name."""

    header: str
    """CSV header name."""

    name: str
    """Target field name."""


@dataclass(frozen=True)
class CsvIndexField:
    """Represents a mapping between a CSV column index and a target field name."""

    index: int
    """CSV column index."""

    name: str
    """Target field name."""


@dataclass(frozen=True)
class CsvHeaderMode:
    """Specifies CSV header-based column mapping options."""

    fields: tuple[CsvHeaderField, ...] | None = None
    """Collection of header field mappings."""


@dataclass(frozen=True)
class CsvNoHeaderMode:
    """Specifies CSV index-based column mapping options when headers are absent."""

    fields: tuple[CsvIndexField, ...] | None = None
    """Collection of index field mappings."""


type CsvColumnMode = CsvHeaderMode | CsvNoHeaderMode
"""Type alias representing either header-based or index-based CSV column modes."""


@dataclass(frozen=True)
class CsvParseOptions:
    """Defines configuration options for parsing CSV inputs."""

    delimiter: str = ","
    """Field separator delimiter string."""

    quotechar: str = '"'
    """Quote character for fields containing special characters."""

    doublequote: bool = True
    """Indicates whether quotes inside fields should be doubled."""

    escapechar: str | None = None
    """Character used to escape other characters."""

    skipinitialspace: bool = False
    """Indicates whether whitespace immediately following the delimiter should be
    ignored.
    """
    strict: bool = True
    """Indicates whether bad CSV input should raise an exception."""

    columns: CsvColumnMode = CsvHeaderMode()
    """Column mapping configuration mode."""


@dataclass(frozen=True)
class CsvEncodingOptions:
    """Defines character encoding configuration options for CSV operations."""

    utf8_bom: bool = False
    """Indicates whether UTF-8 BOM should be included or expected."""

    encoding: str = "utf-8"
    """Character encoding string."""


@dataclass(frozen=True)
class CsvIOOptions(CsvParseOptions, CsvEncodingOptions):
    """Defines combined parsing and encoding options for CSV input/output operations."""

    filter_raw: Callable[[dict[str, str]], bool] | None = None
    """Optional callback to filter raw dictionary rows."""


@dataclass(frozen=True)
class CsvReadOptions[T](CsvIOOptions):
    """Defines configuration options for reading CSV data into typed objects."""

    filter: Callable[[T], bool] | None = None
    """Optional callback to filter parsed objects."""


@dataclass(frozen=True)
class CsvWriteOptions:
    """Defines configuration options for serializing objects to CSV format."""

    delimiter: str = ","
    """Field separator delimiter string."""

    quotechar: str = '"'
    """Quote character for fields containing special characters."""

    doublequote: bool = True
    """Indicates whether quotes inside fields should be doubled."""

    escapechar: str | None = None
    """Character used to escape other characters."""

    columns: dict[str, str] | None = None
    """Mapping of field names to CSV column headers."""

    utf8_bom: bool = False
    """Indicates whether to write a UTF-8 BOM at the start of the output."""

    encoding: str = "utf-8"
    """Character encoding string."""

    lineterminator: str = "\r\n"
    """Line terminator string used for output rows."""
