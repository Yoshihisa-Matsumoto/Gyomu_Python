from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
from gyomu_schema.schemas.knowledge.coding_guideline import CodingGuideline


class LlmKnowledge(Knowledge):
    """Defines LLM knowledge containing a coding guideline.

    Represents LLM knowledge containing coding guidelines.
    """

    coding_guideline: CodingGuideline


class LlmContextBuildContext(DocumentBaseContext[LlmKnowledge]):
    """Defines the document build context for LLM knowledge.

    Represents the build context for LLM documents utilizing LlmKnowledge.
    """

    pass
