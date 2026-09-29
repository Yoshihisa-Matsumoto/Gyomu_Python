from pathlib import Path

from gyomu_concept.error.concept import ConceptError
from gyomu_concept.package.analysis import build_package_analysis
from gyomu_concept.package.internal.load import load_package_concept
from gyomu_concept.package.internal.process import process_package_concept
from gyomu_concept.package.internal.save import save_package_concept
from gyomu_infra.filesystem.file_io import write_json
from gyomu_infra.logger import logger
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from gyomu_schema.utility.fromatting import format_object
from returns.result import Failure, Result, Success


async def build_package_concept(
    context: ProjectContext, option: ConceptOption | None = None
) -> Result[PackageConcept, ConceptError]:
    if (
        option is not None
        and option.changed_files is not None
        and len(option.changed_files) == 0
    ):
        load_result = load_package_concept(context, option)
        if isinstance(load_result, Failure):
            logger.info(
                f"Error on load_package_concept.\n"
                f"Error:{format_object(load_result.failure(), depth=5)}"
            )
        else:
            concept = load_result.unwrap()
            if concept is not None:
                return Success(concept)

    analysis_result = build_package_analysis(context, option)
    if isinstance(analysis_result, Failure):
        return analysis_result
    analysis = analysis_result.unwrap()

    if option and option.debug_info and option.debug_info.package_analysis:
        if option.debug_info.dump_to_file:
            write_json(
                Path("log") / "PackageAnalysis.json",
                analysis,
                PackageAnalysis,
            )
        else:
            logger.debug_object(analysis, depth=6)

    generate_result = await process_package_concept(
        package_name=context.config.name,
        package_path=context.source_root,
        context=analysis,
    )
    if isinstance(generate_result, Failure):
        return generate_result
    concept = generate_result.unwrap()
    if option and option.debug_info and option.debug_info.package_concept:
        if option.debug_info.dump_to_file:
            write_json(
                Path("log") / "PackageConcept.json",
                concept,
                PackageConcept,
            )
        else:
            logger.debug_object(concept, depth=6)

    save_result = save_package_concept(context=context, concept=concept, option=option)
    if isinstance(save_result, Failure):
        return save_result

    return generate_result
