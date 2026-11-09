from pathlib import Path
from unittest.mock import Mock

import pytest
from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.symbol import (
    resolve_workspace_symbol_analysis,
)
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationIdentity,
    PythonPath,
    SourceRelativePath,
)
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_project_context,
    create_workspace_context,
)
from packages.schema.test_support.helpers import (
    create_class_analysis,
    create_class_variable_analysis,
    create_file_analysis_context,
    create_function_analysis,
    create_module_analysis,
    create_type_alias_analysis,
    create_variable_analysis,
    simple_create_declaration_identity,
)


@pytest.fixture
def declaration_identity() -> DeclarationIdentity:
    return simple_create_declaration_identity("sample.module")


@pytest.fixture
def file_analysis_context() -> FileAnalysisContext:
    return create_file_analysis_context(
        analysis=create_module_analysis(
            module_name=PythonPath("sample.module"),
            path=SourceRelativePath(Path("sample/module.py")),
        )
    )


@pytest.fixture
def project_context() -> ProjectContext:
    return create_project_context()


@pytest.fixture
def workspace_context() -> WorkspaceContext:
    return create_workspace_context()


class TestResolveWorkspaceSymbolAnalysis:
    @pytest.mark.parametrize(
        "symbol",
        [
            create_variable_analysis(),
            create_class_analysis(),
            create_function_analysis(),
            create_type_alias_analysis(),
        ],
        ids=["variable", "class", "function", "type_alias"],
    )
    def test__success(
        self,
        declaration_identity: DeclarationIdentity,
        file_analysis_context: FileAnalysisContext,
        project_context: ProjectContext,
        workspace_context: WorkspaceContext,
        symbol: SymbolAnalysis,
    ) -> None:
        file_analysis_context.metadata.symbols = {
            declaration_identity: symbol,
        }
        workspace_context.find_file_analysis_context = Mock(
            return_value=Success((file_analysis_context, project_context))
        )

        result = resolve_workspace_symbol_analysis(
            declaration_identity=declaration_identity,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == (file_analysis_context, symbol)
        workspace_context.find_file_analysis_context.assert_called_once_with(
            target_identity=declaration_identity
        )

    def test_module_not_found(
        self,
        declaration_identity: DeclarationIdentity,
        workspace_context: WorkspaceContext,
    ) -> None:
        workspace_context.find_file_analysis_context = Mock(return_value=Success(None))

        result = resolve_workspace_symbol_analysis(
            declaration_identity=declaration_identity,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

    def test_symbol_not_found(
        self,
        declaration_identity: DeclarationIdentity,
        file_analysis_context: FileAnalysisContext,
        project_context: ProjectContext,
        workspace_context: WorkspaceContext,
    ) -> None:
        file_analysis_context.metadata.symbols = {}
        workspace_context.find_file_analysis_context = Mock(
            return_value=Success((file_analysis_context, project_context))
        )

        result = resolve_workspace_symbol_analysis(
            declaration_identity=declaration_identity,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)

        error = result.failure()
        assert error.message == "can not find symbol on the file"
        assert error.reference == Path("sample/module.py")
        assert error.details == {
            "project": "test",
            "target_symbol": declaration_identity.symbol_id,
        }

    def test_resolve_workspace_symbol_analysis_invalid_symbol_type(
        self,
        declaration_identity: DeclarationIdentity,
        file_analysis_context: FileAnalysisContext,
        project_context: ProjectContext,
        workspace_context: WorkspaceContext,
    ) -> None:
        file_analysis_context.metadata.symbols = {
            declaration_identity: create_class_variable_analysis(),
        }
        workspace_context.find_file_analysis_context = Mock(
            return_value=Success((file_analysis_context, project_context))
        )

        result = resolve_workspace_symbol_analysis(
            declaration_identity=declaration_identity,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)

        error = result.failure()
        assert error.message == "target symbol is not Symbol"
        assert error.reference == Path("sample/module.py")
        assert error.details == {
            "project": "test",
            "target_identity": declaration_identity,
        }

    def test_resolve_workspace_symbol_analysis_lookup_failure(
        self,
        declaration_identity: DeclarationIdentity,
        workspace_context: WorkspaceContext,
    ) -> None:
        workspace_context.find_file_analysis_context = Mock(
            return_value=Failure(
                ResolveError(
                    message="original lookup error",
                    reference="sample.module",
                )
            )
        )

        result = resolve_workspace_symbol_analysis(
            declaration_identity=declaration_identity,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)

        error = result.failure()
        assert error.message == "fail to find target file"
        assert error.reference == "sample.module"
