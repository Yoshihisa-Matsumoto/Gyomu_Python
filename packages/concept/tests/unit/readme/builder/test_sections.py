from gyomu_concept.readme.builder.section.architecture import build_architecture
from gyomu_concept.readme.builder.section.development import build_development
from gyomu_concept.readme.builder.section.license import build_license
from gyomu_concept.readme.builder.section.overview import build_overview
from gyomu_concept.readme.builder.section.public_api import build_public_api
from gyomu_concept.readme.builder.sections import README_SECTION_BUILDERS


def test_readme_section_builder_map() -> None:
    assert (
        build_overview,  # paragraph + AI
        build_architecture,  # paragraph + AI
        build_license,  # paragraph + code
        build_development,  # paragraph + AI
        build_development,  # paragraph + AI
        build_public_api,  # bullet-list
        build_license,  # paragraph
    ) == README_SECTION_BUILDERS
