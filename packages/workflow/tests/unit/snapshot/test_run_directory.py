from pathlib import Path

import pytest
from gyomu_concept.error.concept import ConceptError
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.snapshot.types import ProjectSnapshot
from gyomu_workflow.snapshot.checkpoint import (
    Checkpoint,
    PipelineStep,
    SnapshotActionResult,
)
from gyomu_workflow.snapshot.models import SnapshotRequest
from gyomu_workflow.snapshot.run_directory import run_directory_action
from returns.result import Failure, Success


@pytest.mark.asyncio
async def test_run_directory_action_success(
    mocker,
    snapshot_request: SnapshotRequest,
    concept_option: ConceptOption,
) -> None:
    current_checkpoint = Checkpoint(
        package="example",
        completed_steps=(),
    )
    updated_checkpoint = Checkpoint(
        package="example",
        completed_steps=(PipelineStep.DIRECTORY_CONCEPT,),
    )
    current_snapshot = ProjectSnapshot(
        project_root=WorkspaceRelativePath(Path("/tmp")), files=tuple()
    )

    build = mocker.patch(
        "gyomu_workflow.snapshot.run_directory.build_directory_concept",
        new_callable=mocker.AsyncMock,
        return_value=Success(None),
    )
    update_snapshot = mocker.patch(
        "gyomu_workflow.snapshot.run_directory.update_snapshot",
        return_value=Success(current_snapshot),
    )
    update_checkpoint = mocker.patch(
        "gyomu_workflow.snapshot.run_directory.update_checkpoint",
        return_value=Success(updated_checkpoint),
    )

    result = await run_directory_action(
        current_checkpoint=current_checkpoint,
        request=snapshot_request,
        option=concept_option,
    )

    assert result == Success(
        SnapshotActionResult(checkpoint=updated_checkpoint, snapshot=current_snapshot)
    )

    build.assert_awaited_once_with(
        context=snapshot_request.project_context,
        option=concept_option,
    )
    update_snapshot.assert_called_once_with(snapshot_request)
    update_checkpoint.assert_called_once_with(
        checkpoint=current_checkpoint,
        request=snapshot_request,
        status_to_add=PipelineStep.DIRECTORY_CONCEPT,
    )


@pytest.mark.asyncio
async def test_run_directory_action_build_failure(
    mocker,
    snapshot_request: SnapshotRequest,
    concept_option: ConceptOption,
) -> None:
    current_checkpoint = Checkpoint(
        package="example",
        completed_steps=(),
    )
    error = ConceptError(
        message="failed to build directory concept",
        package_name="test",
        file_path=Path("tmp"),
        phase="directory-summary",
        identity=None,
    )

    build = mocker.patch(
        "gyomu_workflow.snapshot.run_directory.build_directory_concept",
        new_callable=mocker.AsyncMock,
        return_value=Failure(error),
    )
    update_snapshot = mocker.patch(
        "gyomu_workflow.snapshot.run_directory.update_snapshot",
    )
    update_checkpoint = mocker.patch(
        "gyomu_workflow.snapshot.run_directory.update_checkpoint",
    )

    result = await run_directory_action(
        current_checkpoint=current_checkpoint,
        request=snapshot_request,
        option=concept_option,
    )

    assert isinstance(result, Failure)

    build.assert_awaited_once_with(
        context=snapshot_request.project_context,
        option=concept_option,
    )
    update_snapshot.assert_not_called()
    update_checkpoint.assert_not_called()

    actual_error = result.failure()
    assert isinstance(actual_error, GyomuError)
    assert actual_error.message == "fail to generate directory concept"
    assert actual_error.domain == "snapshot"
    assert actual_error.operation == "run_actions"
    assert actual_error.reason == "external_failure"


@pytest.mark.asyncio
async def test_run_directory_action_snapshot_failure(
    mocker,
    snapshot_request: SnapshotRequest,
    concept_option: ConceptOption,
) -> None:
    current_checkpoint = Checkpoint(
        package="example",
        completed_steps=(),
    )
    snapshot_error = GyomuError(
        message="failed to update snapshot",
        domain="snapshot",
        operation="update_snapshot",
        reason="external_failure",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run_directory.build_directory_concept",
        new_callable=mocker.AsyncMock,
        return_value=Success(None),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run_directory.update_snapshot",
        return_value=Failure(snapshot_error),
    )
    update_checkpoint = mocker.patch(
        "gyomu_workflow.snapshot.run_directory.update_checkpoint",
    )

    result = await run_directory_action(
        current_checkpoint=current_checkpoint,
        request=snapshot_request,
        option=concept_option,
    )

    assert result == Failure(snapshot_error)
    update_checkpoint.assert_not_called()


@pytest.mark.asyncio
async def test_run_directory_action_checkpoint_failure(
    mocker,
    snapshot_request: SnapshotRequest,
    concept_option: ConceptOption,
) -> None:
    current_checkpoint = Checkpoint(
        package="example",
        completed_steps=(),
    )
    checkpoint_error = GyomuError(
        message="failed to update checkpoint",
        domain="snapshot",
        operation="update_checkpoint",
        reason="external_failure",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run_directory.build_directory_concept",
        new_callable=mocker.AsyncMock,
        return_value=Success(None),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run_directory.update_snapshot",
        return_value=Success(None),
    )
    update_checkpoint = mocker.patch(
        "gyomu_workflow.snapshot.run_directory.update_checkpoint",
        return_value=Failure(checkpoint_error),
    )

    result = await run_directory_action(
        current_checkpoint=current_checkpoint,
        request=snapshot_request,
        option=concept_option,
    )

    assert result == Failure(checkpoint_error)

    update_checkpoint.assert_called_once_with(
        checkpoint=current_checkpoint,
        request=snapshot_request,
        status_to_add=PipelineStep.DIRECTORY_CONCEPT,
    )
