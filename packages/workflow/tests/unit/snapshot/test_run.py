from dataclasses import replace
from pathlib import Path

import pytest
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_workflow.snapshot.checkpoint import PipelineStep, SnapshotActionResult
from gyomu_workflow.snapshot.models import SnapshotRequest
from gyomu_workflow.snapshot.run import (
    run_actions,
    run_snapshot,
)
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_analyze_project_change,
    create_project_snapshot,
)
from packages.workflow.test_support.helper import (
    create_checkpoint,
    create_snapshot_target,
)


def _request_with_actions(
    snapshot_request,
    *,
    docstring_enabled: bool = True,
    project_context: bool = False,
    unit_test: bool = False,
):
    action = snapshot_request.option.action.model_copy(
        update={
            "docstring": (
                snapshot_request.option.action.docstring.model_copy(
                    update={"enabled": docstring_enabled}
                )
            ),
            "project_context": project_context,
            "unit_test": unit_test,
        }
    )
    option = snapshot_request.option.model_copy(update={"action": action})
    return replace(snapshot_request, option=option)


class TestRunSnapshot:
    @pytest.mark.asyncio
    async def test_target_resolution_failure(
        self,
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
        self,
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
        analysis = create_analyze_project_change(
            current_snapshot=snapshot_target.snapshot
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.resolve_snapshot_target",
            return_value=Success((snapshot_target, analysis)),
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
            request=snapshot_request, target=snapshot_target, analysis=analysis
        )
        commit_project_changes.assert_not_called()

    @pytest.mark.asyncio
    async def test_commit_disabled(
        self,
        mocker,
        snapshot_request: SnapshotRequest,
        checkpoint,
    ):
        snapshot_request.option.commit = False
        snapshot_target = create_snapshot_target()
        analysis = create_analyze_project_change(
            current_snapshot=snapshot_target.snapshot
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.resolve_snapshot_target",
            return_value=Success((snapshot_target, analysis)),
        )
        current_snapshot = create_project_snapshot()
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
        self, mocker, snapshot_request, snapshot_target, current_snapshot, analysis
    ):
        snapshot_request.option.commit = True

        mocker.patch(
            "gyomu_workflow.snapshot.run.resolve_snapshot_target",
            return_value=Success((snapshot_target, analysis)),
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
        self, mocker, snapshot_request, snapshot_target, current_snapshot, analysis
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
            return_value=Success((snapshot_target, analysis)),
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


class TestRunActions_BasicFlow:
    async def test_returns_failure_when_loading_checkpoint_fails(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
    ):
        error = GyomuError(
            message="load checkpoint failed",
            domain="snapshot",
            operation="load_checkpoint",
            reason="external_failure",
            context="test",
        )
        load_checkpoint = mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Failure(error),
        )
        run_docstring_actions = mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
        )

        result = await run_actions(
            request=snapshot_request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

        load_checkpoint.assert_called_once_with(
            request=snapshot_request,
            target=snapshot_target,
        )
        run_docstring_actions.assert_not_called()

    async def test_runs_docstring_action(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
        current_snapshot,
    ):

        from gyomu_workflow.snapshot.run import run_actions
        from returns.result import Success

        request = replace(
            snapshot_request,
            option=snapshot_request.option.model_copy(
                update={
                    "action": snapshot_request.option.action.model_copy(
                        update={
                            "docstring": (
                                snapshot_request.option.action.docstring.model_copy(
                                    update={"enabled": False}
                                )
                            ),
                            "project_context": False,
                            "unit_test": False,
                        }
                    )
                }
            ),
        )

        updated_snapshot = create_project_snapshot(
            project_root=current_snapshot.project_root,
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        run_docstring_actions = mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=updated_snapshot,
                )
            ),
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == updated_snapshot

        run_docstring_actions.assert_awaited_once_with(
            request=request,
            current_checkpoint=checkpoint,
            target=snapshot_target,
        )

    async def test_returns_failure_when_docstring_action_fails(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
    ):
        error = GyomuError(
            message="docstring action failed",
            domain="snapshot",
            operation="run_docstring_actions",
            reason="external_failure",
            context="test",
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Failure(error),
        )
        run_directory_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_directory_action",
        )

        result = await run_actions(
            request=snapshot_request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

        run_directory_action.assert_not_called()

    async def test_returns_current_snapshot_when_no_post_actions_enabled(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
        current_snapshot,
    ):
        from dataclasses import replace

        request = replace(
            snapshot_request,
            option=snapshot_request.option.model_copy(
                update={
                    "action": snapshot_request.option.action.model_copy(
                        update={
                            "docstring": (
                                snapshot_request.option.action.docstring.model_copy(
                                    update={"enabled": False}
                                )
                            ),
                            "project_context": False,
                            "unit_test": False,
                        }
                    )
                }
            ),
        )
        updated_snapshot = create_project_snapshot(
            project_root=current_snapshot.project_root,
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=updated_snapshot,
                )
            ),
        )
        run_directory_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_directory_action",
        )
        run_package_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_package_action",
        )
        run_readme_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_readme_action",
        )
        run_llm_context_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_llm_context_action",
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == updated_snapshot

        run_directory_action.assert_not_called()
        run_package_action.assert_not_called()
        run_readme_action.assert_not_called()
        run_llm_context_action.assert_not_called()


