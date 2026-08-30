from dataclasses import dataclass
from typing import Any

from gyomu_ai.provider.pydantic_ai.map_tool import to_pydantic_ai_tool
from gyomu_ai.tool.ai_tool import AiTool, ToolResult
from pydantic import BaseModel


class SearchFileInput(BaseModel):
    path: str
    pattern: str
    recursive: bool = True


@dataclass(frozen=True)
class SearchFileConfig(BaseModel):
    allowed_root: str


class TestToPydanticAiTool:
    def _create_tool(
        self,
    ) -> AiTool[
        SearchFileInput,
        Any,
        SearchFileConfig,
    ]:
        async def execute(
            input: SearchFileInput,
            config: SearchFileConfig | None,
        ) -> ToolResult[Any]:
            """Search files."""
            raise NotImplementedError

        return AiTool(
            name="search_file",
            description="Search files.",
            input_type=SearchFileInput,
            config=None,
            execute=execute,
        )

    def test_maps_name(self) -> None:
        tool = self._create_tool()

        result = to_pydantic_ai_tool(tool)

        assert result.name == "search_file"

    def test_maps_description(self) -> None:
        tool = self._create_tool()

        result = to_pydantic_ai_tool(tool)

        assert result.description == "Search files."

    def test_creates_function_schema_from_input_type(self) -> None:
        tool = self._create_tool()

        result = to_pydantic_ai_tool(tool)

        schema = result.function_schema
        print(schema)
        print(schema.json_schema)

        assert schema.name == "search_file"
        assert schema.description == "Search files."

        assert schema.json_schema == {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                },
                "pattern": {
                    "type": "string",
                },
                "recursive": {
                    "type": "boolean",
                    "default": True,
                },
            },
            "required": [
                "path",
                "pattern",
            ],
            "title": "SearchFileInput",
        }

        assert schema.single_arg_name == "input"
        assert not schema.takes_ctx
        assert schema.is_async
