from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from returns.result import Failure, Result, Success

from gyomu_python_analysis.analysis.query import (
    find_import_by_local_name,
    find_symbol_by_name,
)
from gyomu_python_analysis.analysis.resolve.imports import (
    resolve_import_file_analysis_context,
    resolve_imported_symbol,
)
from gyomu_python_analysis.analysis.resolve.path import normalize_reference_name
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.workspace import WorkspaceContext


def is_dataclass_class(cls: ClassAnalysis, module: ModuleAnalysis) -> bool:
    for decorator in cls.decorators:
        normalized_name = normalize_reference_name(
            module.imports,
            decorator.name,
        )
        if normalized_name == "dataclasses.dataclass":
            return True

    return False


def inherits_from_pydantic_basemodel(
    cls: ClassAnalysis,
    module: ModuleAnalysis,
    workspace: WorkspaceContext,
) -> Result[bool, AnalysisError]:
    for base in cls.bases:
        normalized_name = normalize_reference_name(
            module.imports,
            base.text,
        )

        if normalized_name == "pydantic.BaseModel":
            return Success(True)

        target_import = find_import_by_local_name(base.text, module)

        if target_import is not None:
            module_result = resolve_import_file_analysis_context(
                target_import, workspace
            )
            if isinstance(module_result, Failure):
                return module_result
            file_analysis_context = module_result.unwrap()

            if file_analysis_context is None:
                continue

            target_symbol_result = resolve_imported_symbol(
                target_import=target_import, file_analysis_context=file_analysis_context
            )
            if isinstance(target_symbol_result, Failure):
                return target_symbol_result
            target_symbol = target_symbol_result.unwrap()
            if target_symbol is None:
                continue

            if not isinstance(target_symbol, ClassAnalysis):
                continue

            is_pydantic_result = inherits_from_pydantic_basemodel(
                target_symbol,
                file_analysis_context.analysis,
                workspace,
            )
            if isinstance(is_pydantic_result, Failure):
                return is_pydantic_result

            if is_pydantic_result.unwrap():
                return Success(True)

        else:
            target_symbol = find_symbol_by_name(base.text, module)

            if target_symbol is None or not isinstance(target_symbol, ClassAnalysis):
                continue

            is_pydantic_result = inherits_from_pydantic_basemodel(
                target_symbol,
                module,
                workspace,
            )
            if isinstance(is_pydantic_result, Failure):
                return is_pydantic_result

            if is_pydantic_result.unwrap():
                return Success(True)

    return Success(False)
