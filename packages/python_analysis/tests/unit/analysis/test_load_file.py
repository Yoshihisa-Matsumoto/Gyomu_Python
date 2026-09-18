from pathlib import Path

from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.python.file_analysis import FileAnalysisMetadata
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    PythonPath,
    SourceRelativePath,
)
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class TestLoadFileAnalysisContext:
    def test_returns_failure_when_get_module_analysis_fails(
        self,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
            name="test",
            version="0.1",
            description=None,
        )
        error = AnalysisError(
            message="failed to load module",
            file_path=PythonPath("foo"),
            phase="source-file-load",
        )
        failure = Failure(error)

        get_module_analysis_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_file_context.get_module_analysis",
            return_value=failure,
        )
        create_metadata_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_file_context"
            ".create_file_analysis_metadata",
        )

        file_path = ProjectRelativePath(Path("foo.py"))

        result = load_file_analysis_context(context, file_path)

        assert result == failure
        get_module_analysis_mock.assert_called_once_with(context, file_path, None, None)
        create_metadata_mock.assert_not_called()

    def test_creates_file_analysis_context(
        self,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
            name="test",
            version="0.1",
            description=None,
        )
        module_analysis = ModuleAnalysis(
            path=SourceRelativePath(Path("foo.py")),
            module_name=PythonPath("test.foo"),
            imports=tuple(),
            symbols=tuple(),
            name="foo",
            docstring=None,
        )
        metadata = FileAnalysisMetadata(
            parsed_docstring={},
            symbols={},
        )

        get_module_analysis_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_file_context.get_module_analysis",
            return_value=Success(module_analysis),
        )
        create_metadata_mock = mocker.patch(
            "gyomu_python_analysis.analysis.load_file_context"
            ".create_file_analysis_metadata",
            return_value=metadata,
        )

        file_path = ProjectRelativePath(Path("foo.py"))

        result = load_file_analysis_context(context, file_path)

        assert isinstance(result, Success)

        file_analysis_context = result.unwrap()

        assert file_analysis_context.analysis is module_analysis
        assert file_analysis_context.metadata is metadata

        get_module_analysis_mock.assert_called_once_with(context, file_path, None, None)
        create_metadata_mock.assert_called_once_with(module_analysis)
