from pathlib import Path

import pytest
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.analysis.workspace import find_root
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.mypy.check import (
    check_project,
    check_workspace,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.utility.fromatting import format_object
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    MONOREPO_FIXTURES_ROOT,
)


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


pytestmark = pytest.mark.integration


@pytest.mark.integration
def test_check_project(
    workspace_context: WorkspaceContext,
    root_project_context: ProjectContext,
) -> None:
    target_project_context = workspace_context.get_project_context("project-b")
    assert target_project_context is not None

    actual = check_project(
        target_project_context=target_project_context,
        workspace_root_project_context=root_project_context,
        workspace_context=workspace_context,
    )
    if isinstance(actual, Failure):
        print(format_object(actual.failure(), depth=8))
    assert isinstance(actual, Success)

    print(format_object(actual.unwrap(), depth=5))


@pytest.mark.integration
def test_check_workspace(workspace_context) -> None:
    actual = check_workspace(
        workspace_context=workspace_context,
    )
    if isinstance(actual, Failure):
        print(format_object(actual.failure(), depth=8))
    assert isinstance(actual, Success)

    print(format_object(actual.unwrap(), depth=5))
