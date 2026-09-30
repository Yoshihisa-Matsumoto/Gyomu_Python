from gyomu_ai_compiler.pipelines.package_concept.executor.generate import (
    generate_package_concept,
)
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Result

from gyomu_concept.error.concept import ConceptError


async def process_package_concept(
    package_name: str,
    package_path: ProjectRelativePath,
    context: PackageAnalysis,
) -> Result[PackageConcept, ConceptError]:
    """Processes and generates the package concept for a given package analysis context.

    Args:
        package_name (str): Name of the package being processed.
        package_path (ProjectRelativePath): Project-relative path of the package.
        context (PackageAnalysis): Package analysis context.

    Returns:
        Result[PackageConcept, ConceptError]: Result containing the generated
            PackageConcept or a ConceptError.
    """
    result = await generate_package_concept(context=context)
    return result.alt(
        lambda error: ConceptError(
            message="fail to generate Package Concept",
            file_path=package_path,
            package_name=package_name,
            phase="package-concept",
            identity=None,
            details=vars(context),
        ).chain(error)
    )
