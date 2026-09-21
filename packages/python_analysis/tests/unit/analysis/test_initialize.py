from pathlib import Path

import pytest
from gyomu_python_analysis.analysis.initialize import (
    find_included_python_files,
    initialize_project_context,
    initialize_project_from_workspace,
    read_version,
    resolve_source_root,
)
from gyomu_python_analysis.project.context import ProjectContext, PyProjectConfig
from gyomu_python_analysis.project.workspace import WorkspaceConfig, WorkspaceProject
from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class TestReadVersion:
    def test_read_version(self, tmp_path: Path) -> None:
        path = tmp_path / "__about__.py"
        path.write_text(
            '__version__ = "0.2.0"\n',
            encoding="utf-8",
        )

        result = read_version(path)

        assert result == Success("0.2.0")

    def test_read_version_returns_none_when_version_is_missing(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "__about__.py"
        path.write_text(
            'NAME = "example"\n',
            encoding="utf-8",
        )

        result = read_version(path)

        assert result == Success(None)

    def test_read_version_returns_none_when_version_is_not_string(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "__about__.py"
        path.write_text(
            "__version__ = 123\n",
            encoding="utf-8",
        )

        result = read_version(path)

        assert result == Success(None)


class TestFindIncludedPythonFiles:
    def test_find_included_python_files(self, tmp_path: Path) -> None:
        source_root = tmp_path / "src"

        foo = source_root / "package" / "foo.py"
        bar = source_root / "package" / "sub" / "bar.py"
        init = source_root / "package" / "__init__.py"
        test_file = source_root / "package" / "test_foo.py"
        suffix_test = source_root / "package" / "foo_test.py"
        text_file = source_root / "package" / "README.txt"

        for path in (foo, bar, init, test_file, suffix_test, text_file):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")

        result = find_included_python_files(
            FullPath(tmp_path),
            ProjectRelativePath(Path("src")),
        )

        assert result == frozenset(
            {
                ProjectRelativePath(Path("src/package/foo.py")),
                ProjectRelativePath(Path("src/package/sub/bar.py")),
                ProjectRelativePath(Path("src/package/__init__.py")),
            }
        )


class TestInitializeProjectContext:
    def test_initialize_project_context(
        self,
        tmp_path: Path,
    ) -> None:
        source_root = tmp_path / "src"

        pyproject = """\
    [project]
    name = "example-project"
    description = "Example project"
    version = "1.2.3"
    """

        (tmp_path / "pyproject.toml").write_text(
            pyproject,
            encoding="utf-8",
        )

        source_file = source_root / "example" / "foo.py"
        source_file.parent.mkdir(parents=True)
        source_file.write_text(
            "def foo() -> None:\n    pass\n",
            encoding="utf-8",
        )

        test_file = source_root / "example" / "test_foo.py"
        test_file.write_text(
            "def test_foo() -> None:\n    pass\n",
            encoding="utf-8",
        )

        result = initialize_project_context(
            FullPath(tmp_path),
            ProjectRelativePath(Path("src")),
        )

        assert isinstance(result, Success)

        context = result.unwrap()
        config = context.config
        assert config.name == "example-project"
        assert config.description == "Example project"
        assert config.version == "1.2.3"
        assert context.project_root == FullPath(tmp_path)
        assert context.source_root == ProjectRelativePath(Path("src"))
        assert context.included_files == frozenset(
            {
                ProjectRelativePath(Path("src/example/foo.py")),
            }
        )

    def test_initialize_project_context_with_hatch_dynamic_version(
        self,
        tmp_path: Path,
    ) -> None:
        source_root = tmp_path / "src"

        pyproject = """\
    [project]
    name = "example-project"
    description = "Example project"
    dynamic = ["version"]

    [build-system]
    requires = ["hatchling"]

    [tool.hatch.version]
    path = "src/example/__about__.py"
    """

        (tmp_path / "pyproject.toml").write_text(
            pyproject,
            encoding="utf-8",
        )

        version_file = source_root / "example" / "__about__.py"
        version_file.parent.mkdir(parents=True)
        version_file.write_text(
            '__version__ = "0.2.0"\n',
            encoding="utf-8",
        )

        result = initialize_project_context(
            FullPath(tmp_path),
            ProjectRelativePath(Path("src")),
        )

        assert isinstance(result, Success)

        context = result.unwrap()
        config = context.config
        assert config.name == "example-project"
        assert config.description == "Example project"
        assert config.version == "0.2.0"

    def test_initialize_project_context_returns_failure_when_pyproject_is_missing(
        self,
        tmp_path: Path,
    ) -> None:
        result = initialize_project_context(
            FullPath(tmp_path),
            ProjectRelativePath(Path("src")),
        )

        assert isinstance(result, Failure)


class TestResolveSourceRoot:
    @pytest.mark.parametrize(
        ("create_src", "expected"),
        [
            (True, ProjectRelativePath(Path("src"))),
            (False, ProjectRelativePath(Path("."))),
        ],
    )
    def test_resolve_source_root(
        self,
        tmp_path: Path,
        create_src: bool,
        expected: ProjectRelativePath,
    ) -> None:
        if create_src:
            (tmp_path / "src").mkdir()

        result = resolve_source_root(FullPath(tmp_path))

        assert result == expected


class TestInitializeProjectFromWorkspace:
    def test_initialize_project_from_workspace(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        workspace_path = FullPath(tmp_path)
        project_path = WorkspaceRelativePath(Path("packages/example"))
        project_root = FullPath(tmp_path / "packages/example")

        project_config = PyProjectConfig(
            name="example",
            description="Example project",
            version="1.0.0",
            path=project_path,
            formatter_line_length=88,
        )
        workspace = WorkspaceConfig(
            path=workspace_path,
            name="workspace",
            description="Test workspace",
            formatter_line_length=88,
        )
        project = WorkspaceProject(
            path=project_path,
            config=project_config,
        )

        included_files = frozenset(
            {
                ProjectRelativePath(Path("src/example.py")),
                ProjectRelativePath(Path("src/foo.py")),
            }
        )
        find_files = mocker.patch(
            "gyomu_python_analysis.analysis.initialize.find_included_python_files",
            return_value=included_files,
        )
        mocker.patch(
            "gyomu_python_analysis.analysis.initialize.resolve_source_root",
            return_value=ProjectRelativePath(Path("src")),
        )

        result = initialize_project_from_workspace(workspace, project)

        assert result == ProjectContext(
            project_root=project_root,
            source_root=ProjectRelativePath(Path("src")),
            config=project_config,
            included_files=included_files,
        )

        find_files.assert_called_once_with(
            project_root=project_root,
            source_root=ProjectRelativePath(Path("src")),
        )
        assert result.config is project_config
