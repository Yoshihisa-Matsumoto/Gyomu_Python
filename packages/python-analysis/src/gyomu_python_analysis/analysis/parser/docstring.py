from typing import Protocol

from gyomu_schema.schemas.python.docstring import DocstringAnalysis


class DocstringParser(Protocol):
    def parse(self, value: str) -> DocstringAnalysis: ...
