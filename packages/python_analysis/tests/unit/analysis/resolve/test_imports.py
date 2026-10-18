from pathlib import Path
from typing import cast
from unittest.mock import Mock

import pytest
from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.analysis.load_file_context import (
    load_file_analysis_context,
)
from gyomu_python_analysis.analysis.query import find_import_by_local_name
from gyomu_python_analysis.analysis.resolve.imports import (
    resolve_import_file_analysis_context,
    resolve_import_symbol,
    resolve_imported_symbol,
)
from gyomu_python_analysis.analysis.workspace import initialize_workspace_context
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext, PyProjectConfig
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRoot,
    WorkspaceRootKind,
)
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    ProjectRelativePath,
    SymbolId,
    WorkspaceRelativePath,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis
from returns.result import Failure, Success

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
def project_b_file_context() -> FileAnalysisContext:
    config = PyProjectConfig(
        path=WorkspaceRelativePath(Path(".")),
        name="project-b",
        version="0.1",
        description=None,
        formatter_line_length=88,
        _toml_data={},
    )
    project_context = ProjectContext(
        project_root=MONOREPO_FIXTURES_ROOT / "packages" / "project_b",
        source_root=ProjectRelativePath(Path("src")),
        config=config,
    )
    result = load_file_analysis_context(
        project_context,
        ProjectRelativePath(Path("src/project_b/pydantic_models/models.py")),
    )
    assert isinstance(result, Success)
    return result.unwrap()


def make_user_model_import() -> ImportAnalysis:
    return ImportAnalysis(
        local_name="UserModel",
        imported_name="project_b.pydantic_models.models.UserModel",
        kind=ImportKind.SYMBOL,
    )


class TestResolveImportFileAnalysisContext:
    def test_empty_module_path_returns_none(self) -> None:
        workspace = Mock(spec=WorkspaceContext)
        target_import = ImportAnalysis(
            local_name="BaseModel",
            imported_name="BaseModel",
            kind=ImportKind.SYMBOL,
        )

        result = resolve_import_file_analysis_context(
            target_import=target_import,
            workspace=workspace,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None
        workspace.find_file_analysis_context.assert_not_called()

    def test_resolves_existing_module(
        self, workspace_context: WorkspaceContext
    ) -> None:
        target_import = ImportAnalysis(
            local_name="models",
            imported_name="project_b.pydantic_models.models",
            kind=ImportKind.MODULE,
        )

        result = resolve_import_file_analysis_context(
            target_import=target_import,
            workspace=workspace_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is not None

    def test_propagates_failure(self) -> None:
        workspace = Mock(spec=WorkspaceContext)
        error = cast(AnalysisError, Mock(spec=AnalysisError))
        workspace.find_file_analysis_context.return_value = Failure(error)
        target_import = ImportAnalysis(
            local_name="models",
            imported_name="project_b.pydantic_models.models",
            kind=ImportKind.MODULE,
        )

        result = resolve_import_file_analysis_context(
            target_import=target_import,
            workspace=workspace,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error


class TestResolveImportedSymbol:
    def test_symbol_id_is_none_returns_none(
        self, project_b_file_context: FileAnalysisContext
    ) -> None:
        target_import = ImportAnalysis(
            local_name="models",
            imported_name="project_b.pydantic_models.models",
            kind=ImportKind.MODULE,
        )

        result = resolve_imported_symbol(
            target_import=target_import,
            file_analysis_context=project_b_file_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

    def test_resolves_existing_symbol(
        self, project_b_file_context: FileAnalysisContext
    ) -> None:
        target_import = make_user_model_import()

        result = resolve_imported_symbol(
            target_import=target_import,
            file_analysis_context=project_b_file_context,
        )

        assert isinstance(result, Success)
        symbol = result.unwrap()
        assert symbol is not None
        assert isinstance(
            symbol,
            type(
                project_b_file_context.metadata.symbols[
                    DeclarationIdentity(
                        symbol_id=SymbolId(
                            "project_b.pydantic_models.models::UserModel"
                        ),
                        declaration_id=DeclarationId("."),
                    )
                ]
            ),
        )
        assert isinstance(symbol, ClassAnalysis)

    def test_missing_symbol_returns_none(
        self, project_b_file_context: FileAnalysisContext
    ) -> None:
        target_import = ImportAnalysis(
            local_name="MissingModel",
            imported_name="project_b.pydantic_models.models.MissingModel",
            kind=ImportKind.SYMBOL,
        )

        result = resolve_imported_symbol(
            target_import=target_import,
            file_analysis_context=project_b_file_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None


class TestResolveImportSymbol:
    def test_resolves_symbol_through_workspace(
        self, workspace_context: WorkspaceContext
    ) -> None:
        target_import = make_user_model_import()

        result = resolve_import_symbol(
            target_import=target_import,
            workspace=workspace_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is not None

    def test_missing_module_returns_none(
        self, workspace_context: WorkspaceContext
    ) -> None:
        target_import = ImportAnalysis(
            local_name="MissingModel",
            imported_name="project_b.nonexistent.models.MissingModel",
            kind=ImportKind.SYMBOL,
        )

        result = resolve_import_symbol(
            target_import=target_import,
            workspace=workspace_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

    def test_propagates_failure(self) -> None:
        workspace = Mock(spec=WorkspaceContext)
        error = cast(AnalysisError, Mock(spec=AnalysisError))
        workspace.find_file_analysis_context.return_value = Failure(error)
        target_import = make_user_model_import()

        result = resolve_import_symbol(
            target_import=target_import,
            workspace=workspace,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error


class TestResolveImportedSymbolTypes:
    @pytest.mark.parametrize(
        ("local_name", "expected_type"),
        [
            ("IMPORT_TEST_VALUE", VariableAnalysis),
            ("ImportTestClass", ClassAnalysis),
            ("import_test_function", FunctionAnalysis),
            ("ImportTestAlias", TypeAliasAnalysis),
        ],
    )
    def test_resolves_imported_symbol_type(
        self,
        local_name: str,
        expected_type: type[SymbolAnalysis],
        workspace_context: WorkspaceContext,
    ) -> None:
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
            ProjectRelativePath(Path("src/project_b/import_models/consumers.py")),
        )
        assert isinstance(consumer_result, Success)

        consumer_context = consumer_result.unwrap()
        target_import = find_import_by_local_name(
            local_name,
            consumer_context.analysis,
        )
        assert target_import is not None

        file_result = resolve_import_file_analysis_context(
            target_import=target_import,
            workspace=workspace_context,
        )
        assert isinstance(file_result, Success)

        file_context = file_result.unwrap()
        assert file_context is not None

        symbol_result = resolve_imported_symbol(
            target_import=target_import,
            file_analysis_context=file_context,
        )
        assert isinstance(symbol_result, Success)

        symbol = symbol_result.unwrap()
        assert symbol is not None
        assert isinstance(symbol, expected_type)
