from collections.abc import Mapping
from dataclasses import dataclass

from gyomu_schema.error.base import BaseError
from gyomu_schema.schemas.python.types import DeclarationIdentity
from gyomu_schema.schemas.testing.helper import ParameterInfo


@dataclass(frozen=True)
class MissingFunctionParameterDefault:
    identity: DeclarationIdentity
    parameter: ParameterInfo


@dataclass(frozen=True)
class MissingTypeParameterDefaultError:
    symbol_name: str


class ParameterDefaultResolutionError(BaseError):
    target_identity: DeclarationIdentity
    function_parameters: tuple[MissingFunctionParameterDefault, ...]
    type_parameters: tuple[MissingTypeParameterDefaultError, ...]

    def __init__(
        self,
        message: str,
        *,
        target_identity: DeclarationIdentity,
        function_parameters: tuple[MissingFunctionParameterDefault, ...],
        type_parameters: tuple[MissingTypeParameterDefaultError, ...],
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.target_identity = target_identity
        self.function_parameters = function_parameters
        self.type_parameters = type_parameters
