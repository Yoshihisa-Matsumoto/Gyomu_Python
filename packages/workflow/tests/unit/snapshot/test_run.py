from pathlib import Path

import pytest
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.snapshot.types import ProjectSnapshot
from gyomu_workflow.snapshot.checkpoint import (
    Checkpoint,
    PipelineStep,
    SnapshotActionResult,
)
from gyomu_workflow.snapshot.run import (
    build_docstring_update_option,
    is_source_file,
    run_actions,
    run_snapshot,
)
from returns.result import Failure, Success


@pytest.mark.asyncio
async def test_target_resolution_failure(
    mocker,
    snapshot_request,
):
    error = GyomuError(
        message="target failed",
        domain="test",
        operation="test",
        reason="invalid_input",
    )

    resolve_snapshot_target = mocker.patch(
        "gyomu_workflow.snapshot.run.resolve_snapshot_target",
        return_value=Failure(error),
    )
    run_actions = mocker.patch(
        "gyomu_workflow.snapshot.run.run_actions",
    )
    commit_project_changes = mocker.patch(
        "gyomu_workflow.snapshot.run.commit_project_changes",
    )

    result = await run_snapshot(snapshot_request)

    assert isinstance(result, Failure)
    assert result.failure() is error

    resolve_snapshot_target.assert_called_once_with(
        repository_root_path=snapshot_request.repository_root_path,
        project_context=snapshot_request.project_context,
        option=snapshot_request.option.target,
    )
    run_actions.assert_not_called()
    commit_project_changes.assert_not_called()


@pytest.mark.asyncio
async def test_action_failure(
    mocker,
    snapshot_request,
    snapshot_target,
):
    error = GyomuError(
        message="action failed",
        domain="test",
        operation="test",
        reason="invalid_input",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run.resolve_snapshot_target",
        return_value=Success(snapshot_target),
    )
    run_actions = mocker.patch(
        "gyomu_workflow.snapshot.run.run_actions",
        return_value=Failure(error),
    )
    commit_project_changes = mocker.patch(
        "gyomu_workflow.snapshot.run.commit_project_changes",
    )

    result = await run_snapshot(snapshot_request)

    assert isinstance(result, Failure)
    assert result.failure() is error

    run_actions.assert_awaited_once_with(
        request=snapshot_request,
        target=snapshot_target,
    )
    commit_project_changes.assert_not_called()


@pytest.mark.asyncio
async def test_commit_disabled(
    mocker,
    snapshot_request,
    snapshot_target,
    current_snapshot,
):
    snapshot_request.option.commit = False

    mocker.patch(
        "gyomu_workflow.snapshot.run.resolve_snapshot_target",
        return_value=Success(snapshot_target),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.run_actions",
        return_value=Success(current_snapshot),
    )
    commit_project_changes = mocker.patch(
        "gyomu_workflow.snapshot.run.commit_project_changes",
    )

    result = await run_snapshot(snapshot_request)

    assert isinstance(result, Success)
    assert result.unwrap() is None

    commit_project_changes.assert_not_called()


@pytest.mark.asyncio
async def test_commit_enabled(
    mocker,
    snapshot_request,
    snapshot_target,
    current_snapshot,
):
    snapshot_request.option.commit = True

    mocker.patch(
        "gyomu_workflow.snapshot.run.resolve_snapshot_target",
        return_value=Success(snapshot_target),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.run_actions",
        return_value=Success(current_snapshot),
    )
    commit_project_changes = mocker.patch(
        "gyomu_workflow.snapshot.run.commit_project_changes",
        return_value=Success(None),
    )

    result = await run_snapshot(snapshot_request)

    assert isinstance(result, Success)
    assert result.unwrap() is None

    commit_project_changes.assert_called_once_with(
        repository_root_path=snapshot_request.repository_root_path,
        project_context=snapshot_request.project_context,
        expected_snapshot=current_snapshot,
    )


@pytest.mark.asyncio
async def test_commit_failure(
    mocker,
    snapshot_request,
    snapshot_target,
    current_snapshot,
):
    snapshot_request.option.commit = True

    error = GyomuError(
        message="commit failed",
        domain="test",
        operation="commit",
        reason="invalid_input",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run.resolve_snapshot_target",
        return_value=Success(snapshot_target),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.run_actions",
        return_value=Success(current_snapshot),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.commit_project_changes",
        return_value=Failure(error),
    )

    result = await run_snapshot(snapshot_request)

    assert isinstance(result, Failure)

    wrapped_error = result.failure()

    assert wrapped_error.message == "fail to commit project changes"
    assert wrapped_error.domain == "snapshot"
    assert wrapped_error.operation == "run_snapshot"
    assert wrapped_error.reason == "external_failure"

    assert wrapped_error.__cause__ is not None


