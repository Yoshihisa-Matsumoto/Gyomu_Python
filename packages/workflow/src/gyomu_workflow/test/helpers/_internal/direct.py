from pathlib import Path

from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    LiteralParameter,
    Parameter,
)
from gyomu_schema.schemas.interaction.request import (
    InputMode,
    InteractionDirectRequest,
    InteractionRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionCancelled,
)
from gyomu_test.helper.defaults.requirements import (
    ResolvedParameterDefault,
)
from returns.result import Failure, Result, Success

from gyomu_workflow.test.helpers._internal.models import (
    DefaultPrimitiveLiteralTypeParameterContext,
)
from gyomu_workflow.test.helpers._internal.type_parameter_config import (
    configure_primitive_literal_type_parameter_default,
)


class PrimitiveValueCodec:
    def parse(
        self, raw_input: str, context: DefaultPrimitiveLiteralTypeParameterContext
    ) -> Result[LiteralParameter, ValidationError]:
        parameter_type = context.parameter_type_name()
        try:
            match parameter_type:
                case "str":
                    return Success(LiteralParameter(value=raw_input))
                case "int":
                    return Success(LiteralParameter(value=int(raw_input)))
                case "bool":
                    match raw_input.strip().lower():
                        case "true":
                            return Success(LiteralParameter(value=True))
                        case "false":
                            return Success(LiteralParameter(value=False))
                        case _:
                            return Failure(
                                ValidationError(
                                    "Invalid value; enter true or false.",
                                    input=raw_input,
                                )
                            )
                case "float":
                    return Success(LiteralParameter(value=float(raw_input)))
            return Failure(ValidationError(f"Unsupported Type: {parameter_type}"))
        except ValueError as e:
            return Failure(
                ValidationError(
                    f"fail to convert into type={parameter_type}", input=raw_input
                ).chain(e)
            )


def _build_direct_interaction_request(
    parameter_context: DefaultPrimitiveLiteralTypeParameterContext,
) -> Result[
    InteractionRequest[
        str, Path, DefaultPrimitiveLiteralTypeParameterContext, Parameter
    ],
    GyomuError,
]:
    return Success(
        InteractionDirectRequest[
            str, DefaultPrimitiveLiteralTypeParameterContext, Parameter
        ](
            instruction=(
                "Please define your type parameter for "
                f"({parameter_context.model_symbol_id}) \n"
                f"{parameter_context.parameter.parameter.name}:"
                f"{parameter_context.parameter.parameter.parameter_type.text}"
            ),
            context=parameter_context,
            input_mode=InputMode.DIRECT,
            codec=PrimitiveValueCodec(),
        )
    )


def define_direct_parameter(
    parameter_context: DefaultPrimitiveLiteralTypeParameterContext,
    interaction: InteractionExecutor[str, Path],
) -> Result[ResolvedParameterDefault, GyomuError]:
    request_result = _build_direct_interaction_request(
        parameter_context=parameter_context
    )
    if isinstance(request_result, Failure):
        return request_result
    request = request_result.unwrap()
    interaction_result = interaction.execute(request=request)
    if isinstance(interaction_result, Failure):
        return interaction_result
    result = interaction_result.unwrap()
    if isinstance(result, InteractionCancelled):
        return Failure(
            GyomuError(
                "parameter was not defined by user",
                operation="test",
                domain="test",
                reason="external_failure",
            )
        )

    type_parameter_result = configure_primitive_literal_type_parameter_default(
        parameter_context=parameter_context,
        interaction=interaction,
        parameter=result.value,
    )
    if isinstance(type_parameter_result, Failure):
        return type_parameter_result

    return Success(
        ResolvedParameterDefault(
            parameter=parameter_context.parameter.parameter, default=result.value
        )
    )
