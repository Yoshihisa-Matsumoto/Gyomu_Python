from pathlib import Path
from unittest.mock import call

import gyomu_workflow.test.helpers._internal.reconcile as helpers_module
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_analysis_error,
    create_project_context,
    create_workspace_context,
    create_workspace_project,
)
from packages.schema.test_support.helpers import (
    create_gyomu_error,
)
from packages.schema.test_support.testing_helpers import (
    create_helper_inventory_item,
    create_helper_reconcile_result,
)


class TestReconcileProject:
    def test_success(self, mocker: MockerFixture) -> None:
        # Arrange
        workspace_context = create_workspace_context()
        workspace_project = create_workspace_project()
        project_context = create_project_context()

        expected = (create_helper_inventory_item(),)
        existing = ()
        reconcile_result = create_helper_reconcile_result()

        initialize_project = mocker.patch.object(
            helpers_module,
            "initialize_project_from_workspace",
            return_value=project_context,
        )
        collect_expected = mocker.patch.object(
            helpers_module,
            "collect_model_helper_inventory",
            return_value=Success(expected),
        )
        initialize_root = mocker.patch.object(
            helpers_module,
            "initialize_project_context",
            return_value=Success(project_context),
        )
        collect_existing = mocker.patch.object(
            helpers_module,
            "collect_existing_helper_inventory",
            return_value=Success(existing),
        )
        reconcile = mocker.patch.object(
            helpers_module,
            "reconcile",
            return_value=reconcile_result,
        )

        # Act
        result = helpers_module.reconcile_package(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project,
        )

        # Assert
        assert result == Success((reconcile_result, project_context))

        initialize_project.assert_called_once_with(
            workspace_path=workspace_context.workspace_root.path,
            project=workspace_project,
        )
        collect_expected.assert_called_once_with(
            project_context,
            workspace_context,
        )
        initialize_root.assert_called_once_with(
            project_root=workspace_context.workspace_root.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        collect_existing.assert_called_once_with(
            root=project_context,
            target_project=project_context,
        )
        reconcile.assert_called_once_with(
            existing=existing,
            expected=expected,
        )

        # 呼び出し順序も確認する
        assert [
            initialize_project.call_args,
            collect_expected.call_args,
            initialize_root.call_args,
            collect_existing.call_args,
            reconcile.call_args,
        ] == [
            call(
                workspace_path=workspace_context.workspace_root.path,
                project=workspace_project,
            ),
            call(project_context, workspace_context),
            call(
                project_root=workspace_context.workspace_root.path,
                source_root=ProjectRelativePath(Path(".")),
            ),
            call(root=project_context, target_project=project_context),
            call(existing=existing, expected=expected),
        ]

    def test_collect_model_helper_inventory_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        workspace_context = create_workspace_context()
        workspace_project = create_workspace_project()
        project_context = create_project_context()
        error = create_gyomu_error(message="test error")

        mocker.patch.object(
            helpers_module,
            "initialize_project_from_workspace",
            return_value=project_context,
        )
        mocker.patch.object(
            helpers_module,
            "collect_model_helper_inventory",
            return_value=Failure(error),
        )
        initialize_root = mocker.patch.object(
            helpers_module,
            "initialize_project_context",
        )
        collect_existing = mocker.patch.object(
            helpers_module,
            "collect_existing_helper_inventory",
        )
        reconcile = mocker.patch.object(
            helpers_module,
            "reconcile",
        )

        # Act
        result = helpers_module.reconcile_package(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to collect inventories from models"
        initialize_root.assert_not_called()
        collect_existing.assert_not_called()
        reconcile.assert_not_called()

    def test_initialize_project_context_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        workspace_context = create_workspace_context()
        workspace_project = create_workspace_project()
        project_context = create_project_context()
        error = create_analysis_error(message="test error")

        mocker.patch.object(
            helpers_module,
            "initialize_project_from_workspace",
            return_value=project_context,
        )
        mocker.patch.object(
            helpers_module,
            "collect_model_helper_inventory",
            return_value=Success(()),
        )
        mocker.patch.object(
            helpers_module,
            "initialize_project_context",
            return_value=Failure(error),
        )
        collect_existing = mocker.patch.object(
            helpers_module,
            "collect_existing_helper_inventory",
        )
        reconcile = mocker.patch.object(
            helpers_module,
            "reconcile",
        )

        # Act
        result = helpers_module.reconcile_package(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to initialize project"
        collect_existing.assert_not_called()
        reconcile.assert_not_called()

    def test_collect_existing_helper_inventory_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        workspace_context = create_workspace_context()
        workspace_project = create_workspace_project()
        project_context = create_project_context()
        root_context = create_project_context(
            project_root=workspace_context.workspace_root.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        error = create_gyomu_error(message="test error")

        mocker.patch.object(
            helpers_module,
            "initialize_project_from_workspace",
            return_value=project_context,
        )
        mocker.patch.object(
            helpers_module,
            "collect_model_helper_inventory",
            return_value=Success(()),
        )
        initialize_root = mocker.patch.object(
            helpers_module,
            "initialize_project_context",
            return_value=Success(root_context),
        )
        collect_existing = mocker.patch.object(
            helpers_module,
            "collect_existing_helper_inventory",
            return_value=Failure(error),
        )
        reconcile = mocker.patch.object(
            helpers_module,
            "reconcile",
        )

        # Act
        result = helpers_module.reconcile_package(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to gather existing inventories"

        initialize_root.assert_called_once_with(
            project_root=workspace_context.workspace_root.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        collect_existing.assert_called_once_with(
            root=root_context,
            target_project=project_context,
        )
        reconcile.assert_not_called()
