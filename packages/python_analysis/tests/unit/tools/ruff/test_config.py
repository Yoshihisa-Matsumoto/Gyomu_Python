from pathlib import Path

import pytest
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.analysis.workspace import find_root
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.ruff.config import for_file, for_project, for_workspace
from gyomu_python_analysis.tools.ruff.models import RuffCheckConfig
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Success

from packages.python_analysis.test_support.helpers import MONOREPO_FIXTURES_ROOT


@pytest.fixture
def workspace_context() -> WorkspaceContext:
    result = find_root(MONOREPO_FIXTURES_ROOT)
    assert isinstance(result, Success)
    return result.unwrap()


@pytest.fixture
def root_project_context(workspace_context: WorkspaceContext) -> ProjectContext:
    root_context_result = initialize_project_context(
        project_root=workspace_context.workspace_root.path,
        source_root=ProjectRelativePath(Path(".")),
    )
    assert isinstance(root_context_result, Success)
    return root_context_result.unwrap()


class TestForFile:
    def test_returns_expected_config(
        self,
        workspace_context: WorkspaceContext,
        root_project_context: ProjectContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None
        workspace_relative_file_path = ProjectRelativePath(
            Path("packages/project-a/src/example.py")
        )

        actual = for_file(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )

        expected = RuffCheckConfig(
            target=root_project_context.project_root / workspace_relative_file_path,
            working_directory=root_project_context.project_root,
        )

        assert actual == expected


class TestForProject:
    def test_returns_expected_config(
        self,
        workspace_context: WorkspaceContext,
        root_project_context: ProjectContext,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        actual = for_project(
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )

        expected = RuffCheckConfig(
            target=target_project_context.project_root,
            working_directory=root_project_context.project_root,
        )

        assert actual == expected


class TestForWorkspace:
    def test_returns_expected_config(
        self,
        workspace_context: WorkspaceContext,
        root_project_context: ProjectContext,
    ) -> None:
        actual = for_workspace(
            workspace_context=workspace_context,
        )

        expected = RuffCheckConfig(
            target=root_project_context.project_root,
            working_directory=root_project_context.project_root,
        )

        assert actual == expected
