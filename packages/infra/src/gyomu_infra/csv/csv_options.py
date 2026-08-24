from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class CsvHeaderField:
    header: str
    name: str


@dataclass(frozen=True)
class CsvIndexField:
    index: int
    name: str


@dataclass(frozen=True)
class CsvHeaderMode:
    fields: tuple[CsvHeaderField, ...] | None = None


@dataclass(frozen=True)
class CsvNoHeaderMode:
    fields: tuple[CsvIndexField, ...] | None = None


type CsvColumnMode = CsvHeaderMode | CsvNoHeaderMode


@dataclass(frozen=True)
class CsvParseOptions:
    delimiter: str = ","
    quotechar: str = '"'
    doublequote: bool = True
    escapechar: str | None = None
    skipinitialspace: bool = False
    strict: bool = True
    columns: CsvColumnMode = CsvHeaderMode()


@dataclass(frozen=True)
class CsvEncodingOptions:
    utf8_bom: bool = False
    encoding: str = "utf-8"


@dataclass(frozen=True)
class CsvIOOptions(CsvParseOptions, CsvEncodingOptions):
    filter_raw: Callable[[dict[str, str]], bool] | None = None


@dataclass(frozen=True)
class CsvReadOptions[T](CsvIOOptions):
    filter: Callable[[T], bool] | None = None


@dataclass(frozen=True)
class CsvWriteOptions:
    delimiter: str = ","
    quotechar: str = '"'
    doublequote: bool = True
    escapechar: str | None = None
    columns: dict[str, str] | None = None
    utf8_bom: bool = False
    encoding: str = "utf-8"
    lineterminator: str = "\r\n"
