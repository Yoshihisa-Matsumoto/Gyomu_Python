from gyomu_ai_compiler.pipelines.package_concept.context.input import (
    PackageConceptInput,
)
from gyomu_ai_compiler.pipelines.package_concept.renderer.input import (
    build_package_concept_input,
)
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.utility.serialization import dump_json


def render_package_analysis(context: PackageAnalysis) -> str:
    input = build_package_concept_input(context=context)
    return dump_json(value=input, model_type=PackageConceptInput)
