from gyomu_schema.schemas.concept.llm_context.input import (
    LlmContextBuildContext,
    LlmKnowledge,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import (
    create_llm_context_build_context,
    create_llm_knowledge,
)


class TestLlmKnowledge:
    def test(self) -> None:
        _assert_json_round_trip(LlmKnowledge, create_llm_knowledge())


class TestLlmContextBuildContext:
    def test(self) -> None:
        _assert_json_round_trip(
            LlmContextBuildContext, create_llm_context_build_context()
        )
