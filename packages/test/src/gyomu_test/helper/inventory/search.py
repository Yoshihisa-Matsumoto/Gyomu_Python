from pathlib import Path

from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
)
from gyomu_python_analysis.resolve.models import SymbolType
from gyomu_python_analysis.resolve.type_reference import resolve_type_analysis
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.type.structure import NameStructureAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity, ProjectRelativePath
from returns.result import Failure, Result, Success

from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.inventory.config import get_helper_file_paths
from gyomu_test.helper.inventory.naming import (
    _build_helper_name_from_class_name,
)


def _get_helper_file_paths(
    model_identity: DeclarationIdentity,
    test_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
    model_project_context: ProjectContext | None,
    is_generated_only: bool,
) -> Result[tuple[tuple[ProjectContext, ProjectRelativePath], ...], GyomuTestError]:
    result: list[tuple[ProjectContext, ProjectRelativePath]] = []

    if not is_generated_only:
        test_file_result = get_helper_file_paths(project_context=test_project_context)
        if isinstance(test_file_result, Failure):
            return test_file_result
        for test_path in test_file_result.unwrap():
            result.append((test_project_context, test_path))

    if model_project_context is None:
        model_search_result = workspace_context.find_file_analysis_context(
            target_identity=model_identity
        )
        if isinstance(model_search_result, Failure):
            return model_search_result.alt(
                lambda error: GyomuTestError(
                    "fail to search model", details={"identity": model_identity}
                ).chain(error)
            )
        model_search = model_search_result.unwrap()
        if model_search is None:
            return Failure(
                GyomuTestError("model not found", details={"identity": model_identity})
            )
        _, model_project_context = model_search

    if model_project_context is not None and (
        is_generated_only
        or test_project_context.project_root != model_project_context.project_root
    ):
        model_file_result = get_helper_file_paths(project_context=model_project_context)
        if isinstance(model_file_result, Failure):
            return model_file_result
        for test_path in model_file_result.unwrap():
            result.append((model_project_context, test_path))

    return Success(tuple(result))


def _get_helper_function_candidate(
    model_identity: DeclarationIdentity,
    symbol: SymbolAnalysis,
    module: ModuleAnalysis,
    workspace_context: WorkspaceContext,
) -> Result[DeclarationIdentity | None, GyomuTestError]:
    if not isinstance(symbol, FunctionAnalysis):
        return Success(None)
    func = symbol
    if func.return_type is None:
        return Success(None)

    type_result = resolve_type_analysis(
        type_analysis=func.return_type,
        parameter_name="$return",
        module=module,
        workspace_context=workspace_context,
    )
    if isinstance(type_result, Failure):
        return type_result.alt(
            lambda error: GyomuTestError(
                "fail to resolve return type", details={"identity": func.identity}
            ).chain(error)
        )
    resolved_types = type_result.unwrap()
    if len(resolved_types) != 1:
        return Success(None)
    target_resolved_type = resolved_types[0]
    if not isinstance(target_resolved_type, SymbolType):
        return Success(None)
    if target_resolved_type.symbol.identity != model_identity:
        return Success(None)
    if func.return_type.structure is not None and isinstance(
        func.return_type.structure, NameStructureAnalysis
    ):
        return Success(symbol.identity)
    return Success(None)


def _get_generated_helper_function_candidate(
    model_identity: DeclarationIdentity,
    symbol: SymbolAnalysis,
    module: ModuleAnalysis,
    workspace_context: WorkspaceContext,
) -> Result[DeclarationIdentity | None, GyomuTestError]:
    if not isinstance(symbol, FunctionAnalysis):
        return Success(None)
    func = symbol
    expected_function_name = _build_helper_name_from_class_name(
        class_name=model_identity.get_symbol_name()
    )
    if func.name != expected_function_name:
        return Success(None)
    return _get_helper_function_candidate(
        model_identity=model_identity,
        symbol=symbol,
        module=module,
        workspace_context=workspace_context,
    )


def _get_helper_candidates(
    model_identity: DeclarationIdentity,
    test_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
    model_project_context: ProjectContext | None,
    is_generated_only: bool,
) -> Result[tuple[tuple[DeclarationIdentity, ProjectContext], ...], GyomuTestError]:
    result: list[tuple[DeclarationIdentity, ProjectContext]] = []
    helper_file_paths_result = _get_helper_file_paths(
        model_identity=model_identity,
        test_project_context=test_project_context,
        workspace_context=workspace_context,
        model_project_context=model_project_context,
        is_generated_only=is_generated_only,
    )
    if isinstance(helper_file_paths_result, Failure):
        return helper_file_paths_result

    root_context_result = initialize_project_context(
        project_root=workspace_context.path,
        source_root=ProjectRelativePath(Path(".")),
    )
    if isinstance(root_context_result, Failure):
        return root_context_result.alt(
            lambda error: GyomuTestError("fail to initialze root project").chain(error)
        )

    root_context = root_context_result.unwrap()
    helper_file_paths = helper_file_paths_result.unwrap()
    for project_context, helper_file_path in helper_file_paths:
        file_path = ProjectRelativePath(project_context.config.path / helper_file_path)
        file_result = load_file_analysis_context(
            context=root_context,
            file_path=file_path,
        )
        if isinstance(file_result, Failure):
            return file_result.alt(
                lambda error: GyomuTestError("fail to analyze file").chain(error)
            )
        file_analysis_context = file_result.unwrap()
        for symbol in file_analysis_context.analysis.symbols:
            if symbol.kind != DeclarationKind.FUNCTION:
                continue
            if is_generated_only:
                function_identity_result = _get_generated_helper_function_candidate(
                    model_identity=model_identity,
                    symbol=symbol,
                    module=file_analysis_context.analysis,
                    workspace_context=workspace_context,
                )
            else:
                function_identity_result = _get_helper_function_candidate(
                    model_identity=model_identity,
                    symbol=symbol,
                    module=file_analysis_context.analysis,
                    workspace_context=workspace_context,
                )
            if isinstance(function_identity_result, Failure):
                return function_identity_result
            function_identity = function_identity_result.unwrap()
            if function_identity is not None:
                result.append((function_identity, project_context))

    return Success(tuple(result))


def get_generated_helper_candidates(
    model_identity: DeclarationIdentity,
    test_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
    model_project_context: ProjectContext | None = None,
) -> Result[tuple[tuple[DeclarationIdentity, ProjectContext], ...], GyomuTestError]:
    return _get_helper_candidates(
        model_identity=model_identity,
        test_project_context=test_project_context,
        workspace_context=workspace_context,
        model_project_context=model_project_context,
        is_generated_only=True,
    )


def get_all_helper_candidates(
    model_identity: DeclarationIdentity,
    test_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
    model_project_context: ProjectContext | None = None,
) -> Result[tuple[tuple[DeclarationIdentity, ProjectContext], ...], GyomuTestError]:
    return _get_helper_candidates(
        model_identity=model_identity,
        test_project_context=test_project_context,
        workspace_context=workspace_context,
        model_project_context=model_project_context,
        is_generated_only=False,
    )
