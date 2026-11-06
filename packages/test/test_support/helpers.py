from collections.abc import Mapping
from pathlib import Path

from gyomu_python_analysis.resolve.models import (
    LiteralValueType,
    PrimitiveType,
    ResolvedType,
    SymbolType,
)
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    Parameter,
    PrimitiveDefault,
)
from gyomu_schema.schemas.testing.helper import ParameterInfo, TargetClassKind
from gyomu_schema.schemas.types import FullPath
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.defaults.requirements import (
    ConfiguredParameterDefault,
    MissingParameterDefault,
    ResolvedHelperSymbolDefault,
    ResolvedNonHelperDefault,
    ResolvedParameterDefault,
    ResolvedPrimitiveDefault,
)

from packages.python_analysis.test_support.helpers import (
    create_primitive_type,
    create_symbol_type,
)
from packages.schema.test_support.helpers import (
    create_literal_parameter,
    create_model_default,
    create_primitive_default,
)
from packages.schema.test_support.testing_helpers import create_parameter_info

MONOREPO_FIXTURES_ROOT = FullPath(Path(__file__).parent / "monorepo_fixtures")


def create_test_error(
    message: str = "Test", details: Mapping[str, object] | None = None
) -> GyomuTestError:
    return GyomuTestError(message=message, details=details)


def create_resolved_helper_symbol_default(
    resolved_type: SymbolType = create_symbol_type(),
    model_kind: TargetClassKind = TargetClassKind.DATACLASS,
) -> ResolvedHelperSymbolDefault:
    return ResolvedHelperSymbolDefault(
        resolved_type=resolved_type, model_kind=model_kind
    )


def create_resolved_non_helper_default(
    resolved_type: SymbolType = create_symbol_type(),
    config: ModelDefault = create_model_default(),
) -> ResolvedNonHelperDefault:
    return ResolvedNonHelperDefault(resolved_type=resolved_type, config=config)


def create_resolved_primitive_default(
    resolved_type: PrimitiveType | LiteralValueType = create_primitive_type(),
    config: PrimitiveDefault = create_primitive_default(),
) -> ResolvedPrimitiveDefault:
    return ResolvedPrimitiveDefault(resolved_type=resolved_type, config=config)


def create_missing_parameter_default(
    parameter: ParameterInfo = create_parameter_info(),
    missing_types: tuple[ResolvedType, ...] = (create_primitive_type(),),
) -> MissingParameterDefault:
    return MissingParameterDefault(parameter=parameter, missing_types=missing_types)


def create_resolved_parameter_default(
    parameter: ParameterInfo = create_parameter_info(),
    default: Parameter = create_literal_parameter(),
) -> ResolvedParameterDefault:
    return ResolvedParameterDefault(parameter=parameter, default=default)


def create_configured_parameter_default(
    parameter: ParameterInfo = create_parameter_info(),
) -> ConfiguredParameterDefault:
    return ConfiguredParameterDefault(parameter=parameter)
