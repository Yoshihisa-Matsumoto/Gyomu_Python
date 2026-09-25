from gyomu_ai.execution.context import AiExecutionContext
from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.ai import AiError
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.utility.serialization import dump_json
from returns.result import Failure, Result

from gyomu_ai_compiler.pipelines.docstring_update import DocstringRouteId
from gyomu_ai_compiler.pipelines.docstring_update.context.file_context import (
    DocstringFileContext,
)
from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DocstringUpdatePlan,
)
from gyomu_ai_compiler.prompts.load import (
    load_docstring_update_base_prompt,
)


async def generate_docstring_update_plan(
    context: DocstringFileContext,
) -> Result[DocstringUpdatePlan, GyomuIOError | AiError]:
    prompt = load_docstring_update_base_prompt()
    if isinstance(prompt, Failure):
        return prompt

    conversation = ConversationSchema(
        system=MessageSchema.system_text(prompt.unwrap())
    ).with_request(
        MessageSchema.user_text(
            dump_json(context, indent=2, model_type=DocstringFileContext)
        )
    )

    # try:
    #     registry = create_default_pydantic_ai_model_registry()
    # except Exception as e:
    #     return Failure(
    #         AiError(
    #             "fail to load key setting",
    #             operation=AiOperation.GENERATE,
    #             model_key=None,
    #             model=None,
    #             phase=AiErrorPhase.REQUEST,
    #             resolution=AiFailResolution(),
    #         ).chain(e)
    #     )
    execution = PydanticAiRoutingExecution(route_id=DocstringRouteId)

    result = await execution.generate_object(
        conversation,
        GenerateObjectParams(
            key=AiModelKey.FAST,
            output_type=DocstringUpdatePlan,
            execution=AiExecutionContext(),
        ),
    )

    return result.map(lambda response: response.output)