@pytest.mark.asyncio
async def test_run_actions_runs_directory_and_package_concept(
    mocker,
    snapshot_request,
    snapshot_target,
):
    snapshot_request.option.action.project_context = True
    snapshot_request.option.action.docstring.enabled = False

    initial_checkpoint = Checkpoint(
        package="test",
        completed_steps=tuple(),
    )

    directory_checkpoint = Checkpoint(
        package="test",
        completed_steps=(PipelineStep.DIRECTORY_CONCEPT,),
    )
    directory_snapshot = mocker.Mock(spec=ProjectSnapshot)

    package_checkpoint = Checkpoint(
        package="test",
        completed_steps=(
            PipelineStep.DIRECTORY_CONCEPT,
            PipelineStep.PACKAGE_CONCEPT,
        ),
    )
    package_snapshot = mocker.Mock(spec=ProjectSnapshot)

    mocker.patch(
        "gyomu_workflow.snapshot.run.analyze_project_changes",
        return_value=Success(mocker.Mock(current_snapshot=snapshot_target.snapshot)),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.load_checkpoint",
        return_value=initial_checkpoint,
    )

    run_directory_action = mocker.patch(
        "gyomu_workflow.snapshot.run.run_directory_action",
        return_value=Success(
            SnapshotActionResult(
                checkpoint=directory_checkpoint,
                snapshot=directory_snapshot,
            )
        ),
    )
    run_package_action = mocker.patch(
        "gyomu_workflow.snapshot.run.run_package_action",
        return_value=Success(
            SnapshotActionResult(
                checkpoint=package_checkpoint,
                snapshot=package_snapshot,
            )
        ),
    )

    result = await run_actions(
        request=snapshot_request,
        target=snapshot_target,
    )

    assert isinstance(result, Success)
    assert result.unwrap() is package_snapshot

    run_directory_action.assert_awaited_once()

    run_package_action.assert_awaited_once_with(
        request=snapshot_request,
        current_checkpoint=directory_checkpoint,
        option=run_package_action.call_args.kwargs["option"],
    )


@pytest.mark.asyncio
async def test_run_actions_skips_completed_directory_concept(
    mocker,
    snapshot_request,
    snapshot_target,
):
    snapshot_request.option.action.project_context = True
    snapshot_request.option.action.docstring.enabled = False

    checkpoint = Checkpoint(
        package="test",
        completed_steps=(PipelineStep.DIRECTORY_CONCEPT,),
    )

    package_checkpoint = Checkpoint(
        package="test",
        completed_steps=(
            PipelineStep.DIRECTORY_CONCEPT,
            PipelineStep.PACKAGE_CONCEPT,
        ),
    )
    package_snapshot = mocker.Mock(spec=ProjectSnapshot)

    mocker.patch(
        "gyomu_workflow.snapshot.run.analyze_project_changes",
        return_value=Success(mocker.Mock(current_snapshot=snapshot_target.snapshot)),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.load_checkpoint",
        return_value=checkpoint,
    )

    run_directory_action = mocker.patch(
        "gyomu_workflow.snapshot.run.run_directory_action",
    )
    run_package_action = mocker.patch(
        "gyomu_workflow.snapshot.run.run_package_action",
        return_value=Success(
            SnapshotActionResult(
                checkpoint=package_checkpoint,
                snapshot=package_snapshot,
            )
        ),
    )

    result = await run_actions(
        request=snapshot_request,
        target=snapshot_target,
    )

    assert isinstance(result, Success)
    assert result.unwrap() is package_snapshot

    run_directory_action.assert_not_awaited()
    run_package_action.assert_awaited_once_with(
        request=snapshot_request,
        current_checkpoint=checkpoint,
        option=run_package_action.call_args.kwargs["option"],
    )


