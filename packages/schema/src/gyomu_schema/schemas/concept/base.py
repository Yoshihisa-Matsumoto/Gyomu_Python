from pydantic import BaseModel

from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from gyomu_schema.schemas.knowledge.development import Development
from gyomu_schema.schemas.knowledge.package import Package
from gyomu_schema.schemas.knowledge.roadmap import Roadmap
from gyomu_schema.schemas.knowledge.technical import Technical


class Knowledge(BaseModel):
    package: Package
    technical: Technical
    development: Development
    roadmap: Roadmap | None


class DocumentBaseContext(BaseModel):
    analysis: PackageAnalysis
    concept: PackageConcept
    knowledge: Knowledge
