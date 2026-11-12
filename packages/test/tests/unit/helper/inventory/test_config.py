from pathlib import Path

from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath
from gyomu_schema.schemas.testing.helper import HelperConfig, HelperFileAllocation
from gyomu_schema.schemas.types import FullPath
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.inventory.config import (
    _get_helper_file_paths,
    _load_helper_config,
    get_helper_file_paths,
    get_helper_file_paths_from_workspace_project,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_project_context,
    create_workspace_project,
    create_workspace_root,
)
from packages.schema.test_support.helpers import create_config_error
from packages.test.tests.unit.helper.helpers import create_gyomu_test_error


class TestLoadHelperConfig:
    def test_success(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        project_root = FullPath(tmp_path)
        expected_config = HelperConfig(
            helper_directory="test_support",
        )
        retrieve_mock = mocker.patch(
            "gyomu_test.helper.inventory.config.retrieve_mandatory_config",
            return_value=Success(expected_config),
        )

        result = _load_helper_config(project_root=project_root)

        assert result == Success(expected_config)
        retrieve_mock.assert_called_once_with(
            config_type=HelperConfig,
            path=project_root / ".gyomu" / "config" / "$Package.helper.json",
        )

    def test_error(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        project_root = FullPath(tmp_path)

        expected_error = create_config_error()
        retrieve_mock = mocker.patch(
            "gyomu_test.helper.inventory.config.retrieve_mandatory_config",
            return_value=Failure(expected_error),
        )

        result = _load_helper_config(project_root=project_root)

        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, GyomuTestError)
        assert failure.__cause__ is expected_error
        retrieve_mock.assert_called_once_with(
            config_type=HelperConfig,
            path=project_root / ".gyomu" / "config" / "$Package.helper.json",
        )


class Test_GetHelperFilePaths:
    def test_without_allocation(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        project_root = FullPath(tmp_path)
        mocker.patch(
            "gyomu_test.helper.inventory.config._load_helper_config",
            return_value=Success(HelperConfig(helper_directory="test_support")),
        )

        result = _get_helper_file_paths(project_root=project_root)

        assert result == Success(
            (ProjectRelativePath(Path("test_support/helpers.py")),)
        )

    def test_with_allocation(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        project_root = FullPath(tmp_path)
        mocker.patch(
            "gyomu_test.helper.inventory.config._load_helper_config",
            return_value=Success(
                HelperConfig(
                    helper_directory="test_support",
                    file_allocation=(
                        HelperFileAllocation(
                            path=PythonPath("gyomu_schema.schemas.concept"),
                            helper_filename="concept_helpers.py",
                        ),
                        HelperFileAllocation(
                            path=PythonPath("gyomu_schema.schemas.request"),
                            helper_filename="concept_helpers.py",
                        ),
                    ),
                )
            ),
        )

        result = _get_helper_file_paths(project_root=project_root)

        assert result == Success(
            (
                ProjectRelativePath(Path("test_support/helpers.py")),
                ProjectRelativePath(Path("test_support/concept_helpers.py")),
            )
        )

    def test_failure(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        project_root = FullPath(tmp_path)
        expected_error = create_gyomu_test_error()
        mocker.patch(
            "gyomu_test.helper.inventory.config._load_helper_config",
            return_value=Failure(expected_error),
        )

        result = _get_helper_file_paths(project_root=project_root)

        assert isinstance(result, Failure)
        failure = result.failure()
        assert failure is expected_error


class TestGetHelperFilePathsFromWorkspaceProject:
    def test_success(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:

        workspace_project: WorkspaceProject = create_workspace_project()
        workspace_root = create_workspace_root(path=FullPath(tmp_path))
        workspace_context = mocker.Mock(WorkspaceContext)
        workspace_context.workspace_root = workspace_root
        expected_paths = (ProjectRelativePath(Path("test_support/helpers.py")),)
        get_paths_mock = mocker.patch(
            "gyomu_test.helper.inventory.config._get_helper_file_paths",
            return_value=Success(expected_paths),
        )

        result = get_helper_file_paths_from_workspace_project(
            workspace_context=workspace_context,
            workspace_project=workspace_project,
        )

        assert result == Success(expected_paths)
        get_paths_mock.assert_called_once_with(
            project_root=workspace_root.path / workspace_project.path,
        )


class TestGetHelperFilePaths:
    def test_success(
        self,
        mocker: MockerFixture,
    ) -> None:
        project_context: ProjectContext = create_project_context()
        expected_paths = (ProjectRelativePath(Path("test_support/helpers.py")),)
        get_paths_mock = mocker.patch(
            "gyomu_test.helper.inventory.config._get_helper_file_paths",
            return_value=Success(expected_paths),
        )

        result = get_helper_file_paths(project_context=project_context)

        assert result == Success(expected_paths)
        get_paths_mock.assert_called_once_with(
            project_root=project_context.project_root,
        )
