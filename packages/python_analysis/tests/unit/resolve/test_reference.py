from pathlib import Path

import pytest
from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.analysis.workspace import initialize_workspace_context
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRoot,
    WorkspaceRootKind,
)
from gyomu_python_analysis.resolve.models import ResolvedReference
from gyomu_python_analysis.resolve.reference import resolve_reference
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.import_analysis import ImportKind
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath, SymbolId
from returns.result import Success

from packages.python_analysis.test_support.helpers import MONOREPO_FIXTURES_ROOT


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


@pytest.fixture
def consumer_context(
    workspace_context: WorkspaceContext,
) -> FileAnalysisContext:
    target_project = next(
        (
            project
            for project in workspace_context.projects
            if project.config.name == "project-b"
        ),
        None,
    )
    assert target_project is not None

    project_context = initialize_project_from_workspace(
        workspace_context.path,
        target_project,
    )
    consumer_result = load_file_analysis_context(
        project_context,
        ProjectRelativePath(Path("src/project_b/reference_resolution/consumers.py")),
        option=AnalysisOption(no_check_cache=True),
    )
    assert isinstance(consumer_result, Success)

    return consumer_result.unwrap()


class TestResolveReference:
    def test_local_reference(
        self,
        consumer_context: FileAnalysisContext,
    ) -> None:

        target_reference: ResolvedReference | None = None

        target_reference = resolve_reference(
            reference_name="LocalConsumer", module=consumer_context.analysis
        )
        assert target_reference is not None
        assert target_reference.import_analysis is None
        assert target_reference.module_path == consumer_context.analysis.module_name
        assert target_reference.symbol_id == SymbolId(
            "project_b.reference_resolution.consumers::LocalConsumer"
        )

    def test_LM(
        self,
        consumer_context: FileAnalysisContext,
    ) -> None:

        target_reference = resolve_reference(
            reference_name="LM", module=consumer_context.analysis
        )
        assert target_reference is not None
        assert target_reference.import_analysis is not None
        assert target_reference.import_analysis.kind == ImportKind.SYMBOL
        assert (
            target_reference.import_analysis.imported_name
            == "project_b.reference_resolution.models.LocalModel"
        )
        assert target_reference.module_path == PythonPath(
            "project_b.reference_resolution.models"
        )
        assert target_reference.symbol_id == SymbolId(
            "project_b.reference_resolution.models::LocalModel"
        )

    def test_Base_BaseModel(
        self,
        consumer_context: FileAnalysisContext,
    ) -> None:
        # Base.BaseModel
        target_reference = resolve_reference(
            reference_name="Base.BaseModel", module=consumer_context.analysis
        )
        assert target_reference is not None
        assert target_reference.import_analysis is not None
        assert target_reference.import_analysis.kind == ImportKind.MODULE
        assert target_reference.import_analysis.imported_name == "pydantic"
        assert target_reference.module_path == PythonPath("pydantic")
        assert target_reference.symbol_id == SymbolId("pydantic::BaseModel")

    def test_not_found(self, consumer_context: FileAnalysisContext) -> None:

        # Unexpected
        target_reference = resolve_reference(
            reference_name="NotFound.InvalidSybol", module=consumer_context.analysis
        )
        assert target_reference is None

    def test_resolves_dotted_module_import(
        self,
        consumer_context: FileAnalysisContext,
    ) -> None:
        # Base.BaseModel
        reference = resolve_reference(
            reference_name="project_b.reference_resolution.models.LocalModel",
            module=consumer_context.analysis,
        )
        print(consumer_context.analysis.imports)
        assert reference is not None
        assert reference.import_analysis is not None
        assert reference.import_analysis.kind == ImportKind.MODULE
        assert reference.import_analysis.local_name == "project_b"
        assert (
            reference.import_analysis.imported_name
            == "project_b.reference_resolution.models"
        )
        assert reference.module_path == PythonPath(
            "project_b.reference_resolution.models"
        )
        assert reference.symbol_id == SymbolId(
            "project_b.reference_resolution.models::LocalModel"
        )
