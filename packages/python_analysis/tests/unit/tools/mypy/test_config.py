from pathlib import Path

import pytest
from gyomu_python_analysis.analysis.workspace import find_root
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.mypy.config import (
    _gather_workspace_projects_src_path,
    _get_workspace_mypy_test_ini,
    _get_workspace_pyproject_toml,
    for_file,
    for_project,
    for_workspace,
)
from gyomu_python_analysis.tools.mypy.models import (
    MypyCheckConfig,
    MypyTarget,
)
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from pytest_mock import MockerFixture
from returns.result import Success

from packages.python_analysis.test_support.helpers import MONOREPO_FIXTURES_ROOT


@pytest.fixture
def workspace_context() -> WorkspaceContext:
    result = find_root(MONOREPO_FIXTURES_ROOT)
    assert isinstance(result, Success)
    return result.unwrap()


class Test_GatherWorkspaceProjectsSrcPath:
    def test_without_dependencies(
        self,
        workspace_context,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-a")
        assert target_project_context is not None

        actual = _gather_workspace_projects_src_path(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        expected = (
            target_project_context.project_root / target_project_context.source_root,
        )

        assert actual == expected

    def test_with_direct_dependency(
        self,
        workspace_context: WorkspaceContext,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        dependency_context = workspace_context.get_project_context("project-a")

        assert target_project_context is not None
        assert dependency_context is not None

        actual = _gather_workspace_projects_src_path(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        expected = (
            target_project_context.project_root / target_project_context.source_root,
            dependency_context.project_root / dependency_context.source_root,
        )

        assert actual == expected


class TestForFile:
    def test_returns_expected_config(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        workspace_relative_file_path = WorkspaceRelativePath(
            Path("packages/project_b/test_support/example.py")
        )
        expected_mypy_path = (
            target_project_context.project_root / target_project_context.source_root,
        )

        gather_mock = mocker.patch(
            "gyomu_python_analysis.tools.mypy.config."
            "_gather_workspace_projects_src_path",
            return_value=expected_mypy_path,
        )
        actual = for_file(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )
        gather_mock.assert_called_once_with(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        expected = MypyCheckConfig(
            targets=(workspace_relative_file_path,),
            config_file=_get_workspace_pyproject_toml(
                workspace_context=workspace_context
            ),
            cache_dir=None,
            explicit_package_bases=True,
            working_directory=workspace_context.root_project_context.project_root,
            mypy_path=expected_mypy_path,
        )

        assert actual == expected
        gather_mock.assert_called_once_with(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )


class TestForProject:
    def test_source_returns_expected_config(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        gather_mock = mocker.patch(
            "gyomu_python_analysis.tools.mypy.config."
            "_gather_workspace_projects_src_path",
        )

        actual = for_project(
            target=MypyTarget.SOURCE,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        expected = MypyCheckConfig(
            targets=(
                target_project_context.project_root
                / target_project_context.source_root,
            ),
            config_file=_get_workspace_pyproject_toml(
                workspace_context=workspace_context
            ),
            cache_dir=(
                target_project_context.project_root
                / ".mypy_cache"
                / str(MypyTarget.SOURCE)
            ),
            explicit_package_bases=False,
            working_directory=workspace_context.root_project_context.project_root,
            mypy_path=None,
        )

        assert actual == expected
        gather_mock.assert_not_called()

    def test_test_support_returns_expected_config(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        expected_mypy_path = (
            target_project_context.project_root / target_project_context.source_root,
        )
        gather_mock = mocker.patch(
            "gyomu_python_analysis.tools.mypy.config."
            "_gather_workspace_projects_src_path",
            return_value=expected_mypy_path,
        )

        actual = for_project(
            target=MypyTarget.TEST_SUPPORT,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        expected = MypyCheckConfig(
            targets=(
                target_project_context.project_root / "test_support" / "helpers.py",
            ),
            config_file=_get_workspace_pyproject_toml(
                workspace_context=workspace_context
            ),
            cache_dir=(
                target_project_context.project_root
                / ".mypy_cache"
                / str(MypyTarget.TEST_SUPPORT)
            ),
            explicit_package_bases=True,
            working_directory=workspace_context.root_project_context.project_root,
            mypy_path=expected_mypy_path,
        )

        assert actual == expected
        gather_mock.assert_called_once_with(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

    def test_tests_returns_expected_config(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        expected_mypy_path = (
            target_project_context.project_root / target_project_context.source_root,
        )
        gather_mock = mocker.patch(
            "gyomu_python_analysis.tools.mypy.config."
            "_gather_workspace_projects_src_path",
            return_value=expected_mypy_path,
        )

        actual = for_project(
            target=MypyTarget.TESTS,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        expected = MypyCheckConfig(
            targets=(target_project_context.project_root / "tests",),
            config_file=_get_workspace_mypy_test_ini(
                workspace_context=workspace_context
            ),
            cache_dir=(
                target_project_context.project_root
                / ".mypy_cache"
                / str(MypyTarget.TESTS)
            ),
            explicit_package_bases=True,
            working_directory=workspace_context.root_project_context.project_root,
            mypy_path=expected_mypy_path,
        )

        assert actual == expected
        gather_mock.assert_called_once_with(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )


class TestForWorkspace:
    def test_source(
        self,
        workspace_context: WorkspaceContext,
    ) -> None:
        result = for_workspace(
            workspace_context=workspace_context,
            target=MypyTarget.SOURCE,
        )

        workspace_root = workspace_context.workspace_root.path
        expected_targets = tuple(
            sorted(
                project_context.project_root / project_context.source_root
                for project in workspace_context.projects
                if (
                    project_context := workspace_context.get_project_context(
                        project.config.name
                    )
                )
                is not None
            )
        )

        assert result.targets == expected_targets
        assert result.config_file == _get_workspace_pyproject_toml(
            workspace_context=workspace_context
        )
        assert result.cache_dir == workspace_root / ".mypy_cache" / "src"
        assert result.explicit_package_bases is False
        assert result.working_directory == workspace_root
        assert result.mypy_path is None

    def test_test_support(
        self,
        workspace_context: WorkspaceContext,
    ) -> None:
        result = for_workspace(
            workspace_context=workspace_context,
            target=MypyTarget.TEST_SUPPORT,
        )

        workspace_root = workspace_context.workspace_root.path
        expected_targets = tuple(
            sorted(
                file
                for project in workspace_context.projects
                if (
                    project_context := workspace_context.get_project_context(
                        project.config.name
                    )
                )
                is not None
                for support_dir in (project_context.project_root / "test_support",)
                if support_dir.exists() and support_dir.is_dir()
                for file in support_dir.glob("*.py")
                if file.is_file()
            )
        )

        assert result.targets == expected_targets
        assert result.config_file == _get_workspace_pyproject_toml(
            workspace_context=workspace_context
        )
        assert result.cache_dir == workspace_root / ".mypy_cache" / "test_support"
        assert result.explicit_package_bases is True
        assert result.working_directory == workspace_root
        assert result.mypy_path == (workspace_root,)

    def test_tests(
        self,
        workspace_context: WorkspaceContext,
    ) -> None:
        result = for_workspace(
            workspace_context=workspace_context,
            target=MypyTarget.TESTS,
        )

        workspace_root = workspace_context.workspace_root.path
        expected_targets = tuple(
            sorted(
                test_dir
                for project in workspace_context.projects
                if (
                    project_context := workspace_context.get_project_context(
                        project.config.name
                    )
                )
                is not None
                for test_dir in (project_context.project_root / "tests",)
                if test_dir.exists()
            )
        )

        assert result.targets == expected_targets
        assert result.config_file == _get_workspace_mypy_test_ini(
            workspace_context=workspace_context
        )
        assert result.cache_dir == workspace_root / ".mypy_cache" / "tests"
        assert result.explicit_package_bases is True
        assert result.working_directory == workspace_root
        assert result.mypy_path == (workspace_root,)
