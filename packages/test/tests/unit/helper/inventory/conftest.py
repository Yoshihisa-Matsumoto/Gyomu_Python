import pytest
from gyomu_python_analysis.analysis.workspace import initialize_workspace_context
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRoot,
    WorkspaceRootKind,
)
from returns.result import Success

from packages.test.test_support.helpers import MONOREPO_FIXTURES_ROOT


@pytest.fixture
def workspace_context() -> WorkspaceContext:
    result = initialize_workspace_context(
        root=WorkspaceRoot(
            path=MONOREPO_FIXTURES_ROOT,
            kind=WorkspaceRootKind.UV_WORKSPACE,
        )
    )
    assert isinstance(result, Success)
    return result.unwrap()
