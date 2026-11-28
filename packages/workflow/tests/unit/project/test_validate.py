from pathlib import Path

from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_workflow.project.error import (
    PyProjectStructureValidationErrors,
)
from gyomu_workflow.project.validate import (
    validate_python_package_structure,
)
from returns.result import Failure, Success

from packages.workflow.test_support.helpers import (
    build_test_project_structure,
)


class TestValidatePythonPackageStructure:
    def test_returns_success_when_structure_is_valid(self, tmp_path):
        context = build_test_project_structure(
            project_root=tmp_path,
            files={
                "src/foo/py.typed": "",
                "src/foo/__init__.py": "",
                "src/foo/module.py": "",
                "src/foo/sub/__init__.py": "",
                "src/foo/sub/module.py": "",
            },
        )

        result = validate_python_package_structure(context)

        assert result == Success(None)

    def test_returns_all_missing_init_files(self, tmp_path):
        context = build_test_project_structure(
            project_root=tmp_path,
            files={
                "src/foo/py.typed": "",
                "src/foo/__init__.py": "",
                "src/foo/module.py": "",
                "src/bar/py.typed": "",
                "src/bar/module.py": "",
                "src/baz/py.typed": "",
                "src/baz/__init__.py": "",
                "src/baz/sub/module.py": "",
            },
        )

        result = validate_python_package_structure(context)

        assert isinstance(result, Failure)

        error = result.failure()

        assert error.project_name == "test-project"
        assert len(error.errors) == 2
        assert {item.path for item in error.errors} == {
            ProjectRelativePath(Path("src/bar")),
            ProjectRelativePath(Path("src/baz/sub")),
        }
        assert all(
            item.message == "__init__.py does not exist" for item in error.errors
        )

    def test_does_not_require_init_for_directory_without_python_files(self, tmp_path):
        context = build_test_project_structure(
            project_root=tmp_path,
            files={
                "src/foo/py.typed": "",
                "src/foo/__init__.py": "",
                "src/foo/module.py": "",
                "src/docs/README.md": "",
            },
        )

        result = validate_python_package_structure(context)

        assert result == Success(None)

    def test_requires_init_for_directory_with_python_files_in_descendants(
        self,
        tmp_path,
    ):
        context = build_test_project_structure(
            project_root=tmp_path,
            files={
                "src/foo/py.typed": "",
                "src/foo/__init__.py": "",
                "src/foo/bar/module.py": "",
            },
        )

        result = validate_python_package_structure(context)
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, PyProjectStructureValidationErrors)
        assert {item.path for item in error.errors} == {
            ProjectRelativePath(Path("src/foo/bar")),
        }

    def test_requires_init_for_all_directories_in_python_package_tree(
        self,
        tmp_path,
    ):
        context = build_test_project_structure(
            project_root=tmp_path,
            files={"src/foo/bar/baz/module.py": "", "src/foo/__init__.py": ""},
        )

        result = validate_python_package_structure(context)
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, PyProjectStructureValidationErrors)
        assert {item.path for item in error.errors} == {
            ProjectRelativePath(Path("src/foo/bar/baz")),
            ProjectRelativePath(Path("src/foo/bar")),
            ProjectRelativePath(Path("src/foo")),
        }
        assert len(error.errors) == 3
