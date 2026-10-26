from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity, SymbolId
from returns.result import Failure, Result, Success

from gyomu_python_analysis.analysis.query import (
    find_symbol_by_name,
)
from gyomu_python_analysis.analysis.resolve.file_analysis_cache import FileAnalysisCache
from gyomu_python_analysis.analysis.resolve.imports import (
    resolve_reference_file_analysis_context,
    resolve_referenced_symbol,
)
from gyomu_python_analysis.analysis.resolve.models import (
    ClassResolution,
    ClassResolutionCollection,
    ExternalClass,
    ResolvedClass,
    UnresolvedClass,
)
from gyomu_python_analysis.analysis.resolve.path import normalize_reference_name
from gyomu_python_analysis.analysis.resolve.reference import resolve_reference
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext


def _register_identity(
    resolved_class: ResolvedClass,
    resolved_classes: list[ClassResolution],
    registered_identity: set[DeclarationIdentity],
) -> None:
    if resolved_class.symbol.identity not in registered_identity:
        resolved_classes.append(resolved_class)
        registered_identity.add(resolved_class.symbol.identity)


def collect_class_hierarchy(
    cls: ClassAnalysis,
    module: ModuleAnalysis,
    workspace: WorkspaceContext,
    is_base_first: bool = True,
) -> Result[ClassResolutionCollection, AnalysisError]:
    resolved_classes: list[ClassResolution] = []
    registered_identity: set[DeclarationIdentity] = set()
    visited_identity: set[DeclarationIdentity] = set()

    def visit(
        current_cls: ClassAnalysis,
        current_module: ModuleAnalysis,
    ) -> Result[None, AnalysisError]:
        if current_cls.identity in visited_identity:
            return Success(None)

        visited_identity.add(current_cls.identity)
        current_class = ResolvedClass(
            symbol=current_cls,
            module=current_module,
        )

        if not is_base_first:
            _register_identity(
                resolved_class=current_class,
                resolved_classes=resolved_classes,
                registered_identity=registered_identity,
            )

        for base in current_cls.bases:
            target_reference = resolve_reference(
                base.text,
                current_module,
            )

            if target_reference is None:
                resolved_classes.append(
                    UnresolvedClass(
                        reference_name=base.text,
                        reason="reference-not-resolved",
                    )
                )
                continue

            if target_reference.import_analysis is not None:
                module_result = resolve_reference_file_analysis_context(
                    reference=target_reference,
                    workspace=workspace,
                )
                if isinstance(module_result, Failure):
                    return module_result

                file_analysis_context = module_result.unwrap()

                if file_analysis_context is None:
                    resolved_classes.append(ExternalClass(reference=target_reference))
                    continue

                target_symbol_result = resolve_referenced_symbol(
                    reference=target_reference,
                    file_analysis_context=file_analysis_context,
                )
                if isinstance(target_symbol_result, Failure):
                    return target_symbol_result

                target_symbol = target_symbol_result.unwrap()

                if target_symbol is None:
                    resolved_classes.append(
                        UnresolvedClass(
                            reference_name=base.text,
                            reason="symbol-not-found-in-module",
                        )
                    )
                    continue

                if not isinstance(target_symbol, ClassAnalysis):
                    resolved_classes.append(
                        UnresolvedClass(
                            reference_name=base.text,
                            reason="symbol-is-not-class",
                        )
                    )
                    continue

                target_module = file_analysis_context.analysis

            else:
                target_symbol = find_symbol_by_name(
                    name=base.text,
                    module=current_module,
                )

                if target_symbol is None:
                    resolved_classes.append(
                        UnresolvedClass(
                            reference_name=base.text,
                            reason="reference-not-resolved",
                        )
                    )
                    continue

                if not isinstance(target_symbol, ClassAnalysis):
                    resolved_classes.append(
                        UnresolvedClass(
                            reference_name=base.text,
                            reason="symbol-is-not-class",
                        )
                    )
                    continue

                target_module = current_module

            visit_result = visit(
                current_cls=target_symbol,
                current_module=target_module,
            )
            if isinstance(visit_result, Failure):
                return visit_result

        if is_base_first:
            _register_identity(
                resolved_class=current_class,
                resolved_classes=resolved_classes,
                registered_identity=registered_identity,
            )

        return Success(None)

    result = visit(cls, module)
    if isinstance(result, Failure):
        return result

    return Success(ClassResolutionCollection(tuple(resolved_classes)))


# def _create_external_class(reference:ResolvedReference)


def is_dataclass_class(cls: ClassAnalysis, module: ModuleAnalysis) -> bool:
    for decorator in cls.decorators:
        normalized_name = normalize_reference_name(
            module.imports,
            decorator.name,
        )
        if normalized_name == "dataclasses.dataclass":
            return True

    return False


def inherits_from_gyomu_base_error(
    cls: ClassAnalysis,
    module: ModuleAnalysis,
    workspace: WorkspaceContext,
) -> Result[bool, AnalysisError]:
    resolve_result = collect_class_hierarchy(
        cls=cls, module=module, workspace=workspace
    )
    if isinstance(resolve_result, Failure):
        return resolve_result
    for external in resolve_result.unwrap().external():
        if external.reference.symbol_id == SymbolId(
            "gyomu_schema.error.base::BaseError"
        ):
            return Success(True)
    for resolved in resolve_result.unwrap().resolved():
        if resolved.symbol.identity.symbol_id == SymbolId(
            "gyomu_schema.error.base::BaseError"
        ):
            return Success(True)

    return Success(False)


def inherits_from_pydantic_basemodel(
    cls: ClassAnalysis,
    module: ModuleAnalysis,
    workspace: WorkspaceContext,
) -> Result[bool, AnalysisError]:
    resolve_result = collect_class_hierarchy(
        cls=cls, module=module, workspace=workspace
    )
    if isinstance(resolve_result, Failure):
        return resolve_result
    for external in resolve_result.unwrap().external():
        if external.reference.symbol_id == SymbolId("pydantic::BaseModel"):
            return Success(True)

    return Success(False)


def resolve_class_analysis(
    declaration_identity: DeclarationIdentity,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
) -> Result[tuple[FileAnalysisContext, ClassAnalysis], AnalysisError]:
    context_result = file_analysis_cache.get_file_analysis_context(
        project_context=project_context, identity=declaration_identity
    )
    if isinstance(context_result, Failure):
        return context_result
    file_analysis = context_result.unwrap()

    symbol = file_analysis.metadata.symbols.get(declaration_identity)
    if isinstance(symbol, ClassAnalysis):
        return Success((file_analysis, symbol))
    return Failure(
        AnalysisError(
            message="symbol is not found" if symbol is None else "symbol is not class",
            file_path=declaration_identity.get_module_name(),
            phase="resolve",
            details={"identity": declaration_identity},
        )
    )