class TestRunActions_Conditions:
    async def test_skips_post_actions_when_all_conditions_are_disabled(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=False,
            project_context=False,
            unit_test=False,
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=None,
                )
            ),
        )

        run_directory_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_directory_action",
        )
        run_package_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_package_action",
        )
        run_readme_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_readme_action",
        )
        run_llm_context_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_llm_context_action",
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == snapshot_target.snapshot

        run_directory_action.assert_not_called()
        run_package_action.assert_not_called()
        run_readme_action.assert_not_called()
        run_llm_context_action.assert_not_called()

    async def test_runs_post_actions_when_docstring_is_enabled(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=True,
            project_context=False,
            unit_test=False,
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=snapshot_target.snapshot,
                )
            ),
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == analysis.current_snapshot

    async def test_runs_post_actions_when_unit_test_is_enabled(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=False,
            project_context=False,
            unit_test=True,
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=snapshot_target.snapshot,
                )
            ),
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == analysis.current_snapshot

    async def test_runs_concept_actions_in_order(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
        concept_option,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=False,
            project_context=True,
            unit_test=False,
        )
        call_order = []

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.build_concept_update_option",
            return_value=concept_option,
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=None,
                )
            ),
        )

        def create_action_mock(name):
            async def action(*args, **kwargs):
                call_order.append(name)
                return Success(
                    SnapshotActionResult(
                        checkpoint=checkpoint,
                        snapshot=None,
                    )
                )

            return action

        mocker.patch(
            "gyomu_workflow.snapshot.run.run_directory_action",
            side_effect=create_action_mock("directory"),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_package_action",
            side_effect=create_action_mock("package"),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_readme_action",
            side_effect=create_action_mock("readme"),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_llm_context_action",
            side_effect=create_action_mock("llm_context"),
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Success)
        assert call_order == [
            "directory",
            "package",
            "readme",
            "llm_context",
        ]

    async def test_passes_updated_checkpoint_between_actions(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
        concept_option,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=False,
            project_context=True,
            unit_test=False,
        )

        directory_checkpoint = create_checkpoint(
            completed_steps=(PipelineStep.DOCSTRING,),
        )
        package_checkpoint = create_checkpoint(
            completed_steps=(
                PipelineStep.DOCSTRING,
                PipelineStep.DIRECTORY_CONCEPT,
            ),
        )
        readme_checkpoint = create_checkpoint(
            completed_steps=(
                PipelineStep.DOCSTRING,
                PipelineStep.DIRECTORY_CONCEPT,
                PipelineStep.PACKAGE_CONCEPT,
            ),
        )
        llm_checkpoint = create_checkpoint(
            completed_steps=tuple(PipelineStep),
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.build_concept_update_option",
            return_value=concept_option,
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=None,
                )
            ),
        )

        directory = mocker.patch(
            "gyomu_workflow.snapshot.run.run_directory_action",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=directory_checkpoint,
                    snapshot=None,
                )
            ),
        )
        package = mocker.patch(
            "gyomu_workflow.snapshot.run.run_package_action",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=package_checkpoint,
                    snapshot=None,
                )
            ),
        )
        readme = mocker.patch(
            "gyomu_workflow.snapshot.run.run_readme_action",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=readme_checkpoint,
                    snapshot=None,
                )
            ),
        )
        llm_context = mocker.patch(
            "gyomu_workflow.snapshot.run.run_llm_context_action",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=llm_checkpoint,
                    snapshot=None,
                )
            ),
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Success)

        directory.assert_awaited_once_with(
            request=request,
            current_checkpoint=checkpoint,
            option=concept_option,
            target=snapshot_target,
        )
        package.assert_awaited_once_with(
            request=request,
            current_checkpoint=directory_checkpoint,
            option=concept_option,
            target=snapshot_target,
        )
        readme.assert_awaited_once_with(
            request=request,
            current_checkpoint=package_checkpoint,
            option=concept_option,
            target=snapshot_target,
        )
        llm_context.assert_awaited_once_with(
            request=request,
            current_checkpoint=readme_checkpoint,
            option=concept_option,
            target=snapshot_target,
        )

    async def test_uses_analysis_snapshot_for_post_actions(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
        concept_option,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=True,
            project_context=False,
            unit_test=False,
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.build_concept_update_option",
            return_value=concept_option,
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=snapshot_target.snapshot,
                )
            ),
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == analysis.current_snapshot

    async def test_returns_latest_action_snapshot(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
        concept_option,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=False,
            project_context=True,
            unit_test=False,
        )

        directory_snapshot = create_project_snapshot(
            project_root=WorkspaceRelativePath(Path("projects/directory")),
        )
        package_snapshot = create_project_snapshot(
            project_root=WorkspaceRelativePath(Path("projects/package")),
        )
        readme_snapshot = create_project_snapshot(
            project_root=WorkspaceRelativePath(Path("projects/readme")),
        )
        llm_snapshot = create_project_snapshot(
            project_root=WorkspaceRelativePath(Path("projects/llm_context")),
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.build_concept_update_option",
            return_value=concept_option,
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=None,
                )
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_directory_action",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=directory_snapshot,
                )
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_package_action",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=package_snapshot,
                )
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_readme_action",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=readme_snapshot,
                )
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_llm_context_action",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=llm_snapshot,
                )
            ),
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == llm_snapshot

    async def test_preserves_snapshot_when_action_returns_none(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=False,
            project_context=False,
            unit_test=False,
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(
                    checkpoint=checkpoint,
                    snapshot=None,
                )
            ),
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == snapshot_target.snapshot


