from pathlib import Path

import pytest
from gyomu_python_analysis.path.conversion import (
    project_relative_path_to_source_relative_path,
    source_relative_path_to_python_path,
)
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    PythonPath,
    SourceRelativePath,
)
from gyomu_schema.schemas.types import FullPath


class TestSourceRelativePathToPythonPath:
    def test_converts_module_path(self) -> None:
        path = SourceRelativePath(Path("foo/bar.py"))

        assert source_relative_path_to_python_path(path) == PythonPath("foo.bar")

    def test_converts_package_init_path(self) -> None:
        path = SourceRelativePath(Path("foo/__init__.py"))

        assert source_relative_path_to_python_path(path) == PythonPath("foo")

    def test_converts_nested_module_path(self) -> None:
        path = SourceRelativePath(Path("foo/bar/baz.py"))

        assert source_relative_path_to_python_path(path) == PythonPath("foo.bar.baz")

    def test_converts_nested_package_init_path(self) -> None:
        path = SourceRelativePath(Path("foo/bar/__init__.py"))

        assert source_relative_path_to_python_path(path) == PythonPath("foo.bar")


class TestProjectRelativePath2SourceRelativePath:
    def test_converts_source_root_file(self) -> None:
        context = ProjectContext(
            project_root=FullPath(Path("/project")),
            source_root=ProjectRelativePath(Path("src")),
            name="test",
            version="0.1",
            description=None,
        )
        path = ProjectRelativePath(Path("src/foo.py"))

        result = project_relative_path_to_source_relative_path(path, context)

        assert result == SourceRelativePath(Path("foo.py"))

    def test_converts_nested_source_file(self) -> None:
        context = ProjectContext(
            project_root=FullPath(Path("/project")),
            source_root=ProjectRelativePath(Path("src")),
            name="test",
            version="0.1",
            description=None,
        )
        path = ProjectRelativePath(Path("src/gyomu_schema/analysis/foo.py"))

        result = project_relative_path_to_source_relative_path(path, context)

        assert result == SourceRelativePath(Path("gyomu_schema/analysis/foo.py"))

    def test_supports_project_without_src_directory(self) -> None:
        context = ProjectContext(
            project_root=FullPath(Path("/project")),
            source_root=ProjectRelativePath(Path(".")),
            name="test",
            version="0.1",
            description=None,
        )
        path = ProjectRelativePath(Path("foo.py"))

        result = project_relative_path_to_source_relative_path(path, context)

        assert result == SourceRelativePath(Path("foo.py"))

    def test_raises_when_path_is_outside_source_root(self) -> None:
        context = ProjectContext(
            project_root=FullPath(Path("/project")),
            source_root=ProjectRelativePath(Path("src")),
            name="test",
            version="0.1",
            description=None,
        )
        path = ProjectRelativePath(Path("tests/foo.py"))

        with pytest.raises(ValueError):
            project_relative_path_to_source_relative_path(path, context)
