from gyomu_config.manager import ConfigManager
from gyomu_config.request import (
    ComplexConfigExtractorRequest,
    FirstAvailableStrategy,
    MergePolicy,
)
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    PackageModelDefaults,
    PrimitiveDefault,
)
from returns.result import Result

from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.defaults.resolution import (
    PrimitiveDefaultConfigContext,
    PrimitiveDefaultResolver,
    SymbolDefaultConfigContext,
    SymbolDefaultResolver,
)


def _build_primitive_config_request(
    context: PrimitiveDefaultConfigContext,
) -> ComplexConfigExtractorRequest[
    PackageModelDefaults, PrimitiveDefault, PrimitiveDefaultConfigContext
]:
    resolver = PrimitiveDefaultResolver()
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

    request = _build_primitive_config_request(context)
    return config_manager.retrieve_extracted_config(request).alt(
        lambda e: GyomuTestError(
            "Failed to load primitive parameter default config"
        ).chain(e)
    )


def _build_symbol_config_request(
    context: SymbolDefaultConfigContext,
) -> ComplexConfigExtractorRequest[
    PackageModelDefaults, ModelDefault, SymbolDefaultConfigContext
]:
    resolver = SymbolDefaultResolver()
    return ComplexConfigExtractorRequest[
        PackageModelDefaults, ModelDefault, SymbolDefaultConfigContext
    ](
        config_type=PackageModelDefaults,
        context=context,
        paths_resolver=resolver,
        merge_policy=MergePolicy[ModelDefault](strategy=FirstAvailableStrategy()),
        default_value=None,
        extractor=resolver,
    )


def load_symbol_parameter_default_config(
    context: SymbolDefaultConfigContext,
    config_manager: ConfigManager,
) -> Result[ModelDefault | None, GyomuTestError]:

    request = _build_symbol_config_request(context)
    return config_manager.retrieve_extracted_config(request).alt(
        lambda e: GyomuTestError(
            "Failed to load symbol parameter default config"
        ).chain(e)
    )
