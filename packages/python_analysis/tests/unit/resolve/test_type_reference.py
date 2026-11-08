from typing import get_args
from unittest.mock import MagicMock

from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.symbol import (
    resolve_workspace_symbol_analysis as actual_resolve_workspace_symbol_analysis,
)
from gyomu_python_analysis.resolve.type_reference import (
    _resolve_structure,
    resolve_type_analysis,
)
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.type.structure import (
    UnknownStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    StructureAnalysis,
)
from gyomu_schema.schemas.python.types import DeclarationIdentity, PythonPath
from gyomu_schema.schemas.python.variable import VariableAnalysis
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    AnalysisTestBase,
    BaseContext,
    create_resolve_error,
)
from packages.schema.test_support.helpers import STRUCTURE_FACTORIES


def test_all_structure_types_have_handlers(mocker) -> None:
    structure_types: set[type[StructureAnalysis]] = set(
        get_args(StructureAnalysis.__value__)
    )
    factory_types: set[type[StructureAnalysis]] = set(STRUCTURE_FACTORIES)

    assert structure_types == factory_types
    module = MagicMock(spec=ModuleAnalysis)
    module.imports = {}
    module.symbols = tuple()

    workspace_context = MagicMock(spec=WorkspaceContext)
    for structure in STRUCTURE_FACTORIES.values():
        if not isinstance(structure, UnknownStructureAnalysis):
            _resolve_structure(
                structure=structure,
                parameter_name="param",
                module=module,
                workspace_context=workspace_context,
            )


class TestResolveTypeAnalysis(AnalysisTestBase):
    def _analyze_variable_internal(
        self, name: str, module_name: PythonPath
    ) -> tuple[VariableAnalysis, BaseContext, FileAnalysisContext]:
        return self._analyze_variable_base(module_name, name)

    def _analyze_generics(
        self, name: str
    ) -> tuple[VariableAnalysis, BaseContext, FileAnalysisContext]:
        return self._analyze_variable_internal(
            name, PythonPath("analysis.symbol.generics")
        )

    def test_analyze_generic_deep_nested(self) -> None:
        result, base_context, file_analysis_context = self._analyze_generics(
            "value_generic_deep_nested"
        )

        assert result.type is not None
        resolve_result = resolve_type_analysis(
            type_analysis=result.type,
            parameter_name=result.name,
            workspace_context=base_context.workspace_context,
            module=file_analysis_context.analysis,
        )
        assert isinstance(resolve_result, Success)

    def test_resolve_type_analysis_propagates_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        result, base_context, file_analysis_context = self._analyze_generics(
            "value_generic_deep_nested"
        )
        assert result.type is not None

        expected_error = create_resolve_error()
        resolve_symbol_analysis_mock = mocker.patch(
            "gyomu_python_analysis.resolve.type_reference.resolve_workspace_symbol_analysis",
            return_value=Failure(expected_error),
        )

        resolve_result = resolve_type_analysis(
            type_analysis=result.type,
            parameter_name=result.name,
            workspace_context=base_context.workspace_context,
            module=file_analysis_context.analysis,
        )

        assert resolve_result == Failure(expected_error)
        resolve_symbol_analysis_mock.assert_called_once()

    def test_resolve_type_analysis_propagates_nested_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        result, base_context, file_analysis_context = self._analyze_generics(
            "value_generic_deep_nested"
        )
        assert result.type is not None

        expected_error = create_resolve_error()

        call_count = 0

        def resolve_workspace_symbol_analysis_side_effect(
            declaration_identity: DeclarationIdentity,
            workspace_context: WorkspaceContext,
        ) -> object:
            nonlocal call_count
            call_count += 1

            if call_count == 2:
                return Failure(expected_error)

            return actual_resolve_workspace_symbol_analysis(
                declaration_identity=declaration_identity,
                workspace_context=workspace_context,
            )

        resolve_symbol_analysis_mock = mocker.patch(
            "gyomu_python_analysis.resolve.type_reference.resolve_workspace_symbol_analysis",
            side_effect=resolve_workspace_symbol_analysis_side_effect,
        )

        resolve_result = resolve_type_analysis(
            type_analysis=result.type,
            parameter_name=result.name,
            module=file_analysis_context.analysis,
            workspace_context=base_context.workspace_context,
        )

        assert resolve_result == Failure(expected_error)
        assert resolve_symbol_analysis_mock.call_count == 2
