# from datetime import datetime

# import pytest
# from gyomu_ai.provider.instructor.build_prompt import build_prompt
# from gyomu_schema.conversation.message import MessageRole, MessageSchema


# class TestBuildPrompt:
#     def test_rejects_empty_messages(self) -> None:
#         with pytest.raises(
#             ValueError,
#             match="messages must not be empty",
#         ):
#             build_prompt([])

#     def test_builds_system_message(self) -> None:
#         message = MessageSchema(
#             id="1",
#             role=MessageRole.system,
#             content="You are a helpful assistant.",
#             created_at=datetime(2026, 8, 27, 10, 0, 0),
#         )

#         result = build_prompt([message])

#         assert result == [
#             {
#                 "role": "system",
#                 "content": "You are a helpful assistant.",
#             }
#         ]

#     def test_builds_user_message(self) -> None:
#         message = MessageSchema(
#             id="1",
#             role=MessageRole.user,
#             content="Hello",
#             created_at=datetime(2026, 8, 27, 10, 0, 0),
#         )

#         result = build_prompt([message])

#         assert result == [
#             {
#                 "role": "user",
#                 "content": "Hello",
#             }
#         ]

#     def test_builds_assistant_message(self) -> None:
#         message = MessageSchema(
#             id="1",
#             role=MessageRole.assistant,
#             content="Hello! How can I help you?",
#             created_at=datetime(2026, 8, 27, 10, 0, 0),
#         )

#         result = build_prompt([message])

#         assert result == [
#             {
#                 "role": "assistant",
#                 "content": "Hello! How can I help you?",
#             }
#         ]

#     def test_builds_multiple_messages(self) -> None:
#         messages = [
#             MessageSchema(
#                 id="1",
#                 role=MessageRole.system,
#                 content="You are a helpful assistant.",
#                 created_at=datetime(2026, 8, 27, 10, 0, 0),
#             ),
#             MessageSchema(
#                 id="2",
#                 role=MessageRole.user,
#                 content="Hello",
#                 created_at=datetime(2026, 8, 27, 10, 1, 0),
#             ),
#             MessageSchema(
#                 id="3",
#                 role=MessageRole.assistant,
#                 content="Hello! How can I help you?",
#                 created_at=datetime(2026, 8, 27, 10, 2, 0),
#             ),
#         ]

#         result = build_prompt(messages)

#         assert result == [
#             {
#                 "role": "system",
#                 "content": "You are a helpful assistant.",
#             },
#             {
#                 "role": "user",
#                 "content": "Hello",
#             },
#             {
#                 "role": "assistant",
#                 "content": "Hello! How can I help you?",
#             },
#         ]
