from pathlib import Path

import pytest
from gyomu_python_analysis.project.context import ProjectContext, PyProjectConfig
from gyomu_python_analysis.project.workspace import WorkspaceProject
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.option.update import UpdateOption
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.snapshot.types import ProjectSnapshot
from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.checkpoint import Checkpoint
from gyomu_workflow.snapshot.models import (
    DocstringExecutionOption,
    SnapshotActionOption,
    SnapshotExecutionOption,
    SnapshotRequest,
    SnapshotTarget,
    SnapshotTargetOption,
)
from gyomu_workflow.snapshot.run import build_docstring_update_option

from packages.python_analysis.python_analysis_test_support.helpers import (
    _create_context,
    create_project_snapshot,
)


@pytest.fixture
def update_option() -> UpdateOption:
    return build_docstring_update_option(None)


@pytest.fixture
def concept_option() -> ConceptOption:
    return ConceptOption()


@pytest.fixture
def project_context() -> ProjectContext:
    return _create_context()


@pytest.fixture
def snapshot_target(current_snapshot) -> SnapshotTarget:
    return SnapshotTarget(
        files=frozenset(), deleted_files=frozenset(), snapshot=current_snapshot
    )


@pytest.fixture
def checkpoint() -> Checkpoint:
    return Checkpoint(package="test", completed_steps=tuple())


@pytest.fixture
def current_snapshot() -> ProjectSnapshot:
    return create_project_snapshot()


@pytest.fixture
def snapshot_request(project_context: ProjectContext) -> SnapshotRequest:
    return SnapshotRequest(
        repository_root_path=FullPath(Path("/tmp")),
        project_context=project_context,
        option=SnapshotExecutionOption(
            commit=True,
            action=SnapshotActionOption(
                docstring=DocstringExecutionOption(enabled=True),
            ),
            target=SnapshotTargetOption(),
        ),
        project=WorkspaceProject(
            path=WorkspaceRelativePath(Path("/tmp")),
            config=PyProjectConfig(
                path=WorkspaceRelativePath(Path(".")),
                name="test",
                version="0.1",
                description=None,
                formatter_line_length=88,
                _toml_data={},
            ),
        ),
    )
