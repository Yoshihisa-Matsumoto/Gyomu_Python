from pathlib import Path

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath
from gyomu_schema.schemas.testing.helper import HelperConfig, HelperFileAllocation
from gyomu_schema.schemas.types import FullPath
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.inventory.config import (
    _get_helper_file_paths_from_project_context,
    _load_helper_config_with_default,
    get_helper_file_path,
    get_helper_file_paths,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_project_context,
)
from packages.schema.test_support.helpers import (
    create_config_error,
    simple_create_declaration_identity,
)
from packages.schema.test_support.testing_helpers import create_helper_file_allocation
from packages.test.tests.unit.helper.helpers import create_gyomu_test_error


class TestLoadHelperConfigWithDefault:
    def test_success_without_allocation(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        project_root = FullPath(tmp_path)
        expected_config = HelperConfig(
            helper_directory="test_support",
        )
        retrieve_mock = mocker.patch(
            "gyomu_test.helper.inventory.config.retrieve_config",
            return_value=Success(expected_config),
        )
        project_context = create_project_context(project_root=project_root)
        result = _load_helper_config_with_default(project_context=project_context)

        assert result == Success(
            HelperConfig(
                helper_directory="test_support",
            )
        )

    def test_success_without_config_file(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        project_root = FullPath(tmp_path)
        expected_config = HelperConfig(
            helper_directory="test_support",
        )
        mocker.patch(
            "gyomu_test.helper.inventory.config.retrieve_config",
            return_value=Success(None),
        )
        project_context = create_project_context(project_root=project_root)
        result = _load_helper_config_with_default(project_context=project_context)

        assert result == Success(
            HelperConfig(
                helper_directory="test_support",
            )
        )

    def test_success_with_allocation(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        project_root = FullPath(tmp_path)
        expected_config = HelperConfig(
            helper_directory="test_support",
            file_allocation=(
                create_helper_file_allocation(helper_filename="test_helper.py"),
            ),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.config.retrieve_config",
            return_value=Success(expected_config),
        )
        project_context = create_project_context(project_root=project_root)
        result = _load_helper_config_with_default(project_context=project_context)

        assert result == Success(expected_config)

    def test_error(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        project_root = FullPath(tmp_path)

        expected_error = create_config_error()
        retrieve_mock = mocker.patch(
            "gyomu_test.helper.inventory.config.retrieve_config",
            return_value=Failure(expected_error),
        )
        project_context = create_project_context(project_root=project_root)
        result = _load_helper_config_with_default(project_context=project_context)

        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, GyomuTestError)
        assert failure.__cause__ is expected_error
        # retrieve_mock.assert_called_once_with(
        #     config_type=HelperConfig,
        #     path=project_root / ".gyomu" / "config" / "$Package.helper.json",
        # )


class Test_GetHelperFilePaths:
    def test_without_allocation(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        project_root = FullPath(tmp_path)
        mocker.patch(
            "gyomu_test.helper.inventory.config._load_helper_config_with_default",
            return_value=Success(HelperConfig(helper_directory="test_support")),
        )
        project_context = create_project_context(project_root=project_root)
        result = _get_helper_file_paths_from_project_context(
            project_context=project_context
        )

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
            "gyomu_test.helper.inventory.config._load_helper_config_with_default",
            return_value=Success(
                HelperConfig(
                    helper_directory="test_support",
                    file_allocation=(
                        HelperFileAllocation(
                            path=PythonPath(""),
                            helper_filename="helpers.py",
                        ),
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
        project_context = create_project_context(project_root=project_root)
        result = _get_helper_file_paths_from_project_context(
            project_context=project_context
        )
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
            "gyomu_test.helper.inventory.config._load_helper_config_with_default",
            return_value=Failure(expected_error),
        )

        project_context = create_project_context(project_root=project_root)
        result = _get_helper_file_paths_from_project_context(
            project_context=project_context
        )

        assert isinstance(result, Failure)
        failure = result.failure()
        assert failure is expected_error


# class TestGetHelperFilePathsFromWorkspaceProject:
#     def test_success(
#         self,
#         tmp_path: Path,
#         mocker: MockerFixture,
#     ) -> None:

#         workspace_project: WorkspaceProject = create_workspace_project()
#         workspace_root = create_workspace_root(path=FullPath(tmp_path))
#         workspace_context = mocker.Mock(WorkspaceContext)
#         workspace_context.workspace_root = workspace_root
#         expected_paths = (ProjectRelativePath(Path("test_support/helpers.py")),)
#         get_paths_mock = mocker.patch(
#             "gyomu_test.helper.inventory.config._get_helper_file_paths",
#             return_value=Success(expected_paths),
#         )

#         result = get_helper_file_paths_from_workspace_project(
#             workspace_context=workspace_context,
#             workspace_project=workspace_project,
#         )

#         assert result == Success(expected_paths)
#         get_paths_mock.assert_called_once_with(
#             project_root=workspace_root.path / workspace_project.path,
#         )


class TestGetHelperFilePaths:
    def test_success(
        self,
        mocker: MockerFixture,
    ) -> None:
        project_context: ProjectContext = create_project_context()
        expected_paths = (ProjectRelativePath(Path("test_support/helpers.py")),)
        get_paths_mock = mocker.patch(
            "gyomu_test.helper.inventory.config._get_helper_file_paths_from_project_context",
            return_value=Success(expected_paths),
        )

        result = get_helper_file_paths(project_context=project_context)

        assert result == Success(expected_paths)
        get_paths_mock.assert_called_once_with(
            project_context=project_context,
        )


class TestGetHelperFilePath:
    def test_returns_default_helpers_file_when_no_allocation_matches(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context(project_root=FullPath(tmp_path))
        model_identity = simple_create_declaration_identity("package.other::Model")
        helper_config = HelperConfig(
            helper_directory="test_support",
            file_allocation=(
                HelperFileAllocation(
                    path=PythonPath("package.models"),
                    helper_filename="models.py",
                ),
            ),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.config._load_helper_config_with_default",
            return_value=Success(helper_config),
        )

        # Act
        result = get_helper_file_path(
            model_identity=model_identity,
            project_context=project_context,
        )

        # Assert
        assert result == Success(tmp_path / "test_support" / "helpers.py")

    def test_returns_allocated_file_when_module_path_matches_exactly(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context(project_root=FullPath(tmp_path))
        model_identity = simple_create_declaration_identity("package.models::Model")
        helper_config = HelperConfig(
            helper_directory="test_support",
            file_allocation=(
                HelperFileAllocation(
                    path=PythonPath("package.models"),
                    helper_filename="models.py",
                ),
            ),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.config._load_helper_config_with_default",
            return_value=Success(helper_config),
        )

        # Act
        result = get_helper_file_path(
            model_identity=model_identity,
            project_context=project_context,
        )

        # Assert
        assert result == Success(tmp_path / "test_support" / "models.py")

    def test_returns_allocated_file_for_submodule(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context(project_root=FullPath(tmp_path))
        model_identity = simple_create_declaration_identity(
            "package.models.customer::Customer"
        )
        helper_config = HelperConfig(
            helper_directory="test_support",
            file_allocation=(
                HelperFileAllocation(
                    path=PythonPath("package.models"),
                    helper_filename="models.py",
                ),
            ),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.config._load_helper_config_with_default",
            return_value=Success(helper_config),
        )

        # Act
        result = get_helper_file_path(
            model_identity=model_identity,
            project_context=project_context,
        )

        # Assert
        assert result == Success(tmp_path / "test_support" / "models.py")

    def test_prefers_longest_matching_allocation_path(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context(project_root=FullPath(tmp_path))
        model_identity = simple_create_declaration_identity(
            "package.models.customer::Customer"
        )
        helper_config = HelperConfig(
            helper_directory="test_support",
            file_allocation=(
                HelperFileAllocation(
                    path=PythonPath("package"),
                    helper_filename="package.py",
                ),
                HelperFileAllocation(
                    path=PythonPath("package.models"),
                    helper_filename="models.py",
                ),
                HelperFileAllocation(
                    path=PythonPath("package.models.customer"),
                    helper_filename="customers.py",
                ),
            ),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.config._load_helper_config_with_default",
            return_value=Success(helper_config),
        )

        # Act
        result = get_helper_file_path(
            model_identity=model_identity,
            project_context=project_context,
        )

        # Assert
        assert result == Success(tmp_path / "test_support" / "customers.py")

    def test_does_not_match_module_path_with_same_prefix_but_different_segment(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context(project_root=FullPath(tmp_path))
        model_identity = simple_create_declaration_identity(
            "package.models_extra::Model"
        )
        helper_config = HelperConfig(
            helper_directory="test_support",
            file_allocation=(
                HelperFileAllocation(
                    path=PythonPath("package.models"),
                    helper_filename="models.py",
                ),
            ),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.config._load_helper_config_with_default",
            return_value=Success(helper_config),
        )

        # Act
        result = get_helper_file_path(
            model_identity=model_identity,
            project_context=project_context,
        )

        # Assert
        assert result == Success(tmp_path / "test_support" / "helpers.py")

    def test_returns_failure_when_loading_helper_config_fails(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context(project_root=FullPath(tmp_path))
        model_identity = simple_create_declaration_identity("package.models::Model")
        error = GyomuTestError(message="Failed to load helper config")
        mocker.patch(
            "gyomu_test.helper.inventory.config._load_helper_config_with_default",
            return_value=Failure(error),
        )

        # Act
        result = get_helper_file_path(
            model_identity=model_identity,
            project_context=project_context,
        )

        # Assert
        assert result == Failure(error)
