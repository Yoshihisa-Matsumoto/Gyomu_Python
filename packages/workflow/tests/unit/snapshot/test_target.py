from pathlib import Path
from unittest.mock import MagicMock

from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.snapshot.models import (
    ProjectSnapshot,
)
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.models import FileFilter, SnapshotTargetOption
from gyomu_workflow.snapshot.target import (
    filter_included_files,
    resolve_snapshot_target,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.python_analysis_test_support.helpers import (
    create_analyze_project_change,
    create_file_added,
    create_file_deleted,
    create_file_updated,
    create_test_file_snapshot,
)


class TestFilterIncludedFiles:
    def test_filter_included_files(self) -> None:
        included_files = frozenset(
            {
                ProjectRelativePath(Path("foo.py")),
                ProjectRelativePath(Path("bar.py")),
                ProjectRelativePath(Path("sub/baz.py")),
            }
        )

        result = filter_included_files(included_files, "*.py")

        assert result == included_files

    def test_filter_included_files_returns_matching_files(self) -> None:
        included_files = frozenset(
            {
                ProjectRelativePath(Path("foo.py")),
                ProjectRelativePath(Path("foo.txt")),
                ProjectRelativePath(Path("sub/bar.py")),
            }
        )

        result = filter_included_files(included_files, "foo.py")

        assert result == frozenset(
            {
                ProjectRelativePath(Path("foo.py")),
            }
        )

    def test_filter_included_files_returns_empty_when_no_match(self) -> None:
        included_files = frozenset(
            {
                ProjectRelativePath(Path("foo.py")),
                ProjectRelativePath(Path("bar.py")),
            }
        )

        result = filter_included_files(included_files, "missing.py")

        assert result == frozenset()

    def test_file_match(self) -> None:
        included_files = frozenset(
            {
                ProjectRelativePath(
                    Path("src/gyomu_schema/schemas/python/import_analysis.py")
                ),
                ProjectRelativePath(
                    Path("src/gyomu_schema/gyomu/holiday/business_calendar.py")
                ),
            }
        )
        result = filter_included_files(
            included_files, "gyomu/holiday/business_calendar.py"
        )
        assert result == frozenset(
            {
                ProjectRelativePath(
                    Path("src/gyomu_schema/gyomu/holiday/business_calendar.py")
                ),
            }
        )


class TestResolveSnapshotTarget:
    def test_resolve_snapshot_target_from_diff(
        self,
        mocker: MockerFixture,
    ) -> None:
        diff = (
            create_file_added(
                current=create_test_file_snapshot(
                    project_relative_path=ProjectRelativePath(Path("foo.py"))
                )
            ),
            create_file_updated(
                current=create_test_file_snapshot(
                    project_relative_path=ProjectRelativePath(Path("bar.py"))
                ),
                previous=create_test_file_snapshot(
                    project_relative_path=ProjectRelativePath(Path("bar.py"))
                ),
            ),
            create_file_deleted(
                previous=create_test_file_snapshot(
                    project_relative_path=ProjectRelativePath(Path("par.py"))
                ),
            ),
        )
        current_snapshot = ProjectSnapshot(
            project_root=WorkspaceRelativePath(Path("/tmp")), files=tuple()
        )
        analyze_project_changes = mocker.patch(
            "gyomu_workflow.snapshot.target.analyze_project_changes",
            return_value=Success(
                create_analyze_project_change(
                    diff=diff,
                    project_id="test",
                    snapshot_path=FullPath(Path("/tmp")),
                    current_snapshot=current_snapshot,
                    previous_snapshot=ProjectSnapshot(
                        project_root=WorkspaceRelativePath(Path("/tmp")), files=tuple()
                    ),
                )
            ),
        )
        repository_root_path = MagicMock()
        project_context = MagicMock()

        option = SnapshotTargetOption()

        result = resolve_snapshot_target(
            repository_root_path=repository_root_path,
            project_context=project_context,
            option=option,
        )

        assert isinstance(result, Success)

        target = result.unwrap()

        assert target.files == frozenset(
            {
                diff[0].project_relative_path,
                diff[1].project_relative_path,
            }
        )
        assert target.deleted_files == frozenset(
            {
                diff[2].project_relative_path,
            }
        )
        assert target.snapshot == current_snapshot

        analyze_project_changes.assert_called_once_with(
            repository_root_path=repository_root_path,
            project_context=project_context,
            include_all=False,
        )

    def test_resolve_snapshot_target_with_all(
        self,
        mocker: MockerFixture,
    ) -> None:
        analyze_project_changes = mocker.patch(
            "gyomu_workflow.snapshot.target.analyze_project_changes",
            return_value=Success(
                create_analyze_project_change(
                    diff=(
                        create_file_added(
                            current=create_test_file_snapshot(
                                project_relative_path=ProjectRelativePath(
                                    Path("foo.py")
                                )
                            )
                        ),
                        create_file_updated(
                            current=create_test_file_snapshot(
                                project_relative_path=ProjectRelativePath(
                                    Path("bar.py")
                                )
                            ),
                            previous=create_test_file_snapshot(
                                project_relative_path=ProjectRelativePath(
                                    Path("bar.py")
                                )
                            ),
                        ),
                    ),
                    current_snapshot=ProjectSnapshot(
                        project_root=WorkspaceRelativePath(Path("/tmp")), files=tuple()
                    ),
                )
            ),
        )

        project_context = MagicMock()
        option = SnapshotTargetOption(all=True)
        repository_root_path = FullPath(Path("/tmp"))
        result = resolve_snapshot_target(
            repository_root_path=repository_root_path,
            project_context=project_context,
            option=option,
        )

        assert isinstance(result, Success)

        analyze_project_changes.assert_called_once_with(
            repository_root_path=repository_root_path,
            project_context=project_context,
            include_all=True,
        )

    def test_resolve_snapshot_target_with_file_filter(self, mocker) -> None:
        included_files = frozenset(
            {
                ProjectRelativePath(Path("foo.py")),
                ProjectRelativePath(Path("bar.py")),
                ProjectRelativePath(Path("foo.txt")),
            }
        )

        current_snapshot = ProjectSnapshot(
            project_root=WorkspaceRelativePath(Path("/tmp")), files=tuple()
        )
        mocker.patch(
            "gyomu_workflow.snapshot.target.analyze_project_changes",
            return_value=Success(
                create_analyze_project_change(
                    diff=(
                        create_file_added(
                            current=create_test_file_snapshot(
                                project_relative_path=ProjectRelativePath(
                                    Path("foo.py")
                                )
                            )
                        ),
                        create_file_updated(
                            current=create_test_file_snapshot(
                                project_relative_path=ProjectRelativePath(
                                    Path("bar.py")
                                )
                            ),
                            previous=create_test_file_snapshot(
                                project_relative_path=ProjectRelativePath(
                                    Path("bar.py")
                                )
                            ),
                        ),
                    ),
                    project_id="test",
                    snapshot_path=FullPath(Path("/tmp")),
                    current_snapshot=current_snapshot,
                    previous_snapshot=ProjectSnapshot(
                        project_root=WorkspaceRelativePath(Path("/tmp")), files=tuple()
                    ),
                )
            ),
        )

        project_context = MagicMock()
        project_context.included_files = included_files

        option = SnapshotTargetOption(
            file_filter=FileFilter(pattern="foo.py"),
        )

        result = resolve_snapshot_target(
            repository_root_path=MagicMock(),
            project_context=project_context,
            option=option,
        )

        assert isinstance(result, Success)

        target = result.unwrap()

        assert target.files == frozenset(
            {
                ProjectRelativePath(Path("foo.py")),
            }
        )
        assert target.deleted_files == frozenset()
        assert target.snapshot == current_snapshot

    # def test_resolve_snapshot_target_with_file_filter_does_not_analyze_snapshot(
    #     self,
    #     mocker,
    # ) -> None:
    #     mocker.patch(
    #         "gyomu_workflow.snapshot.target.analyze_project_changes",
    #     )

    #     project_context = MagicMock()
    #     project_context.included_files = frozenset(
    #         {
    #             ProjectRelativePath(Path("foo.py")),
    #         }
    #     )

    #     option = SnapshotTargetOption(
    #         file_filter=FileFilter(pattern="foo.py"),
    #     )

    #     result = resolve_snapshot_target(
    #         repository_root_path=MagicMock(),
    #         project_context=project_context,
    #         option=option,
    #     )

    #     assert isinstance(result, Success)

    def test_resolve_snapshot_target_wraps_analysis_error(self, mocker) -> None:
        analysis_error = AnalysisError(
            message="test",
            context="analysis",
            file_path=FullPath(Path("/tmp")),
            phase="snapshot",
        )

        mocker.patch(
            "gyomu_workflow.snapshot.target.analyze_project_changes",
            return_value=Failure(analysis_error),
        )

        project_context = MagicMock()
        project_context.included_files = frozenset(
            {
                ProjectRelativePath(Path("foo.py")),
            }
        )
        result = resolve_snapshot_target(
            repository_root_path=MagicMock(),
            project_context=project_context,
            option=SnapshotTargetOption(),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, GyomuError)
        assert error.domain == "snapshot"
        assert error.operation == "resolve_snapshot_target"
        assert error.reason == "external_failure"
        assert error.context == "gyomu_workflow.snapshot.target.resolve_snapshot_target"
        assert error.__cause__ == analysis_error
