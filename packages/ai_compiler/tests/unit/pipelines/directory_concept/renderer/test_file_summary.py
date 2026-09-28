from pathlib import Path

from gyomu_ai_compiler.pipelines.directory_concept.renderer.file_summary import (
    build_export_symbol_input,
    render_file_summary,
)
from gyomu_schema.schemas.concept.file_summary import (
    FileSummary,
    PublicDeclarationSummary,
)
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import ProjectRelativePath


class TestBuildExportSymbolInput:
    def test_returns_formatted_symbol(self) -> None:
        symbol = PublicDeclarationSummary(
            symbol="example::Example",
            kind=DeclarationKind.CLASS,
            summary="Example class.",
        )

        result = build_export_symbol_input(symbol)

        assert result == ("- example::Example (class)\n  Summary:\n  Example class.")


class TestRenderFileSummary:
    def test_returns_file_summary_with_exports(self) -> None:
        context = FileSummary(
            path=ProjectRelativePath(Path("src/example.py")),
            exports=(
                PublicDeclarationSummary(
                    symbol="example::Example",
                    kind=DeclarationKind.CLASS,
                    summary="Example class.",
                ),
                PublicDeclarationSummary(
                    symbol="example::create_example",
                    kind=DeclarationKind.FUNCTION,
                    summary="Create an example.",
                ),
            ),
            dependencies=(),
        )

        result = render_file_summary(context)

        assert result == (
            "File path:\n"
            "src/example.py\n"
            "\n"
            "Exported symbols:\n"
            "- example::Example (class)\n"
            "  Summary:\n"
            "  Example class.\n"
            "\n"
            "- example::create_example (function)\n"
            "  Summary:\n"
            "  Create an example.\n"
        )

    def test_returns_file_summary_without_exports(self) -> None:
        context = FileSummary(
            path=ProjectRelativePath(Path("src/example.py")),
            exports=(),
            dependencies=(),
        )

        result = render_file_summary(context)

        assert result == ("File path:\nsrc/example.py\n\nExported symbols:\n\n")
