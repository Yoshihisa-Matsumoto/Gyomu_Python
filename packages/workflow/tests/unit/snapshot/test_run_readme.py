import pytest
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.snapshot.types import ProjectSnapshot
from gyomu_workflow.snapshot.checkpoint import (
    Checkpoint,
    PipelineStep,
    SnapshotActionResult,
)
from gyomu_workflow.snapshot.run_readme import run_readme_action
from returns.result import Failure, Success


@pytest.mark.asyncio
async def test_run_readme_action_success(
    mocker,
    snapshot_request,
    checkpoint,
    concept_option: ConceptOption,
):
    package_concept = mocker.Mock()

    mocker.patch(
        "gyomu_workflow.snapshot.run_readme.generate_readme_files",
        return_value=Success(package_concept),
    )

    snapshot = mocker.Mock(spec=ProjectSnapshot)
    update_snapshot = mocker.patch(
        "gyomu_workflow.snapshot.run_readme.update_snapshot",
        return_value=Success(snapshot),
    )

    updated_checkpoint = Checkpoint(
        package=checkpoint.package,
        completed_steps=(PipelineStep.PACKAGE_CONCEPT,),
    )
    update_checkpoint = mocker.patch(
        "gyomu_workflow.snapshot.run_readme.update_checkpoint",
        return_value=Success(updated_checkpoint),
    )

    result = await run_readme_action(
        current_checkpoint=checkpoint,
        request=snapshot_request,
        option=concept_option,
    )

    assert isinstance(result, Success)

    action_result = result.unwrap()
    assert isinstance(action_result, SnapshotActionResult)
    assert action_result.checkpoint == updated_checkpoint
    assert action_result.snapshot == snapshot

    update_snapshot.assert_called_once_with(snapshot_request)
    update_checkpoint.assert_called_once_with(
        checkpoint=checkpoint,
        request=snapshot_request,
        status_to_add=PipelineStep.README,
    )


@pytest.mark.asyncio
async def test_run_readme_action_returns_failure_when_build_fails(
    mocker,
    snapshot_request,
    checkpoint,
    concept_option: ConceptOption,
):
    error = GyomuError(
        message="package concept failed",
        domain="concept",
        operation="generate_readme_files",
        reason="external_failure",
        context="test",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run_readme.generate_readme_files",
        return_value=Failure(error),
    )
    update_snapshot = mocker.patch("gyomu_workflow.snapshot.run_readme.update_snapshot")
    update_checkpoint = mocker.patch(
        "gyomu_workflow.snapshot.run_readme.update_checkpoint"
    )

    result = await run_readme_action(
        current_checkpoint=checkpoint,
        request=snapshot_request,
        option=concept_option,
    )

    assert isinstance(result, Failure)
    update_snapshot.assert_not_called()
    update_checkpoint.assert_not_called()


@pytest.mark.asyncio
async def test_run_readme_action_returns_failure_when_snapshot_update_fails(
    mocker,
    snapshot_request,
    checkpoint,
    concept_option: ConceptOption,
):
    mocker.patch(
        "gyomu_workflow.snapshot.run_readme.generate_readme_files",
        return_value=Success(mocker.Mock()),
    )

    error = GyomuError(
        message="snapshot failed",
        domain="snapshot",
        operation="update_snapshot",
        reason="external_failure",
        context="test",
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run_readme.update_snapshot",
        return_value=Failure(error),
    )

    update_checkpoint = mocker.patch(
        "gyomu_workflow.snapshot.run_readme.update_checkpoint"
    )

    result = await run_readme_action(
        current_checkpoint=checkpoint,
        request=snapshot_request,
        option=concept_option,
    )

    assert isinstance(result, Failure)
    assert result.failure() == error
    update_checkpoint.assert_not_called()


@pytest.mark.asyncio
async def test_run_readme_action_returns_failure_when_checkpoint_update_fails(
    mocker,
    snapshot_request,
    checkpoint,
    concept_option: ConceptOption,
):
    mocker.patch(
        "gyomu_workflow.snapshot.run_readme.generate_readme_files",
        return_value=Success(mocker.Mock()),
    )

    snapshot = mocker.Mock(spec=ProjectSnapshot)
    mocker.patch(
        "gyomu_workflow.snapshot.run_readme.update_snapshot",
        return_value=Success(snapshot),
    )

    error = GyomuError(
        message="checkpoint failed",
        domain="snapshot",
        operation="update_checkpoint",
        reason="external_failure",
        context="test",
    )
    update_checkpoint = mocker.patch(
        "gyomu_workflow.snapshot.run_readme.update_checkpoint",
        return_value=Failure(error),
    )

    result = await run_readme_action(
        current_checkpoint=checkpoint,
        request=snapshot_request,
        option=concept_option,
    )

    assert isinstance(result, Failure)
    assert result.failure() == error

    update_checkpoint.assert_called_once_with(
        checkpoint=checkpoint,
        request=snapshot_request,
        status_to_add=PipelineStep.README,
    )
