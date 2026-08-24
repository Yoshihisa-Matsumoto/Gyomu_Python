from collections.abc import Mapping
from typing import Protocol


class Logger(Protocol):
    def debug(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...

    def info(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...

    def warning(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...

    def error(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...

    def critical(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...

    def exception(
        self,
        message: str,
        *args: object,
        extra: Mapping[str, object] | None = None,
    ) -> None: ...
