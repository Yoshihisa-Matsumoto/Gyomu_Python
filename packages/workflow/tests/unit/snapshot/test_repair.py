from pathlib import Path
from unittest.mock import MagicMock

from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.error import (
    PyProjectStructureErrorKind,
    PyProjectStructureValidationError,
)
from gyomu_workflow.snapshot.repair import (
    create_file_if_not_exist,
    repair_python_package_structure,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class TestCreateFileIfNotExist:
    def test_creates_empty_file_when_file_does_not_exist(
        self,
        tmp_path: Path,
    ) -> None:
        path = FullPath(tmp_path / "module.py")

        result = create_file_if_not_exist(path)

        assert result == Success(None)
        assert path.is_file()
        assert path.read_text() == ""

    def test_preserves_existing_file_content(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        path = FullPath(tmp_path / "module.py")
        path.write_text("existing content")

        write_text_mock = mocker.patch(
            "gyomu_workflow.snapshot.repair.write_text",
        )

        result = create_file_if_not_exist(path)

        assert result == Success(None)
        assert path.read_text() == "existing content"
        write_text_mock.assert_not_called()

    def test_returns_failure_when_file_creation_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        path = FullPath(tmp_path / "module.py")
        io_error = MagicMock(spec=GyomuIOError)

        mocker.patch(
            "gyomu_workflow.snapshot.repair.write_text",
            return_value=Failure(io_error),
        )

        result = create_file_if_not_exist(path)

        assert isinstance(result, Failure)
        assert result.failure() is io_error


class TestRepairPythonPackageStructure:
    def test_creates_missing_init_and_py_typed_files(
        self,
        tmp_path: Path,
    ) -> None:
        package_root = tmp_path / "src" / "foo"
        package_root.mkdir(parents=True)

        context = MagicMock()
        context.project_root = FullPath(tmp_path)

        errors = (
            PyProjectStructureValidationError(
                "__init__.py does not exist",
                kind=PyProjectStructureErrorKind.MISSING_INIT_FILE,
                path=ProjectRelativePath(Path("src/foo")),
            ),
            PyProjectStructureValidationError(
                "py.typed does not exist",
                kind=PyProjectStructureErrorKind.MISSING_PY_TYPED_FILE,
                path=ProjectRelativePath(Path("src/foo")),
            ),
        )

        result = repair_python_package_structure(context, errors)

        assert result == Success(None)
        assert (package_root / "__init__.py").is_file()
        assert (package_root / "py.typed").is_file()
        assert (package_root / "__init__.py").read_text() == ""
        assert (package_root / "py.typed").read_text() == ""

    def test_preserves_existing_file_content(
        self,
        tmp_path: Path,
    ) -> None:
        package_root = tmp_path / "src" / "foo"
        package_root.mkdir(parents=True)

        init_path = package_root / "__init__.py"
        init_path.write_text("# existing initializer")

        pytyped_path = package_root / "py.typed"
        pytyped_path.write_text("existing marker")

        context = MagicMock()
        context.project_root = FullPath(tmp_path)

        errors = (
            PyProjectStructureValidationError(
                "__init__.py does not exist",
                kind=PyProjectStructureErrorKind.MISSING_INIT_FILE,
                path=ProjectRelativePath(Path("src/foo")),
            ),
            PyProjectStructureValidationError(
                "py.typed does not exist",
                kind=PyProjectStructureErrorKind.MISSING_PY_TYPED_FILE,
                path=ProjectRelativePath(Path("src/foo")),
            ),
        )

        result = repair_python_package_structure(context, errors)

        assert result == Success(None)
        assert init_path.read_text() == "# existing initializer"
        assert pytyped_path.read_text() == "existing marker"

    def test_returns_failure_when_file_creation_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        package_root = tmp_path / "src" / "foo"
        package_root.mkdir(parents=True)

        context = MagicMock()
        context.project_root = FullPath(tmp_path)

        error = PyProjectStructureValidationError(
            "__init__.py does not exist",
            kind=PyProjectStructureErrorKind.MISSING_INIT_FILE,
            path=ProjectRelativePath(Path("src/foo")),
        )
        io_error = MagicMock(spec=GyomuIOError)

        mocker.patch(
            "gyomu_workflow.snapshot.repair.write_text",
            return_value=Failure(io_error),
        )

        result = repair_python_package_structure(context, (error,))

        assert isinstance(result, Failure)
        assert result.failure() is io_error

    def test_succeeds_when_errors_are_empty(
        self,
        tmp_path: Path,
    ) -> None:
        context = MagicMock()
        context.project_root = FullPath(tmp_path)

        result = repair_python_package_structure(context, ())

        assert result == Success(None)
