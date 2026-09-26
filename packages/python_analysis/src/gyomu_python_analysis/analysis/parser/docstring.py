from typing import Protocol

from gyomu_schema.schemas.python.docstring import DocstringAnalysis


class DocstringParser(Protocol):
    """Protocol defining a parser for docstrings into analysis results."""

    def parse(self, value: str) -> DocstringAnalysis: ...
