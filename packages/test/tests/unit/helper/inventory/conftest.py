import pytest
from gyomu_python_analysis.analysis.workspace import initialize_workspace_context
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRootKind,
)
from returns.result import Success

from packages.python_analysis.test_support.helpers import create_workspace_root
from packages.test.test_support.helpers import MONOREPO_FIXTURES_ROOT


@pytest.fixture
def workspace_context() -> WorkspaceContext:
    result = initialize_workspace_context(
        root=create_workspace_root(
            path=MONOREPO_FIXTURES_ROOT,
            kind=WorkspaceRootKind.UV_WORKSPACE,
        )
    )
    assert isinstance(result, Success)
    return result.unwrap()
