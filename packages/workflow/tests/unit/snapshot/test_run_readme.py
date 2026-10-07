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


@pytest.mark.asyncio
async def test_run_readme_action_skips_when_completed_and_files_exist(
    mocker,
    snapshot_request,
    checkpoint,
    concept_option: ConceptOption,
):
    completed_checkpoint = Checkpoint(
        package=checkpoint.package,
        completed_steps=(PipelineStep.README,),
    )

    output_file_path = mocker.Mock()
    output_file_path.exists.return_value = True

    mocker.patch(
        "gyomu_workflow.snapshot.run_readme."
        "README_DOCUMENT_DEFINITION.output.filepath_resolver.resolve",
        return_value=output_file_path,
    )

    generate_readme_files = mocker.patch(
        "gyomu_workflow.snapshot.run_readme.generate_readme_files"
    )
    update_snapshot = mocker.patch("gyomu_workflow.snapshot.run_readme.update_snapshot")
    update_checkpoint = mocker.patch(
        "gyomu_workflow.snapshot.run_readme.update_checkpoint"
    )

    result = await run_readme_action(
        current_checkpoint=completed_checkpoint,
        request=snapshot_request,
        option=concept_option,
    )

    assert isinstance(result, Success)

    action_result = result.unwrap()
    assert action_result.checkpoint == completed_checkpoint
    assert action_result.snapshot is None

    generate_readme_files.assert_not_called()
    update_snapshot.assert_not_called()
    update_checkpoint.assert_not_called()


@pytest.mark.asyncio
async def test_run_readme_action_regenerates_when_readme_file_is_missing(
    mocker,
    snapshot_request,
    checkpoint,
    concept_option: ConceptOption,
):
    completed_checkpoint = Checkpoint(
        package=checkpoint.package,
        completed_steps=(PipelineStep.README,),
    )

    existing_path = mocker.Mock()
    existing_path.exists.return_value = True

    missing_path = mocker.Mock()
    missing_path.exists.return_value = False

    resolve = mocker.patch(
        "gyomu_workflow.snapshot.run_readme."
        "README_DOCUMENT_DEFINITION.output.filepath_resolver.resolve",
        side_effect=[existing_path, missing_path],
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run_readme.generate_readme_files",
        return_value=Success(mocker.Mock()),
    )

    snapshot = mocker.Mock(spec=ProjectSnapshot)
    mocker.patch(
        "gyomu_workflow.snapshot.run_readme.update_snapshot",
        return_value=Success(snapshot),
    )

    updated_checkpoint = Checkpoint(
        package=checkpoint.package,
        completed_steps=(PipelineStep.README,),
    )
    update_checkpoint = mocker.patch(
        "gyomu_workflow.snapshot.run_readme.update_checkpoint",
        return_value=Success(updated_checkpoint),
    )

    result = await run_readme_action(
        current_checkpoint=completed_checkpoint,
        request=snapshot_request,
        option=concept_option,
    )

    assert isinstance(result, Success)

    action_result = result.unwrap()
    assert action_result.checkpoint == updated_checkpoint
    assert action_result.snapshot == snapshot

    resolve.assert_called()
    update_checkpoint.assert_called_once_with(
        checkpoint=completed_checkpoint,
        request=snapshot_request,
        status_to_add=PipelineStep.README,
    )