class TestRunActions_Failure:
    async def test_returns_failure_when_directory_action_fails(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
        concept_option,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=False,
            project_context=True,
            unit_test=False,
        )
        error = GyomuError(
            message="directory action failed",
            domain="snapshot",
            operation="run_directory_action",
            reason="external_failure",
            context="test",
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.build_concept_update_option",
            return_value=concept_option,
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(checkpoint=checkpoint, snapshot=None)
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_directory_action",
            return_value=Failure(error),
        )
        run_package_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_package_action",
        )
        run_readme_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_readme_action",
        )
        run_llm_context_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_llm_context_action",
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

        run_package_action.assert_not_called()
        run_readme_action.assert_not_called()
        run_llm_context_action.assert_not_called()

    async def test_returns_failure_when_package_action_fails(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
        concept_option,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=False,
            project_context=True,
            unit_test=False,
        )
        error = GyomuError(
            message="package action failed",
            domain="snapshot",
            operation="run_package_action",
            reason="external_failure",
            context="test",
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.build_concept_update_option",
            return_value=concept_option,
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(checkpoint=checkpoint, snapshot=None)
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_directory_action",
            return_value=Success(
                SnapshotActionResult(checkpoint=checkpoint, snapshot=None)
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_package_action",
            return_value=Failure(error),
        )
        run_readme_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_readme_action",
        )
        run_llm_context_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_llm_context_action",
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

        run_readme_action.assert_not_called()
        run_llm_context_action.assert_not_called()

    async def test_returns_failure_when_readme_action_fails(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
        concept_option,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=False,
            project_context=True,
            unit_test=False,
        )
        error = GyomuError(
            message="readme action failed",
            domain="snapshot",
            operation="run_readme_action",
            reason="external_failure",
            context="test",
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.build_concept_update_option",
            return_value=concept_option,
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(checkpoint=checkpoint, snapshot=None)
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_directory_action",
            return_value=Success(
                SnapshotActionResult(checkpoint=checkpoint, snapshot=None)
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_package_action",
            return_value=Success(
                SnapshotActionResult(checkpoint=checkpoint, snapshot=None)
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_readme_action",
            return_value=Failure(error),
        )
        run_llm_context_action = mocker.patch(
            "gyomu_workflow.snapshot.run.run_llm_context_action",
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

        run_llm_context_action.assert_not_called()

    async def test_returns_failure_when_llm_context_action_fails(
        self,
        mocker,
        snapshot_request,
        snapshot_target,
        analysis,
        checkpoint,
        concept_option,
    ):

        request = _request_with_actions(
            snapshot_request,
            docstring_enabled=False,
            project_context=True,
            unit_test=False,
        )
        error = GyomuError(
            message="LLM context action failed",
            domain="snapshot",
            operation="run_llm_context_action",
            reason="external_failure",
            context="test",
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run.load_checkpoint",
            return_value=Success(checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.build_concept_update_option",
            return_value=concept_option,
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_docstring_actions",
            return_value=Success(
                SnapshotActionResult(checkpoint=checkpoint, snapshot=None)
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_directory_action",
            return_value=Success(
                SnapshotActionResult(checkpoint=checkpoint, snapshot=None)
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_package_action",
            return_value=Success(
                SnapshotActionResult(checkpoint=checkpoint, snapshot=None)
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_readme_action",
            return_value=Success(
                SnapshotActionResult(checkpoint=checkpoint, snapshot=None)
            ),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run.run_llm_context_action",
            return_value=Failure(error),
        )

        result = await run_actions(
            request=request,
            target=snapshot_target,
            analysis=analysis,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
