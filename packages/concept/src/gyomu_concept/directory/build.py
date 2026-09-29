from gyomu_concept.directory.internal.build import build_directory_concept_from_path
from gyomu_concept.directory.types import BuildRootResult
from gyomu_concept.error.concept import ConceptError
from gyomu_infra.logger import logger
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.fromatting import format_object
from returns.result import Failure, Result, Success


async def build_directory_concept(
    context: ProjectContext, option: ConceptOption | None = None
) -> Result[BuildRootResult, ConceptError]:
    root_path_items: tuple[FullPath, ...] = (
        (FullPath(context.project_root / option.target_folder),)
        if option is not None and option.target_folder is not None
        else tuple(
            FullPath(context.project_root / root) for root in context.package_roots
        )
    )
    is_changed = False
    concepts: list[DirectoryConcept] = []
    logger.debug(f"Directory Concept generation on {repr(root_path_items)}")
    logger.debug(repr(context.package_roots))
    if option is not None and option.changed_files is not None:
        logger.debug(f"Changed Files: {format_object(option.changed_files)}")
    else:
        logger.debug("No Changed Files Specified")
    for root_path in root_path_items:
        result = await build_directory_concept_from_path(context, root_path, option)
        if isinstance(result, Failure):
            return result

        item_result = result.unwrap()
        concepts.append(item_result.concept)

        if item_result.changed:
            is_changed = True

    return Success(BuildRootResult(concepts=tuple(concepts), changed=is_changed))
