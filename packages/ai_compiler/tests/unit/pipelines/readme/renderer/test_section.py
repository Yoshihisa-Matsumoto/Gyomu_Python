from gyomu_ai_compiler.pipelines.readme.renderer.architecture import (
    build_architecture_messages,
)
from gyomu_ai_compiler.pipelines.readme.renderer.dependencies import (
    build_dependencies_messages,
)
from gyomu_ai_compiler.pipelines.readme.renderer.development import (
    build_development_messages,
)
from gyomu_ai_compiler.pipelines.readme.renderer.overview import (
    build_overview_messages,
)
from gyomu_ai_compiler.pipelines.readme.renderer.section import (
    README_SECTION_PROMPT_MAP,
)


def test_readme_llm_section_prompt_map() -> None:
    assert {
        "overview": build_overview_messages,
        "architecture": build_architecture_messages,
        "dependencies": build_dependencies_messages,
        "development": build_development_messages,
    } == README_SECTION_PROMPT_MAP
