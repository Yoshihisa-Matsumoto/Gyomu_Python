from pathlib import Path
from unittest.mock import MagicMock

from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceProject,
)
from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.models import SnapshotExecutionOption, SnapshotRequest
from gyomu_workflow.snapshot.translate import translate_snapshot_request
from pytest_mock import MockerFixture


class TestTranslateSnapshotRequest:
    def test_creates_snapshot_request(self, mocker: MockerFixture) -> None:
        repository_root_path = FullPath(Path("/workspace"))
        workspace_context = MagicMock(spec=WorkspaceContext)
        workspace_context.path = repository_root_path

        target_package = MagicMock(spec=WorkspaceProject)
        option = MagicMock(spec=SnapshotExecutionOption)
        project_context = MagicMock()

        initialize_mock = mocker.patch(
            "gyomu_workflow.snapshot.translate.initialize_project_from_workspace",
            return_value=project_context,
        )

        result = translate_snapshot_request(
            workspace_context=workspace_context,
            target_package=target_package,
            option=option,
        )

        assert isinstance(result, SnapshotRequest)
        assert result.repository_root_path == repository_root_path
        assert result.project_context is project_context
        assert result.option is option
        assert result.project is target_package
        assert result.workspace is workspace_context

        initialize_mock.assert_called_once_with(
            repository_root_path,
            target_package,
        )
