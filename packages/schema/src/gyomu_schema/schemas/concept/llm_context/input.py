from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
from gyomu_schema.schemas.knowledge.coding_guideline import CodingGuideline


class LlmKnowledge(Knowledge):
    coding_guideline: CodingGuideline


class LlmContextBuildContext(DocumentBaseContext[LlmKnowledge]):
    pass
