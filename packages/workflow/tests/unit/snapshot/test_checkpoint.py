from pathlib import Path

from gyomu_schema.error.gyomu import GyomuError
from gyomu_workflow.snapshot.checkpoint import (
    Checkpoint,
    PipelineStep,
    initialize_checkpoint,
    load_checkpoint,
    update_checkpoint,
)
from returns.result import Failure, Success


def test_initialize_checkpoint() -> None:
    result = initialize_checkpoint("example")

    assert result == Checkpoint(
        package="example",
        completed_steps=(),
    )


def test_load_checkpoint_success(
    mocker,
    snapshot_request,
    tmp_path,
) -> None:
    checkpoint = Checkpoint(
        package="example",
        completed_steps=(PipelineStep.DIRECTORY_CONCEPT,),
    )
    checkpoint_path = tmp_path / "Checkpoint.json"
    checkpoint_path.touch()

    mocker.patch(
        "gyomu_workflow.snapshot.checkpoint._get_checkpoint_path",
        return_value=checkpoint_path,
    )

    read_json = mocker.patch(
        "gyomu_workflow.snapshot.checkpoint.read_json",
        return_value=Success(checkpoint),
    )

    result = load_checkpoint(snapshot_request)

    assert result == checkpoint
    read_json.assert_called_once_with(
        path=checkpoint_path,
        model_type=Checkpoint,
    )


def test_load_checkpoint_when_file_does_not_exist(
    mocker,
    snapshot_request,
    tmp_path,
) -> None:
    checkpoint_path = tmp_path / "Checkpoint.json"

    mocker.patch(
        "gyomu_workflow.snapshot.checkpoint._get_checkpoint_path",
        return_value=checkpoint_path,
    )

    read_json = mocker.patch(
        "gyomu_workflow.snapshot.checkpoint.read_json",
    )

    result = load_checkpoint(snapshot_request)

    assert result == Checkpoint(
        package=snapshot_request.project_context.config.name,
        completed_steps=(),
    )
    read_json.assert_not_called()


def test_load_checkpoint_when_read_fails(
    mocker,
    snapshot_request,
    tmp_path,
) -> None:
    checkpoint_path = tmp_path / "Checkpoint.json"
    checkpoint_path.touch()
    error = GyomuError(
        message="failed to read checkpoint",
        domain="filesystem",
        operation="read_json",
        reason="external_failure",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.checkpoint._get_checkpoint_path",
        return_value=checkpoint_path,
    )

    mocker.patch(
        "gyomu_workflow.snapshot.checkpoint.read_json",
        return_value=Failure(error),
    )

    result = load_checkpoint(snapshot_request)

    assert result == Checkpoint(
        package=snapshot_request.project_context.config.name,
        completed_steps=(),
    )


def test_update_checkpoint_adds_step(
    mocker,
    snapshot_request,
) -> None:
    checkpoint = Checkpoint(
        package="example",
        completed_steps=(PipelineStep.DIRECTORY_CONCEPT,),
    )
    checkpoint_path = Path(".gyomu/checkpoint/test/Checkpoint.json")

    mocker.patch(
        "gyomu_workflow.snapshot.checkpoint._get_checkpoint_path",
        return_value=checkpoint_path,
    )
    write_json = mocker.patch(
        "gyomu_workflow.snapshot.checkpoint.write_json",
        return_value=Success(None),
    )

    result = update_checkpoint(
        checkpoint=checkpoint,
        request=snapshot_request,
        status_to_add=PipelineStep.PACKAGE_CONCEPT,
    )

    expected = Checkpoint(
        package="example",
        completed_steps=(
            PipelineStep.DIRECTORY_CONCEPT,
            PipelineStep.PACKAGE_CONCEPT,
        ),
    )

    assert result == Success(expected)
    write_json.assert_called_once_with(
        path=checkpoint_path,
        value=expected,
        value_type=Checkpoint,
    )


def test_update_checkpoint_does_not_duplicate_step(
    mocker,
    snapshot_request,
) -> None:
    checkpoint = Checkpoint(
        package="example",
        completed_steps=(
            PipelineStep.DIRECTORY_CONCEPT,
            PipelineStep.PACKAGE_CONCEPT,
        ),
    )
    checkpoint_path = Path(".gyomu/checkpoint/test/Checkpoint.json")

    mocker.patch(
        "gyomu_workflow.snapshot.checkpoint._get_checkpoint_path",
        return_value=checkpoint_path,
    )
    write_json = mocker.patch(
        "gyomu_workflow.snapshot.checkpoint.write_json",
        return_value=Success(None),
    )

    result = update_checkpoint(
        checkpoint=checkpoint,
        request=snapshot_request,
        status_to_add=PipelineStep.PACKAGE_CONCEPT,
    )

    assert result == Success(checkpoint)
    write_json.assert_called_once_with(
        path=checkpoint_path,
        value=checkpoint,
        value_type=Checkpoint,
    )


def test_update_checkpoint_write_failure(
    mocker,
    snapshot_request,
) -> None:
    checkpoint = Checkpoint(
        package="example",
        completed_steps=(PipelineStep.DIRECTORY_CONCEPT,),
    )
    checkpoint_path = Path(".gyomu/checkpoint/test/Checkpoint.json")

    error = GyomuError(
        message="failed to write checkpoint",
        domain="filesystem",
        operation="write_json",
        reason="external_failure",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.checkpoint._get_checkpoint_path",
        return_value=checkpoint_path,
    )
    mocker.patch(
        "gyomu_workflow.snapshot.checkpoint.write_json",
        return_value=Failure(error),
    )

    result = update_checkpoint(
        checkpoint=checkpoint,
        request=snapshot_request,
        status_to_add=PipelineStep.PACKAGE_CONCEPT,
    )

    assert isinstance(result, Failure)
