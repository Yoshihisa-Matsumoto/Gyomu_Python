from pathlib import Path

from gyomu_python_analysis.analysis.get_module import (
    _get_cache_path,
    get_module_analysis,
)
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext, PyProjectConfig
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    PythonPath,
    SourceRelativePath,
    WorkspaceRelativePath,
)
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

config = PyProjectConfig(
    path=WorkspaceRelativePath(Path(".")),
    name="test",
    version="0.1",
    description="test",
    formatter_line_length=88,
)


class TestReturnsCachePath:
    def test_returns_cache_path_for_nested_project_relative_path(
        self, tmp_path: Path
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
            config=config,
        )
        file_path = ProjectRelativePath(
            Path("src/gyomu_python_analysis/analysis/foo.py")
        )

        result = _get_cache_path(context, file_path)

        assert result == FullPath(
            tmp_path
            / ".gyomu"
            / "cache"
            / "src"
            / "gyomu_python_analysis"
            / "analysis"
            / "foo.py.json"
        )

    def test_keeps_py_extension_in_cache_filename(
        self,
        tmp_path: Path,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path(".")),
            config=config,
        )
        file_path = ProjectRelativePath(Path("foo.py"))

        result = _get_cache_path(context, file_path)

        assert result == FullPath(tmp_path / ".gyomu" / "cache" / "foo.py.json")


class TestGetModuleAnalysis:
    def test_returns_cached_module_analysis(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
            config=config,
        )
        file_path = ProjectRelativePath(Path("src/foo.py"))
        expected = ModuleAnalysis(
            module_name=PythonPath("test.foo"),
            docstring=None,
            name="foo",
            imports=tuple(),
            path=SourceRelativePath(Path("foo.py")),
            symbols=tuple(),
        )

        cache_path = _get_cache_path(context, file_path)
        cache_path.parent.mkdir(parents=True)
        cache_path.touch()

        read_json_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.read_json",
            return_value=Success(expected),
        )
        load_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.load_module_analysis",
        )
        write_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.write_json",
        )

        result = get_module_analysis(context, file_path)

        assert result == Success(expected)
        read_json_mock.assert_called_once_with(cache_path, ModuleAnalysis)
        load_mock.assert_not_called()
        write_mock.assert_not_called()

    def test_loads_module_analysis_when_cache_does_not_exist(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
            config=config,
        )
        file_path = ProjectRelativePath(Path("src/foo.py"))
        expected = ModuleAnalysis(
            module_name=PythonPath("test.foo"),
            docstring=None,
            name="foo",
            imports=tuple(),
            path=SourceRelativePath(Path("foo.py")),
            symbols=tuple(),
        )

        load_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.load_module_analysis",
            return_value=Success(expected),
        )
        write_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.write_json",
            return_value=Success(None),
        )

        result = get_module_analysis(context, file_path)

        assert result == Success(expected)

        load_mock.assert_called_once_with(context, PythonPath("foo"), None)

        write_mock.assert_called_once_with(
            _get_cache_path(context, file_path), expected, ModuleAnalysis
        )

    def test_loads_module_analysis_when_cache_is_invalid(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
            config=config,
        )
        file_path = ProjectRelativePath(Path("src/foo.py"))
        expected = ModuleAnalysis(
            module_name=PythonPath("test.foo"),
            docstring=None,
            name="foo",
            imports=tuple(),
            path=SourceRelativePath(Path("foo.py")),
            symbols=tuple(),
        )

        cache_path = _get_cache_path(context, file_path)
        cache_path.parent.mkdir(parents=True)
        cache_path.write_text("invalid json")

        load_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.load_module_analysis",
            return_value=Success(expected),
        )
        write_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.write_json",
            return_value=Success(None),
        )

        result = get_module_analysis(context, file_path)

        assert result == Success(expected)

        load_mock.assert_called_once_with(context, PythonPath("foo"), None)

        write_mock.assert_called_once_with(cache_path, expected, ModuleAnalysis)

    def test_returns_failure_when_load_module_analysis_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
            config=config,
        )
        file_path = ProjectRelativePath(Path("src/foo.py"))

        expected = AnalysisError(
            "fail to load ModuleAnalysis",
            file_path=PythonPath("foo"),
            phase="analysis",
        )

        load_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.load_module_analysis",
            return_value=Failure(expected),
        )
        write_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.write_json",
        )

        result = get_module_analysis(context, file_path)

        assert result == Failure(expected)

        load_mock.assert_called_once_with(context, PythonPath("foo"), None)

        write_mock.assert_not_called()

    def test_returns_failure_when_writing_module_analysis_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        context = ProjectContext(
            project_root=FullPath(tmp_path),
            source_root=ProjectRelativePath(Path("src")),
            config=config,
        )
        file_path = ProjectRelativePath(Path("src/foo.py"))
        expected = ModuleAnalysis(
            module_name=PythonPath("test.foo"),
            docstring=None,
            name="foo",
            imports=tuple(),
            path=SourceRelativePath(Path("foo.py")),
            symbols=tuple(),
        )

        write_error = AnalysisError(
            "fail to write cache",
            file_path=PythonPath("foo"),
            phase="post-analysis",
        )

        load_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.load_module_analysis",
            return_value=Success(expected),
        )
        write_mock = mocker.patch(
            "gyomu_python_analysis.analysis.get_module.write_json",
            return_value=Failure(write_error),
        )

        result = get_module_analysis(context, file_path)

        assert isinstance(result, Failure)
        failure = result.failure()
        assert failure.message == "fail to write ModuleAnalysis"
        assert failure.file_path == PythonPath("foo")
        assert failure.phase == "post-analysis"

        load_mock.assert_called_once_with(context, PythonPath("foo"), None)

        write_mock.assert_called_once_with(
            _get_cache_path(context, file_path), expected, ModuleAnalysis
        )
