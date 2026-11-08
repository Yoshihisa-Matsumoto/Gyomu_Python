import pytest
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext

from packages.schema.test_support.helpers import (
    simple_create_declaration_identity,
)


@pytest.fixture
def context() -> SymbolContext:
    return SymbolContext(
        declaration=simple_create_declaration_identity("test"),
        dependencies=[],
        source_lines=[],
        line_start_offsets=[],
    )
