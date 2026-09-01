from griffe import Object
from gyomu_python_analysis.analysis.analyzers.internal.location import (
    calculate_member_location,
    calculate_symbol_location,
)
from gyomu_python_analysis.analysis.analyzers.internal.visibility import (
    calculate_visibility,
)
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.member_analysis import MemberCommon
from gyomu_schema.schemas.python.symbol_base import SymbolCommon


def build_symbol_common(
    symbol: Object,
    name: str,
    source_lines: list[str],
) -> SymbolCommon:
    location = calculate_symbol_location(
        symbol=symbol,
        source_lines=source_lines,
    )
    return {
        "name": name,
        "location": location,
        "visibility": calculate_visibility(name),
        "indent": location.start_column,
    }


def build_member_common(
    symbol: Object,
    name: str,
    source_lines: list[str],
    parent_location: SourceLocation | None = None,
) -> MemberCommon:
    location = calculate_member_location(
        symbol=symbol,
        source_lines=source_lines,
        parent_location=parent_location,
    )
    return {
        "name": name,
        "location": location,
        "visibility": calculate_visibility(name),
        "indent": location.start_column if location is not None else None,
    }
