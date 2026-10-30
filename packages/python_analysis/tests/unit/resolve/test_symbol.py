from pathlib import Path

from gyomu_python_analysis.analysis.initialize import (
    initialize_project_context,
)
from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.resolve.file_analysis_cache import FileAnalysisCache
from gyomu_python_analysis.resolve.symbol import resolve_symbol_analysis
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    ProjectRelativePath,
    SymbolId,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    FIXTURES_ROOT,
    create_analysis_error,
)
from packages.schema.test_support.helpers import (
    create_class_analysis,
    create_file_analysis_context,
)


class TestResolveSymbolAnalysis:
    def test_success(
        self,
        mocker: MockerFixture,
    ) -> None:
        identity = DeclarationIdentity(
            symbol_id=SymbolId("project_a.models::Product"),
            declaration_id=DeclarationId("."),
        )
        class_analysis = create_class_analysis(identity=identity)
        file_analysis_context = create_file_analysis_context(symbol=class_analysis)
        project_context = initialize_project_context(
            project_root=FIXTURES_ROOT,
            source_root=ProjectRelativePath(Path("src")),
        ).unwrap()

        file_analysis_context.metadata.symbols[identity] = class_analysis

        file_analysis_cache = mocker.create_autospec(
            FileAnalysisCache,
            instance=True,
        )
        file_analysis_cache.get_file_analysis_context.return_value = Success(
            file_analysis_context
        )

        result = resolve_symbol_analysis(
            declaration_identity=identity,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
        )

        assert isinstance(result, Success)
        file_analysis, symbol = result.unwrap()
        assert file_analysis is file_analysis_context
        assert symbol is class_analysis

        file_analysis_cache.get_file_analysis_context.assert_called_once_with(
            project_context=project_context,
            identity=identity,
        )

    def test_symbol_not_found(
        self,
        mocker: MockerFixture,
    ) -> None:
        identity = DeclarationIdentity(
            symbol_id=SymbolId("project_a.models::Missing"),
            declaration_id=DeclarationId("."),
        )
        file_analysis_context = create_file_analysis_context()
        project_context = initialize_project_context(
            project_root=FIXTURES_ROOT,
            source_root=ProjectRelativePath(Path("src")),
        ).unwrap()
        file_analysis_context.metadata.symbols.pop(identity, None)

        file_analysis_cache = mocker.create_autospec(
            FileAnalysisCache,
            instance=True,
        )
        file_analysis_cache.get_file_analysis_context.return_value = Success(
            file_analysis_context
        )

        result = resolve_symbol_analysis(
            declaration_identity=identity,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert error.message == "symbol is not found"
        assert error.details == {"identity": identity}

    def test_file_analysis_failure(self, mocker: MockerFixture) -> None:
        identity = DeclarationIdentity(
            symbol_id=SymbolId("project_a.models::Product"),
            declaration_id=DeclarationId("."),
        )
        project_context = initialize_project_context(
            project_root=FIXTURES_ROOT,
            source_root=ProjectRelativePath(Path("src")),
        ).unwrap()

        error = create_analysis_error()

        file_analysis_cache = mocker.create_autospec(
            FileAnalysisCache,
            instance=True,
        )
        file_analysis_cache.get_file_analysis_context.return_value = Failure(error)

        result = resolve_symbol_analysis(
            declaration_identity=identity,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
        )

        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, ResolveError)
        assert failure.__cause__ is error
