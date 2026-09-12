from pathlib import Path

from gyomu_python_analysis.analysis.load_module import load_module_analysis
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.python.docstring import DocstringAnalysis, DocstringStyle
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    PythonPath,
    SourceRelativePath,
)
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from tests.helpers import create_location


class TestLoadModuleAnalysis:
    def test_returns_failure_when_load_module_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        expected = AnalysisError(
            message="fail to load source file",
            file_path=PythonPath("foo"),
            phase="source-file-load",
        )

        load_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_module.load_module",
            return_value=Failure(expected),
        )

        context = ProjectContext(
            project_root=FullPath(Path("/tmp/project")),
            source_root=ProjectRelativePath(Path("src")),
        )

        result = load_module_analysis(
            context,
            PythonPath("foo"),
        )

        assert result == Failure(expected)
        load_mock.assert_called_once_with(context, PythonPath("foo"))

    def test_analyzes_module_without_docstring(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(Path("/tmp/project")),
            source_root=ProjectRelativePath(Path("src")),
        )

        source_file = mocker.MagicMock()
        source_file.path = SourceRelativePath(Path("foo.py"))
        source_file.module.path = "test.foo"
        source_file.module.name = "foo"
        source_file.module.docstring = None

        symbols = mocker.MagicMock()
        symbols.imported = tuple()
        symbols.symbols = tuple()

        load_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_module.load_module",
            return_value=Success(source_file),
        )
        extract_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_module.extract_symbols",
            return_value=symbols,
        )
        initialize_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_module.initialize_symbol_context",
        )
        analyze_docstring_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_module.analyze_docstring",
        )
        build_common_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_module.build_docstring_common",
        )
        read_mock = mocker.patch("pathlib.Path.read_text", return_value="")

        result = load_module_analysis(
            context,
            PythonPath("foo"),
        )

        expected = ModuleAnalysis(
            path=SourceRelativePath(Path("foo.py")),
            module_name=PythonPath("test.foo"),
            imports=tuple(),
            symbols=tuple(),
            name="foo",
            docstring=None,
        )
        # if isinstance(result, Failure):
        #     failure = result.failure()
        #     print(repr(failure))
        assert result == Success(expected)

        load_mock.assert_called_once_with(context, PythonPath("foo"))

        extract_mock.assert_called_once_with(
            source_file=source_file,
            source_lines=[],
        )

        initialize_mock.assert_called_once_with(
            module_name=PythonPath("test.foo"),
            name="",
            source_lines=[],
        )

        build_common_mock.assert_not_called()
        analyze_docstring_mock.assert_not_called()

    def test_returns_analysis_error_when_reading_source_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
        )

        source_file = mocker.MagicMock()
        source_file.path = SourceRelativePath(Path("foo.py"))
        source_file.module.path = "test.foo"
        source_file.module.name = "foo"
        source_file.module.docstring = None

        read_mock = mocker.patch(
            "pathlib.Path.read_text",
            side_effect=OSError("failed to read source file"),
        )

        mocker.patch(
            "gyomu_python_analysis.analysis.load_module.load_module",
            return_value=Success(source_file),
        )

        result = load_module_analysis(
            context,
            PythonPath("foo"),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert error.message == "fail to analyze module"
        assert error.file_path == PythonPath("foo")
        assert error.phase == "symbol-extract"

        read_mock.assert_called_once_with(encoding="utf-8")

    def test_analyzes_module_with_docstring(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
        )

        source_path = tmp_path / "src" / "foo.py"
        source_path.parent.mkdir(parents=True)
        source_lines = [
            '"""Module docstring."""\n',
            "\n",
            "x = 1\n",
        ]
        source_path.write_text(
            "".join(source_lines),
            encoding="utf-8",
        )

        source_file = mocker.MagicMock()
        source_file.path = SourceRelativePath(Path("foo.py"))
        source_file.module.path = "test.foo"
        source_file.module.name = "foo"

        raw_docstring = mocker.MagicMock()
        source_file.module.docstring = raw_docstring

        symbols = mocker.MagicMock()
        symbols.imported = tuple()
        symbols.symbols = tuple()

        module_context = mocker.MagicMock()
        doc_common = mocker.MagicMock()
        analyzed_docstring = DocstringAnalysis(
            raw="",
            summary="",
            description=None,
            style=DocstringStyle.GOOGLE,
            location=create_location(),
            sections=tuple(),
            indent=0,
        )

        mocker.patch(
            "gyomu_python_analysis.analysis.load_module.load_module",
            return_value=Success(source_file),
        )
        extract_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_module.extract_symbols",
            return_value=symbols,
        )
        initialize_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_module.initialize_symbol_context",
            return_value=module_context,
        )
        build_common_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_module.build_docstring_common",
            return_value=doc_common,
        )
        analyze_docstring_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_module.analyze_docstring",
            return_value=analyzed_docstring,
        )

        result = load_module_analysis(
            context,
            PythonPath("foo"),
        )

        expected = ModuleAnalysis(
            path=SourceRelativePath(Path("foo.py")),
            module_name=PythonPath("test.foo"),
            imports=tuple(),
            symbols=tuple(),
            name="foo",
            docstring=analyzed_docstring,
        )

        assert result == Success(expected)

        extract_mock.assert_called_once_with(
            source_file=source_file,
            source_lines=source_lines,
        )

        initialize_mock.assert_called_once_with(
            module_name=PythonPath("test.foo"),
            name="",
            source_lines=source_lines,
        )

        build_common_mock.assert_called_once_with(
            raw_docstring,
            module_context,
        )

        analyze_docstring_mock.assert_called_once_with(
            raw_docstring,
            doc_common=doc_common,
            context=module_context,
        )

    def test_returns_analysis_error_when_analysis_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
        )

        source_path = tmp_path / "src" / "foo.py"
        source_path.parent.mkdir(parents=True)
        source_path.write_text(
            "x = 1\n",
            encoding="utf-8",
        )

        source_file = mocker.MagicMock()
        source_file.path = SourceRelativePath(Path("foo.py"))
        source_file.module.path = "test.foo"
        source_file.module.name = "foo"
        source_file.module.docstring = None

        cause = ValueError("unexpected error")

        mocker.patch(
            "gyomu_python_analysis.analysis.load_module.load_module",
            return_value=Success(source_file),
        )
        mocker.patch(
            "gyomu_python_analysis.analysis.load_module.extract_symbols",
            side_effect=cause,
        )

        result = load_module_analysis(
            context,
            PythonPath("foo"),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert error.message == "fail to analyze module"
        assert error.file_path == PythonPath("foo")
        assert error.phase == "symbol-extract"
