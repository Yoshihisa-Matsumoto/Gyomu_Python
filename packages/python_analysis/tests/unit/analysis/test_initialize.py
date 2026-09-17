from pathlib import Path

from gyomu_python_analysis.analysis.initialize import (
    find_included_python_files,
    initialize_project_context,
    read_version,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
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

        assert context.name == "example-project"
        assert context.description == "Example project"
        assert context.version == "1.2.3"
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

        assert context.name == "example-project"
        assert context.description == "Example project"
        assert context.version == "0.2.0"

    def test_initialize_project_context_returns_failure_when_pyproject_is_missing(
        self,
        tmp_path: Path,
    ) -> None:
        result = initialize_project_context(
            FullPath(tmp_path),
            ProjectRelativePath(Path("src")),
        )

        assert isinstance(result, Failure)
