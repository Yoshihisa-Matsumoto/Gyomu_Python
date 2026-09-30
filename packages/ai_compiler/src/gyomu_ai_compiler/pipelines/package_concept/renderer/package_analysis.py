from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.utility.serialization import dump_json

from gyomu_ai_compiler.pipelines.package_concept.context.input import (
    PackageConceptInput,
)
from gyomu_ai_compiler.pipelines.package_concept.renderer.input import (
    build_package_concept_input,
)


def render_package_analysis(context: PackageAnalysis) -> str:
    """Render package analysis context into a JSON string.

    Renders package analysis context into a serialized PackageConceptInput JSON string.

    Args:
        context (PackageAnalysis): The package analysis context to render.

    Returns:
        str: JSON string representation of the package concept input.
    """
    input = build_package_concept_input(context=context)
    return dump_json(value=input, model_type=PackageConceptInput)
