import pytest
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext

from packages.schema.schema_test_support.helpers import create_declaration_identity


@pytest.fixture
def context() -> SymbolContext:
    return SymbolContext(
        declaration=create_declaration_identity("test"),
        dependencies=[],
        source_lines=[],
        line_start_offsets=[],
    )
