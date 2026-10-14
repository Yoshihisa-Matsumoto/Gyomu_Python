from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from gyomu_python_analysis.project.context import ProjectContext, PyProjectConfig
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.option.update import UpdateDebugInfoOption, UpdateOption
from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.checkpoint import PipelineStep, SnapshotActionResult
from gyomu_workflow.snapshot.run_docstring import (
    build_docstring_update_option,
    is_source_docstring_target,
    is_source_file,
    run_docstring_action,
    run_docstring_actions,
)
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    _create_context,
)
from packages.workflow.test_support.helper import (
    create_snapshot_target,
)


@pytest.fixture
def update_option() -> UpdateOption:
    return build_docstring_update_option(None)


@pytest.fixture
def source_project_relative_path() -> ProjectRelativePath:
    return ProjectRelativePath(Path("src/example.py"))


@pytest.fixture
def project_context() -> ProjectContext:
    return _create_context()


class TestRunDocstringAction:
    @pytest.mark.asyncio
    async def test_load_file_analysis_context_failure(
        self,
        mocker,
        project_context,
        source_project_relative_path,
        update_option,
    ):
        error = GyomuError(
            message="load failed",
            domain="test",
            operation="load",
            reason="invalid_input",
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.load_file_analysis_context",
            return_value=Failure(error),
        )
        process_docstring_update = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.process_docstring_update",
            new_callable=AsyncMock,
        )

        result = await run_docstring_action(
            project_context=project_context,
            source_project_relative_path=source_project_relative_path,
            option=update_option,
        )

        assert isinstance(result, Failure)

        wrapped_error = result.failure()

        assert wrapped_error.message == "fail to analyze source file"
        assert wrapped_error.domain == "snapshot"
        assert wrapped_error.operation == "run_docstring_action"
        assert wrapped_error.reason == "external_failure"
        assert wrapped_error.details == {
            "file_path": source_project_relative_path,
        }

        process_docstring_update.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_process_docstring_update_failure(
        self,
        mocker,
        project_context,
        source_project_relative_path,
        update_option,
    ):
        file_context = mocker.Mock()

        error = GyomuError(
            message="update failed",
            domain="test",
            operation="update",
            reason="invalid_input",
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.load_file_analysis_context",
            return_value=Success(file_context),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.process_docstring_update",
            new_callable=AsyncMock,
            return_value=Failure(error),
        )

        result = await run_docstring_action(
            project_context=project_context,
            source_project_relative_path=source_project_relative_path,
            option=update_option,
        )

        assert isinstance(result, Failure)

        wrapped_error = result.failure()

        assert wrapped_error.message == "fail to update docstring"
        assert wrapped_error.domain == "snapshot"
        assert wrapped_error.operation == "run_docstring_action"
        assert wrapped_error.reason == "external_failure"
        assert wrapped_error.details == {
            "file_path": source_project_relative_path,
        }

    @pytest.mark.asyncio
    async def test_success(
        self,
        mocker,
        project_context,
        source_project_relative_path,
        update_option,
    ):
        file_context = mocker.Mock()

        load_file_analysis_context = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.load_file_analysis_context",
            return_value=Success(file_context),
        )
        process_docstring_update = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.process_docstring_update",
            new_callable=AsyncMock,
            return_value=Success(None),
        )

        result = await run_docstring_action(
            project_context=project_context,
            source_project_relative_path=source_project_relative_path,
            option=update_option,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

        load_file_analysis_context.assert_called_once_with(
            context=project_context,
            file_path=source_project_relative_path,
            option=update_option,
        )

        process_docstring_update.assert_awaited_once_with(
            context=project_context,
            file_context=file_context,
            option=update_option,
        )

    async def test_run_docstring_action_skips_excluded_source(
        self,
        mocker,
        project_context: ProjectContext,
        source_project_relative_path: ProjectRelativePath,
        update_option: UpdateOption,
    ) -> None:
        mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.is_source_docstring_target",
            return_value=False,
        )
        process_docstring_update = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.process_docstring_update",
        )

        result = await run_docstring_action(
            project_context=project_context,
            source_project_relative_path=source_project_relative_path,
            option=update_option,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

        process_docstring_update.assert_not_awaited()


class TestIsSourceDocstringTarget:
    @pytest.mark.parametrize(
        ("exclude_path_list", "source_path", "expected"),
        [
            # exclude が未設定
            (
                None,
                "src/example.py",
                True,
            ),
            # ファイルを直接除外
            (
                ["src/example.py"],
                "src/example.py",
                False,
            ),
            # 除外対象ではないファイル
            (
                ["src/example.py"],
                "src/other.py",
                True,
            ),
            # ディレクトリ配下を除外
            (
                ["src/generated"],
                "src/generated/example.py",
                False,
            ),
            # 除外ディレクトリそのもの
            (
                ["src/generated"],
                "src/generated",
                False,
            ),
            # 除外ディレクトリと同名の別階層
            (
                ["src/generated"],
                "src/other/generated.py",
                True,
            ),
            # 複数の除外パスのうち1つに該当
            (
                ["src/generated", "tests/resources"],
                "tests/resources/example.py",
                False,
            ),
        ],
    )
    def test_is_source_docstring_target(
        self,
        exclude_path_list: list[str] | None,
        source_path: str,
        expected: bool,
    ) -> None:
        config = PyProjectConfig(
            path=WorkspaceRelativePath(Path("")),
            name="example",
            version="1.0.0",
            description=None,
            formatter_line_length=88,
            _toml_data={
                "tool": {
                    "gyomu": {
                        "exclude": exclude_path_list,
                    },
                },
            },
        )
        project_context = ProjectContext(
            project_root=FullPath(Path("/tmp")),
            source_root=ProjectRelativePath(Path("src")),
            config=config,
            included_files=frozenset(),
        )

        assert (
            is_source_docstring_target(
                project_context,
                ProjectRelativePath(Path(source_path)),
            )
            is expected
        )


class TestIsSourceFile:
    def test_returns_true_for_file_under_source_root(self) -> None:
        result = is_source_file(
            ProjectRelativePath(Path("src/package/module.py")),
            ProjectRelativePath(Path("src")),
        )

        assert result is True

    def test_returns_false_for_file_outside_source_root(self) -> None:
        result = is_source_file(
            ProjectRelativePath(Path("tests/test_module.py")),
            ProjectRelativePath(Path("src")),
        )

        assert result is False

    def test_returns_true_for_source_root_itself(self) -> None:
        result = is_source_file(
            ProjectRelativePath(Path("src")),
            ProjectRelativePath(Path("src")),
        )

        assert result is True

    def test_does_not_match_similar_directory_name(self) -> None:
        result = is_source_file(
            ProjectRelativePath(Path("src_other/module.py")),
            ProjectRelativePath(Path("src")),
        )

        assert result is False


class TestBuildDocstringUpdateOption:
    def test_builds_option_with_log_keyword(self) -> None:
        result = build_docstring_update_option("test-keyword")

        assert result == UpdateOption(
            debug_info=UpdateDebugInfoOption(
                dump_to_file=True,
                updated_symbol_docstring=True,
                file_update_plan=True,
                rendered_symbol_docstring=True,
                docstring_update_plan=True,
                docstring_update_context=True,
                keyword="test-keyword",
            ),
            no_check_cache=True,
        )

    def test_builds_option_without_log_keyword(self) -> None:
        result = build_docstring_update_option(None)

        assert result == UpdateOption(
            debug_info=UpdateDebugInfoOption(
                dump_to_file=True,
                updated_symbol_docstring=True,
                file_update_plan=True,
                rendered_symbol_docstring=True,
                docstring_update_plan=True,
                docstring_update_context=True,
                keyword=None,
            ),
            no_check_cache=True,
        )


class TestRunDocstringActions:
    async def test_skips_when_docstring_is_already_completed(
        self,
        mocker,
        snapshot_request,
        checkpoint,
    ) -> None:
        checkpoint.completed_steps = (PipelineStep.DOCSTRING,)
        target = create_snapshot_target()
        analyze_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.analyze_project_changes"
        )
        update_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.update_checkpoint"
        )

        result = await run_docstring_actions(
            current_checkpoint=checkpoint,
            request=snapshot_request,
            target=target,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == SnapshotActionResult(
            checkpoint=checkpoint,
            snapshot=None,
        )
        analyze_mock.assert_not_called()
        update_mock.assert_not_called()

    async def test_analyzes_project_and_updates_checkpoint(
        self,
        mocker,
        snapshot_request,
        checkpoint,
    ) -> None:
        checkpoint.completed_steps = ()

        snapshot = mocker.sentinel.snapshot
        updated_checkpoint = mocker.sentinel.updated_checkpoint

        analysis = SimpleNamespace(current_snapshot=snapshot)

        analyze_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.analyze_project_changes",
            return_value=Success(analysis),
        )
        update_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.update_checkpoint",
            return_value=Success(updated_checkpoint),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.delete_module_cache",
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.run_docstring_action",
        )
        target = create_snapshot_target()
        target.files = frozenset()
        target.deleted_files = frozenset()

        result = await run_docstring_actions(
            current_checkpoint=checkpoint,
            request=snapshot_request,
            target=target,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == SnapshotActionResult(
            checkpoint=updated_checkpoint,
            snapshot=snapshot,
        )

        analyze_mock.assert_called_once_with(
            repository_root_path=snapshot_request.repository_root_path,
            project_context=snapshot_request.project_context,
        )
        update_mock.assert_called_once_with(
            checkpoint=checkpoint,
            request=snapshot_request,
            status_to_add=PipelineStep.DOCSTRING,
            target=target,
        )

    async def test_deletes_cache_for_deleted_source_files(
        self,
        mocker,
        snapshot_request,
        checkpoint,
    ) -> None:
        checkpoint.completed_steps = ()
        target = create_snapshot_target()
        deleted_source = ProjectRelativePath(Path("src/package/deleted.py"))
        deleted_test = ProjectRelativePath(Path("tests/test_deleted.py"))
        target.files = frozenset()
        target.deleted_files = frozenset({deleted_source, deleted_test})

        mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.analyze_project_changes",
            return_value=Success(SimpleNamespace(current_snapshot=None)),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.update_checkpoint",
            return_value=Success(checkpoint),
        )
        delete_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.delete_module_cache",
            return_value=Success(None),
        )

        result = await run_docstring_actions(
            current_checkpoint=checkpoint,
            request=snapshot_request,
            target=target,
        )

        assert isinstance(result, Success)
        delete_mock.assert_called_once_with(
            snapshot_request.project_context,
            file_path=deleted_source,
        )

    async def test_returns_failure_when_deleting_module_cache_fails(
        self,
        mocker,
        snapshot_request,
        checkpoint,
    ) -> None:
        checkpoint.completed_steps = ()
        target = create_snapshot_target()
        deleted_source = ProjectRelativePath(Path("src/package/deleted.py"))
        target.files = frozenset()
        target.deleted_files = frozenset({deleted_source})

        error = GyomuError(
            message="fail to delete cache",
            domain="test",
            operation="test",
            reason="unexpected",
            context="test",
        )

        delete_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.delete_module_cache",
            return_value=Failure(error),
        )
        docstring_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.run_docstring_action",
        )
        analyze_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.analyze_project_changes",
        )
        update_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.update_checkpoint",
        )

        result = await run_docstring_actions(
            current_checkpoint=checkpoint,
            request=snapshot_request,
            target=target,
        )

        assert isinstance(result, Failure)
        assert result.failure().message == "fail to delete unnecessary module cache"
        delete_mock.assert_called_once()
        docstring_mock.assert_not_called()
        analyze_mock.assert_not_called()
        update_mock.assert_not_called()

    async def test_returns_failure_when_docstring_action_fails(
        self,
        mocker,
        snapshot_request,
        checkpoint,
    ) -> None:
        checkpoint.completed_steps = ()
        target = create_snapshot_target()
        source_file = ProjectRelativePath(Path("src/package/module.py"))
        target.files = frozenset({source_file})
        target.deleted_files = frozenset()

        error = GyomuError(
            message="fail to update docstring",
            domain="test",
            operation="test",
            reason="unexpected",
            context="test",
        )

        docstring_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.run_docstring_action",
            return_value=Failure(error),
        )
        analyze_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.analyze_project_changes",
        )
        update_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.update_checkpoint",
        )

        result = await run_docstring_actions(
            current_checkpoint=checkpoint,
            request=snapshot_request,
            target=target,
        )

        assert isinstance(result, Failure)
        assert result.failure() == error
        docstring_mock.assert_called_once()
        analyze_mock.assert_not_called()
        update_mock.assert_not_called()

    async def test_returns_failure_when_analyzing_project_changes_fails(
        self,
        mocker,
        snapshot_request,
        checkpoint,
    ) -> None:
        checkpoint.completed_steps = ()
        target = create_snapshot_target()
        target.files = frozenset()
        target.deleted_files = frozenset()

        error = GyomuError(
            message="fail to analyze project change",
            domain="test",
            operation="test",
            reason="unexpected",
            context="test",
        )

        analyze_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.analyze_project_changes",
            return_value=Failure(error),
        )
        update_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.update_checkpoint",
        )

        result = await run_docstring_actions(
            current_checkpoint=checkpoint,
            request=snapshot_request,
            target=target,
        )

        assert isinstance(result, Failure)
        assert result.failure().message == "fail to analyze project change"
        analyze_mock.assert_called_once()
        update_mock.assert_not_called()

    async def test_returns_failure_when_updating_checkpoint_fails(
        self,
        mocker,
        snapshot_request,
        checkpoint,
    ) -> None:
        checkpoint.completed_steps = ()
        target = create_snapshot_target()
        target.files = frozenset()
        target.deleted_files = frozenset()

        snapshot = mocker.sentinel.snapshot
        error = GyomuError(
            message="fail to update checkpoint",
            domain="test",
            operation="test",
            reason="unexpected",
            context="test",
        )

        mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.analyze_project_changes",
            return_value=Success(SimpleNamespace(current_snapshot=snapshot)),
        )
        update_mock = mocker.patch(
            "gyomu_workflow.snapshot.run_docstring.update_checkpoint",
            return_value=Failure(error),
        )

        result = await run_docstring_actions(
            current_checkpoint=checkpoint,
            request=snapshot_request,
            target=target,
        )

        assert isinstance(result, Failure)
        assert result.failure() == error
        update_mock.assert_called_once_with(
            checkpoint=checkpoint,
            request=snapshot_request,
            status_to_add=PipelineStep.DOCSTRING,
            target=target,
        )
