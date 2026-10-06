from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.readme.builder.section.architecture import build_architecture
from gyomu_concept.readme.builder.section.dependencies import build_dependencies
from gyomu_concept.readme.builder.section.development import build_development
from gyomu_concept.readme.builder.section.license import build_license
from gyomu_concept.readme.builder.section.overview import build_overview
from gyomu_concept.readme.builder.section.public_api import build_public_api
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId

README_SECTION_BUILDERS: tuple[
    SectionBuilder[ReadmeSectionId, DocumentBaseContext], ...
] = (
    build_overview,  # paragraph + AI
    build_architecture,  # paragraph + AI
    build_license,  # paragraph + code
    build_development,  # paragraph + AI
    build_dependencies,  # paragraph + AI
    build_public_api,  # bullet-list
    build_license,  # paragraph
)
