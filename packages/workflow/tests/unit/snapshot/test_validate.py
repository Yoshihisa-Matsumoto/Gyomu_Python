from pathlib import Path

from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.error import SnapshotRequestValidationError
from gyomu_workflow.snapshot.models import (
    DocstringExecutionOption,
    SnapshotActionOption,
    SnapshotExecutionOption,
    SnapshotRequest,
    SnapshotTargetOption,
)
from gyomu_workflow.snapshot.validate import (
    validate_python_package_structure,
    validate_snapshot_request,
)
from returns.result import Failure, Success

from packages.python_analysis.python_analysis_test_support.helpers import (
    _create_context,
    create_workspace_project,
)
from packages.workflow.workflow_test_support.helpers import (
    create_test_project_structure,
)


class TestValidateSnapshotRequest:
    def test_succeeds_when_all_is_false(self) -> None:
        request = SnapshotRequest(
            repository_root_path=FullPath(Path("/tmp")),
            project_context=_create_context(),
            option=SnapshotExecutionOption(
                commit=False,
                target=SnapshotTargetOption(
                    all=False,
                ),
                action=SnapshotActionOption(
                    docstring=DocstringExecutionOption(enabled=True)
                ),
            ),
            project=create_workspace_project(),
        )

        result = validate_snapshot_request(request)

        assert result == Success(None)

    def test_fails_when_all_is_true_and_commit_is_false(self) -> None:
        request = SnapshotRequest(
            repository_root_path=FullPath(Path("/tmp")),
            project_context=_create_context(),
            option=SnapshotExecutionOption(
                commit=False,
                target=SnapshotTargetOption(
                    all=True,
                ),
                action=SnapshotActionOption(
                    docstring=DocstringExecutionOption(enabled=True)
                ),
            ),
            project=create_workspace_project(),
        )

        result = validate_snapshot_request(request)

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, SnapshotRequestValidationError)
        assert error.code == "commit_required_for_all"
        assert error.message == "commit must be enabled when all is true."
        assert error.field == "option.commit"
        assert error.expected is True
        assert error.actual is False

    def test_succeeds_when_all_is_true_and_commit_is_true(self) -> None:
        request = SnapshotRequest(
            repository_root_path=FullPath(Path("/tmp")),
            project_context=_create_context(),
            option=SnapshotExecutionOption(
                commit=True,
                target=SnapshotTargetOption(
                    all=True,
                ),
                action=SnapshotActionOption(
                    docstring=DocstringExecutionOption(enabled=True)
                ),
            ),
            project=create_workspace_project(),
        )

        result = validate_snapshot_request(request)

        assert result == Success(None)


class TestValidatePythonPackageStructure:
    def test_returns_success_when_structure_is_valid(self, tmp_path):
        context = create_test_project_structure(
            project_root=tmp_path,
            files={
                "src/foo/__init__.py": "",
                "src/foo/module.py": "",
                "src/foo/sub/__init__.py": "",
                "src/foo/sub/module.py": "",
            },
        )

        result = validate_python_package_structure(context)

        assert result == Success(None)

    def test_returns_all_missing_init_files(self, tmp_path):
        context = create_test_project_structure(
            project_root=tmp_path,
            files={
                "src/foo/__init__.py": "",
                "src/foo/module.py": "",
                "src/bar/module.py": "",
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
        context = create_test_project_structure(
            project_root=tmp_path,
            files={
                "src/foo/__init__.py": "",
                "src/foo/module.py": "",
                "src/docs/README.md": "",
            },
        )

        result = validate_python_package_structure(context)

        assert result == Success(None)
