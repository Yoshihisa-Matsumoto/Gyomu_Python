# from gyomu_schema.conversation.message import MessageRole, MessageSchema
# from openai.types.chat import ChatCompletionMessageParam


# def build_prompt(messages: list[MessageSchema]) -> list[ChatCompletionMessageParam]:
#     if not messages:
#         raise ValueError("messages must not be empty")
#     result: list[ChatCompletionMessageParam] = []
#     for message in messages:
#         match message.role:
#             case MessageRole.system:
#                 result.append(
#                     {
#                         "role": "system",
#                         "content": message.content,
#                     }
#                 )
#             case MessageRole.user:
#                 result.append(
#                     {
#                         "role": "user",
#                         "content": message.content,
#                     }
#                 )
#             case MessageRole.assistant:
#                 result.append(
#                     {
#                         "role": "assistant",
#                         "content": message.content,
#                     }
#                 )

#     return result
