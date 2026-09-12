import io
import tokenize

from gyomu_python_analysis.error.update import UpdateError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis, InnerClassAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from returns.result import Failure, Result, Success

from gyomu_docstring.update.docstring.file_update_plan import (
    FileUpdatePlan,
    FileUpdatePlanEntry,
)
from gyomu_docstring.update.docstring.rendered_symbol import (
    RenderedSymbolDocstring,
)


def build_file_update_plan(
    context: FileAnalysisContext,
    rendered_docstrings: tuple[RenderedSymbolDocstring, ...],
    source: str,
) -> Result[FileUpdatePlan, UpdateError]:
    entries_result = _build_file_update_plan_entries(
        context=context,
        rendered_docstrings=rendered_docstrings,
        source=source,
    )

    if isinstance(entries_result, Failure):
        return entries_result.alt(
            UpdateError(
                "fail to build file update plan entry",
                file_path=context.analysis.module_name,
                phase="update-plan",
                identity=None,
            ).chain
        )

    entries = entries_result.unwrap()

    validation_result = validate_file_update_plan_entries(entries)

    if isinstance(validation_result, Failure):
        return validation_result.alt(
            UpdateError(
                "fail to validate file update plan entry",
                file_path=context.analysis.module_name,
                phase="update-plan",
                identity=None,
            ).chain
        )

    return Success(FileUpdatePlan(items=entries))


def _build_file_update_plan_entries(
    context: FileAnalysisContext,
    rendered_docstrings: tuple[RenderedSymbolDocstring, ...],
    source: str,
) -> Result[tuple[FileUpdatePlanEntry, ...], ValidationError]:
    entries: list[FileUpdatePlanEntry] = []

    for rendered in rendered_docstrings:
        result = build_file_update_plan_entry(
            source=source,
            context=context,
            rendered=rendered,
        )

        if isinstance(result, Failure):
            return result

        entries.append(result.unwrap())

    return Success(tuple(entries))


def validate_file_update_plan_entries(
    entries: tuple[FileUpdatePlanEntry, ...],
) -> Result[None, ValidationError]:
    sorted_entries = sorted(
        entries,
        key=lambda entry: entry.location.start_offset,
    )

    for entry in sorted_entries:
        location = entry.location

        if location.start_offset > location.end_offset:
            return Failure(
                ValidationError(
                    f"Invalid file update range for "
                    f"{entry.identity}: "
                    f"start_offset ({location.start_offset}) is greater than "
                    f"end_offset ({location.end_offset}).",
                    context="gyomu_docstring.update.build_file_update.validate_file_update_plan_entries",
                )
            )

    for previous, current in zip(sorted_entries, sorted_entries[1:], strict=False):
        previous_end = previous.location.end_offset
        current_start = current.location.start_offset

        if current_start < previous_end:
            return Failure(
                ValidationError(
                    f"Overlapping file update ranges: "
                    f"{previous.identity} "
                    f"[{previous.location.start_offset}, {previous_end}) and "
                    f"{current.identity} "
                    f"[{current_start}, {current.location.end_offset}).",
                    context="gyomu_docstring.update.build_file_update.validate_file_update_plan_entries",
                )
            )

    return Success(None)


def build_file_update_plan_entry(
    source: str,
    context: FileAnalysisContext,
    rendered: RenderedSymbolDocstring,
) -> Result[FileUpdatePlanEntry, ValidationError]:
    analysis = context.metadata.symbols.get(rendered.identity)

    if analysis is None:
        return Failure(
            ValidationError(
                message="Declaration Item Not Found",
                context="gyomu_docstring.update.build_file_update.build_file_update_plan_entry",
                details={"identity": rendered.identity},
            )
        )

    if analysis.location is None or analysis.indent is None:
        return Failure(
            ValidationError(
                message="Declation Item is constructor parameter",
                context="gyomu_docstring.update.build_file_update.build_file_update_plan_entry",
                details={"identity": rendered.identity},
            )
        )

    if rendered.location.start_offset == rendered.location.end_offset:
        return build_addition_entry(
            source=source,
            analysis=analysis,
            rendered=rendered,
        )

    if rendered.docstring == "" or rendered.docstring is None:
        return Success(
            build_deletion_entry(
                source=source,
                rendered=rendered,
            )
        )

    return Success(build_replacement_entry(rendered))


def build_addition_entry(
    source: str,
    analysis: SymbolAnalysis | MemberAnalysis,
    rendered: RenderedSymbolDocstring,
) -> Result[FileUpdatePlanEntry, ValidationError]:
    assert rendered.docstring
    assert analysis.location

    # TODO: 追加するdocstringはシンボルの直前ではなく、
    # 定義ヘッダの直後に挿入する位置を計算する。
    location = rendered.location
    new_location = location.model_copy()
    new_location.start_offset = location.start_offset

    new_text = "\n" + rendered.docstring
    if isinstance(
        analysis, ClassAnalysis | FunctionAnalysis | InnerClassAnalysis | MethodAnalysis
    ):
        end_result = _get_declaration_definition_end_offset(source, analysis)
        if isinstance(end_result, Failure):
            return end_result
        new_location.start_offset = end_result.unwrap()
    new_location.end_offset = new_location.start_offset
    return Success(
        FileUpdatePlanEntry(
            identity=rendered.identity, location=new_location, new_text=new_text
        )
    )


def _get_declaration_definition_end_offset(
    source: str,
    analysis: ClassAnalysis | FunctionAnalysis | InnerClassAnalysis | MethodAnalysis,
) -> Result[int, ValidationError]:
    assert analysis.location

    declaration_source = source[
        analysis.location.start_offset : analysis.location.end_offset
    ]

    depth = 0

    tokens = tokenize.generate_tokens(io.StringIO(declaration_source).readline)

    for token in tokens:
        if token.type != tokenize.OP:
            continue

        if token.string in ("(", "[", "{"):
            depth += 1
            continue

        if token.string in (")", "]", "}"):
            depth -= 1
            continue

        if token.string == ":" and depth == 0:
            relative_offset = _get_line_offset(
                declaration_source,
                token.end,
            )

            # ':' の直後から改行までの空白・タブを飛ばす
            while (
                relative_offset < len(declaration_source)
                and declaration_source[relative_offset] not in "\r\n"
            ):
                relative_offset += 1

            return Success(analysis.location.start_offset + relative_offset)

    return Failure(
        ValidationError(
            message="Declaration definition end not found",
            context="gyomu_docstring.update.build_file_update._get_declaration_definition_end_offset",
            details={"identity": analysis.identity},
        )
    )


def _get_line_offset(
    source: str,
    position: tuple[int, int],
) -> int:
    row, column = position

    lines = source.splitlines(keepends=True)

    return sum(len(line) for line in lines[: row - 1]) + column


def build_deletion_entry(
    source: str, rendered: RenderedSymbolDocstring
) -> FileUpdatePlanEntry:
    location = rendered.location.model_copy()

    start = location.start_offset
    while start > 0 and source[start - 1] in " \t":
        start -= 1

    end = location.end_offset
    while end < len(source) and source[end] in " \t":
        end += 1

    location.start_offset = start
    location.end_offset = end

    return FileUpdatePlanEntry(
        identity=rendered.identity,
        location=location,
        new_text="",
    )


def build_replacement_entry(rendered: RenderedSymbolDocstring) -> FileUpdatePlanEntry:
    assert rendered.docstring
    return FileUpdatePlanEntry(
        identity=rendered.identity,
        location=rendered.location,
        new_text=rendered.docstring,
    )