@pytest.mark.asyncio
async def test_run_actions_skips_completed_concepts(
    mocker,
    snapshot_request,
    snapshot_target,
):
    snapshot_request.option.action.project_context = True
    snapshot_request.option.action.docstring.enabled = False

    checkpoint = Checkpoint(
        package="test",
        completed_steps=(
            PipelineStep.DIRECTORY_CONCEPT,
            PipelineStep.PACKAGE_CONCEPT,
        ),
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run.analyze_project_changes",
        return_value=Success(mocker.Mock(current_snapshot=snapshot_target.snapshot)),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.load_checkpoint",
        return_value=checkpoint,
    )

    run_directory_action = mocker.patch(
        "gyomu_workflow.snapshot.run.run_directory_action",
    )
    run_package_action = mocker.patch(
        "gyomu_workflow.snapshot.run.run_package_action",
    )

    result = await run_actions(
        request=snapshot_request,
        target=snapshot_target,
    )

    assert isinstance(result, Success)
    assert result.unwrap() is snapshot_target.snapshot

    run_directory_action.assert_not_awaited()
    run_package_action.assert_not_awaited()


@pytest.mark.asyncio
async def test_run_actions_returns_directory_failure(
    mocker,
    snapshot_request,
    snapshot_target,
):
    snapshot_request.option.action.project_context = True
    snapshot_request.option.action.docstring.enabled = False

    checkpoint = Checkpoint(
        package="test",
        completed_steps=tuple(),
    )

    error = GyomuError(
        message="directory concept failed",
        domain="test",
        operation="test",
        reason="invalid_input",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run.analyze_project_changes",
        return_value=Success(mocker.Mock(current_snapshot=snapshot_target.snapshot)),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.load_checkpoint",
        return_value=checkpoint,
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.run_directory_action",
        return_value=Failure(error),
    )
    run_package_action = mocker.patch(
        "gyomu_workflow.snapshot.run.run_package_action",
    )

    result = await run_actions(
        request=snapshot_request,
        target=snapshot_target,
    )

    assert isinstance(result, Failure)
    assert result.failure() is error

    run_package_action.assert_not_awaited()


@pytest.mark.asyncio
async def test_run_actions_returns_package_failure(
    mocker,
    snapshot_request,
    snapshot_target,
):
    snapshot_request.option.action.project_context = True
    snapshot_request.option.action.docstring.enabled = False

    checkpoint = Checkpoint(
        package="test",
        completed_steps=(PipelineStep.DIRECTORY_CONCEPT,),
    )

    error = GyomuError(
        message="package concept failed",
        domain="test",
        operation="test",
        reason="invalid_input",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run.analyze_project_changes",
        return_value=Success(mocker.Mock(current_snapshot=snapshot_target.snapshot)),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.load_checkpoint",
        return_value=checkpoint,
    )
    run_directory_action = mocker.patch(
        "gyomu_workflow.snapshot.run.run_directory_action",
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run.run_package_action",
        return_value=Failure(error),
    )

    result = await run_actions(
        request=snapshot_request,
        target=snapshot_target,
    )

    assert isinstance(result, Failure)
    assert result.failure() is error

    run_directory_action.assert_not_awaited()


def test_build_docstring_update_option():
    option = build_docstring_update_option("docstring-debug")

    assert option.no_check_cache is True

    assert option.debug_info.dump_to_file is True
    assert option.debug_info.updated_symbol_docstring is True
    assert option.debug_info.file_update_plan is True
    assert option.debug_info.rendered_symbol_docstring is True
    assert option.debug_info.docstring_update_plan is True
    assert option.debug_info.docstring_update_context is True
    assert option.debug_info.keyword == "docstring-debug"


def test_build_docstring_update_option_without_keyword():
    option = build_docstring_update_option(None)

    assert option.debug_info.keyword is None


@pytest.mark.parametrize(
    ("file_path", "source_root", "expected"),
    [
        (
            ProjectRelativePath(Path("src/example.py")),
            ProjectRelativePath(Path("src")),
            True,
        ),
        (
            ProjectRelativePath(Path("src/sub/example.py")),
            ProjectRelativePath(Path("src")),
            True,
        ),
        (
            ProjectRelativePath(Path("tests/example.py")),
            ProjectRelativePath(Path("src")),
            False,
        ),
        (
            ProjectRelativePath(Path("src2/example.py")),
            ProjectRelativePath(Path("src")),
            False,
        ),
    ],
)
def test_is_source_file(file_path, source_root, expected):
    assert is_source_file(file_path, source_root) is expected
