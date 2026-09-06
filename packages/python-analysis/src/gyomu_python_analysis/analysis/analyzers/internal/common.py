from griffe import Class, Docstring, Function, Object
from gyomu_schema.schemas.python.decorator import DecoratorAnalysis
from gyomu_schema.schemas.python.docstring import DocstringCommon
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.member_analysis import MemberCommon
from gyomu_schema.schemas.python.symbol_base import SymbolCommon

from gyomu_python_analysis.analysis.analyzers.decorator import analyze_decorators
from gyomu_python_analysis.analysis.analyzers.docstring import analyze_docstring
from gyomu_python_analysis.analysis.analyzers.internal.location import (
    calculate_docstring_location,
    calculate_member_location,
    calculate_symbol_location,
)
from gyomu_python_analysis.analysis.analyzers.internal.visibility import (
    calculate_visibility,
)


def build_symbol_common(
    symbol: Object,
    name: str,
    source_lines: list[str],
) -> SymbolCommon:
    location = calculate_symbol_location(
        symbol=symbol,
        source_lines=source_lines,
    )
    docstring = (
        analyze_docstring(
            symbol.docstring,
            source_lines,
            doc_common=build_docstring_common(
                symbol.docstring, source_lines=source_lines
            ),
        )
        if symbol.docstring is not None
        else None
    )
    decorators: list[DecoratorAnalysis] = []
    if isinstance(symbol, Class | Function):
        decorators = analyze_decorators(symbol.decorators, source_lines=source_lines)
    return {
        "name": name,
        "location": location,
        "visibility": calculate_visibility(name),
        "indent": location.start_column,
        "docstring": docstring,
        "decorators": tuple(decorators),
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
    docstring = (
        analyze_docstring(
            symbol.docstring,
            source_lines,
            doc_common=build_docstring_common(
                symbol.docstring, source_lines=source_lines
            ),
        )
        if symbol.docstring is not None
        else None
    )
    decorators: list[DecoratorAnalysis] = []
    if isinstance(symbol, Function):
        decorators = analyze_decorators(symbol.decorators, source_lines=source_lines)

    return {
        "name": name,
        "location": location,
        "visibility": calculate_visibility(name),
        "indent": location.start_column if location is not None else None,
        "docstring": docstring,
        "decorators": tuple(decorators),
    }


def build_docstring_common(
    doc: Docstring,
    source_lines: list[str],
) -> DocstringCommon:
    location = calculate_docstring_location(
        doc=doc,
        source_lines=source_lines,
    )
    return {
        "location": location,
        "indent": location.start_column,
    }
