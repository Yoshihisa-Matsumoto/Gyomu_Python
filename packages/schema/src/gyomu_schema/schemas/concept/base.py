from pydantic import BaseModel

from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from gyomu_schema.schemas.knowledge.development import Development
from gyomu_schema.schemas.knowledge.package import Package
from gyomu_schema.schemas.knowledge.roadmap import Roadmap
from gyomu_schema.schemas.knowledge.technical import Technical


class Knowledge(BaseModel):
    """Defines knowledge information containing package, technical, development, and
    roadmap details.
    """

    package: Package
    """Package knowledge details."""

    technical: Technical
    """Technical knowledge details."""

    development: Development
    """Development knowledge details."""

    roadmap: Roadmap | None
    """Roadmap details, if available."""


class DocumentBaseContext[KnowledgeT: Knowledge](BaseModel):
    """Defines base context for documentation containing analysis, concept, and
    knowledge.
    """

    analysis: PackageAnalysis
    """Package analysis details."""

    concept: PackageConcept
    """Package concept details."""

    knowledge: KnowledgeT
    """Knowledge details."""
