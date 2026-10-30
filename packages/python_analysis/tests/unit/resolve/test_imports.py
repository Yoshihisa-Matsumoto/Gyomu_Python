from pathlib import Path
from unittest.mock import Mock

import pytest
from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.analysis.load_file_context import (
    load_file_analysis_context,
)
from gyomu_python_analysis.analysis.workspace import initialize_workspace_context
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.project.context import ProjectContext, PyProjectConfig
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRoot,
    WorkspaceRootKind,
)
from gyomu_python_analysis.resolve.imports import (
    resolve_reference_file_analysis_context,
    resolve_reference_symbol,
    resolve_referenced_symbol,
)
from gyomu_python_analysis.resolve.models import ResolvedReference
from gyomu_python_analysis.resolve.reference import resolve_reference
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    PythonPath,
    SymbolId,
    WorkspaceRelativePath,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    MONOREPO_FIXTURES_ROOT,
    create_analysis_error,
)


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
        option=AnalysisOption(no_check_cache=True),
    )
    assert isinstance(result, Success)
    return result.unwrap()


def make_user_model_import() -> ImportAnalysis:
    return ImportAnalysis(
        local_name="UserModel",
        imported_name="project_b.pydantic_models.models.UserModel",
        kind=ImportKind.SYMBOL,
    )


def make_user_model_reference() -> ResolvedReference:
    target_import = ImportAnalysis(
        local_name="UserModel",
        imported_name="project_b.pydantic_models.models.UserModel",
        kind=ImportKind.SYMBOL,
    )
    return ResolvedReference(
        import_analysis=target_import,
        module_path=PythonPath("project_b.pydantic_models.models"),
        symbol_id=SymbolId("project_b.pydantic_models.models::UserModel"),
    )


class TestResolveReferenceFileAnalysisContext:
    def test_import_analysis_is_none_returns_none(self) -> None:
        workspace = Mock(spec=WorkspaceContext)
        reference = ResolvedReference(
            import_analysis=None,
            module_path=PythonPath("project_b.pydantic_models.models"),
            symbol_id=None,
        )

        result = resolve_reference_file_analysis_context(
            reference=reference,
            workspace=workspace,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None
        workspace.find_workspace_file_analysis_context.assert_not_called()

    def test_resolves_existing_module(
        self,
        workspace_context: WorkspaceContext,
    ) -> None:
        reference = make_user_model_reference()

        result = resolve_reference_file_analysis_context(
            reference=reference,
            workspace=workspace_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is not None

    def test_propagates_failure(self) -> None:
        workspace = Mock(spec=WorkspaceContext)
        error = create_analysis_error()
        workspace.find_workspace_file_analysis_context.return_value = Failure(error)
        reference = make_user_model_reference()

        result = resolve_reference_file_analysis_context(
            reference=reference,
            workspace=workspace,
        )

        assert isinstance(result, Failure)
        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, ResolveError)
        assert failure.__cause__ is error


class TestResolveReferencedSymbol:
    def test_import_analysis_is_none_returns_none(
        self,
        project_b_file_context: FileAnalysisContext,
    ) -> None:
        reference = ResolvedReference(
            import_analysis=None,
            module_path=PythonPath("project_b.pydantic_models.models"),
            symbol_id=SymbolId("project_b.pydantic_models.models::UserModel"),
        )

        result = resolve_referenced_symbol(
            reference=reference,
            file_analysis_context=project_b_file_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

    def test_symbol_id_is_none_returns_none(
        self,
        project_b_file_context: FileAnalysisContext,
    ) -> None:
        reference = ResolvedReference(
            import_analysis=ImportAnalysis(
                local_name="models",
                imported_name="project_b.pydantic_models.models",
                kind=ImportKind.MODULE,
            ),
            module_path=PythonPath("project_b.pydantic_models.models"),
            symbol_id=None,
        )

        result = resolve_referenced_symbol(
            reference=reference,
            file_analysis_context=project_b_file_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

    def test_resolves_existing_symbol(
        self,
        project_b_file_context: FileAnalysisContext,
    ) -> None:
        reference = make_user_model_reference()

        result = resolve_referenced_symbol(
            reference=reference,
            file_analysis_context=project_b_file_context,
        )

        assert isinstance(result, Success)
        symbol = result.unwrap()
        assert isinstance(symbol, ClassAnalysis)

    def test_missing_symbol_returns_none(
        self,
        project_b_file_context: FileAnalysisContext,
    ) -> None:
        reference = ResolvedReference(
            import_analysis=ImportAnalysis(
                local_name="MissingModel",
                imported_name=("project_b.pydantic_models.models.MissingModel"),
                kind=ImportKind.SYMBOL,
            ),
            module_path=PythonPath("project_b.pydantic_models.models"),
            symbol_id=SymbolId("project_b.pydantic_models.models::MissingModel"),
        )

        result = resolve_referenced_symbol(
            reference=reference,
            file_analysis_context=project_b_file_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None


class TestResolveReferenceSymbol:
    def test_resolves_symbol_through_workspace(
        self, workspace_context: WorkspaceContext
    ) -> None:
        reference = make_user_model_reference()

        result = resolve_reference_symbol(
            reference=reference,
            workspace=workspace_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is not None

    def test_missing_module_returns_failure(
        self, workspace_context: WorkspaceContext
    ) -> None:
        target_import = ImportAnalysis(
            local_name="MissingModel",
            imported_name="project_b.nonexistent.models.MissingModel",
            kind=ImportKind.SYMBOL,
        )
        reference = ResolvedReference(
            import_analysis=target_import,
            module_path=PythonPath("project_b.nonexistent.models"),
            symbol_id=SymbolId("project_b.nonexistent.models::MissingModel"),
        )

        result = resolve_reference_symbol(
            reference=reference,
            workspace=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, ResolveError)
        assert isinstance(failure.__cause__, AnalysisError)

    def test_propagates_failure(self) -> None:
        workspace = Mock(spec=WorkspaceContext)
        error = create_analysis_error()
        workspace.find_workspace_file_analysis_context.return_value = Failure(error)
        reference = make_user_model_reference()

        result = resolve_reference_symbol(
            reference=reference,
            workspace=workspace,
        )

        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, ResolveError)
        assert failure.__cause__ is error


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
            option=AnalysisOption(no_check_cache=True),
        )
        assert isinstance(consumer_result, Success)

        consumer_context = consumer_result.unwrap()
        target_reference = resolve_reference(
            local_name,
            consumer_context.analysis,
        )
        assert target_reference is not None

        file_result = resolve_reference_file_analysis_context(
            reference=target_reference,
            workspace=workspace_context,
        )
        assert isinstance(file_result, Success)

        file_context = file_result.unwrap()
        assert file_context is not None

        symbol_result = resolve_referenced_symbol(
            reference=target_reference,
            file_analysis_context=file_context,
        )
        assert isinstance(symbol_result, Success)

        symbol = symbol_result.unwrap()
        assert symbol is not None
        assert isinstance(symbol, expected_type)
