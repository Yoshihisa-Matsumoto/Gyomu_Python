from gyomu_config.manager import ConfigManager
from gyomu_config.request import (
    ComplexConfigExtractorRequest,
    FirstAvailableStrategy,
    MergePolicy,
)
from gyomu_schema.schemas.config.test.model_defaults import (
    PackageModelDefaults,
    PrimitiveDefault,
    SymbolDefault,
)
from returns.result import Result

from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.defaults.resolution import (
    PrimitiveDefaultConfigContext,
    PrimitiveDefaultResolver,
    ProjectPrimitiveDefaultResolver,
    ProjectSymbolDefaultResolver,
    SymbolDefaultConfigContext,
    SymbolDefaultResolver,
    WorkspacePrimitiveDefaultResolver,
    WorkspaceSymbolDefaultResolver,
)


def _build_primitive_config_request(
    context: PrimitiveDefaultConfigContext, resolver: PrimitiveDefaultResolver
) -> ComplexConfigExtractorRequest[
    PackageModelDefaults, PrimitiveDefault, PrimitiveDefaultConfigContext
]:
    return ComplexConfigExtractorRequest[
        PackageModelDefaults, PrimitiveDefault, PrimitiveDefaultConfigContext
    ](
        config_type=PackageModelDefaults,
        context=context,
        paths_resolver=resolver,
        merge_policy=MergePolicy[PrimitiveDefault](strategy=FirstAvailableStrategy()),
        default_value=None,
        extractor=resolver,
    )


def load_primitive_parameter_default_config(
    context: PrimitiveDefaultConfigContext,
    config_manager: ConfigManager,
) -> Result[PrimitiveDefault | None, GyomuTestError]:
    request = _build_primitive_config_request(
        context=context, resolver=PrimitiveDefaultResolver()
    )

    return _internal_load_primitive_parameter_default_config(
        config_manager=config_manager, request=request
    )


def load_workspace_primitive_parameter_default_config(
    context: PrimitiveDefaultConfigContext,
    config_manager: ConfigManager,
) -> Result[PrimitiveDefault | None, GyomuTestError]:

    request = _build_primitive_config_request(
        context=context, resolver=WorkspacePrimitiveDefaultResolver()
    )
    return _internal_load_primitive_parameter_default_config(
        config_manager=config_manager, request=request
    )


def load_project_primitive_parameter_default_config(
    context: PrimitiveDefaultConfigContext,
    config_manager: ConfigManager,
) -> Result[PrimitiveDefault | None, GyomuTestError]:

    request = _build_primitive_config_request(
        context=context, resolver=ProjectPrimitiveDefaultResolver()
    )
    return _internal_load_primitive_parameter_default_config(
        config_manager=config_manager, request=request
    )


def _internal_load_primitive_parameter_default_config(
    config_manager: ConfigManager,
    request: ComplexConfigExtractorRequest[
        PackageModelDefaults, PrimitiveDefault, PrimitiveDefaultConfigContext
    ],
) -> Result[PrimitiveDefault | None, GyomuTestError]:
    return config_manager.retrieve_extracted_config(request).alt(
        lambda e: GyomuTestError(
            "Failed to load primitive parameter default config"
        ).chain(e)
    )


def _build_symbol_config_request(
    context: SymbolDefaultConfigContext, resolver: SymbolDefaultResolver
) -> ComplexConfigExtractorRequest[
    PackageModelDefaults, SymbolDefault, SymbolDefaultConfigContext
]:

    return ComplexConfigExtractorRequest[
        PackageModelDefaults, SymbolDefault, SymbolDefaultConfigContext
    ](
        config_type=PackageModelDefaults,
        context=context,
        paths_resolver=resolver,
        merge_policy=MergePolicy[SymbolDefault](strategy=FirstAvailableStrategy()),
        default_value=None,
        extractor=resolver,
    )


def load_symbol_parameter_default_config(
    context: SymbolDefaultConfigContext,
    config_manager: ConfigManager,
) -> Result[SymbolDefault | None, GyomuTestError]:

    request = _build_symbol_config_request(
        context=context, resolver=SymbolDefaultResolver()
    )
    return _internal_load_symbol_parameter_default_config(
        config_manager=config_manager, request=request
    )


def load_workspace_symbol_parameter_default_config(
    context: SymbolDefaultConfigContext,
    config_manager: ConfigManager,
) -> Result[SymbolDefault | None, GyomuTestError]:

    request = _build_symbol_config_request(
        context=context, resolver=WorkspaceSymbolDefaultResolver()
    )
    return _internal_load_symbol_parameter_default_config(
        config_manager=config_manager, request=request
    )


def load_test_project_symbol_parameter_default_config(
    context: SymbolDefaultConfigContext,
    config_manager: ConfigManager,
) -> Result[SymbolDefault | None, GyomuTestError]:

    request = _build_symbol_config_request(
        context=context, resolver=ProjectSymbolDefaultResolver()
    )
    return _internal_load_symbol_parameter_default_config(
        config_manager=config_manager, request=request
    )


def _internal_load_symbol_parameter_default_config(
    config_manager: ConfigManager,
    request: ComplexConfigExtractorRequest[
        PackageModelDefaults, SymbolDefault, SymbolDefaultConfigContext
    ],
) -> Result[SymbolDefault | None, GyomuTestError]:
    return config_manager.retrieve_extracted_config(request).alt(
        lambda e: GyomuTestError(
            "Failed to load symbol parameter default config"
        ).chain(e)
    )
