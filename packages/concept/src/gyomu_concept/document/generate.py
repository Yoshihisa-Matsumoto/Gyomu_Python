from pathlib import Path

from gyomu_infra.filesystem.file_io import write_text
from gyomu_infra.logger import logger
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.document.section import Section
from gyomu_schema.utility.context import caller_context
from gyomu_schema.utility.fromatting import format_object
from returns.result import Failure, Result, Success

from gyomu_concept.document.builder.section import build_sections
from gyomu_concept.document.models import DocumentDefinition
from gyomu_concept.document.translation.document import TranslatedDocument
from gyomu_concept.document.translation.section import translate_section
from gyomu_concept.error.document import DocumentBuilderError


async def generate_document[
    TSectionId: str,
    TContext: DocumentBaseContext,
    TOption: ConceptOption,
    TRendererOption,
](
    definition: DocumentDefinition[TSectionId, TContext, TOption, TRendererOption],
    project: ProjectContext,
    option: TOption | None = None,
) -> Result[None, DocumentBuilderError]:
    """Generates documentation based on a provided document definition and project
    context.

    Args:
        definition (DocumentDefinition[TSectionId, TContext, TOption, TRendererOption]):
            Document definition containing builders, outputs, and options.
        project (ProjectContext): Project context for analysis and generation.
        option (TOption | None): Optional concept generation options.

    Returns:
        Result[None, DocumentBuilderError]: A Result indicating success with None or a
            DocumentBuilderError on failure.
    """
    caller = caller_context()
    context_result = definition.create_context(project, option)
    if isinstance(context_result, Failure):
        return context_result
    context = context_result.unwrap()

    sections_result = await build_sections(
        context=context, builders=definition.section_builders, option=option
    )
    if isinstance(sections_result, Failure):
        return sections_result
    sections = sections_result.unwrap()

    if (
        option is not None
        and option.debug_info is not None
        and definition.is_scope_of_debug(option)
    ):
        if option.debug_info.dump_to_file:
            write_text(
                Path("log") / f"{definition.log_prefix}Sections.json",
                format_object(sections, depth=10),
            )
        else:
            logger.debug_object(sections, depth=10)

    for language in definition.supported_languages:
        translated_sections: list[Section[TSectionId]] = []
        for section in sections:
            section_id = section.section.id
            translate_result = await translate_section(section, language, option)
            if isinstance(translate_result, Failure):
                error = translate_result.failure()
                return Failure(
                    DocumentBuilderError(
                        "fail to translate section",
                        phase="translate",
                        package_name=context.analysis.package.name,
                        section_id=section_id,
                        context=caller,
                    ).chain(error)
                )
            print(f"Section: {section_id}")
            print(format_object(translate_result.unwrap(), depth=10))
            translated_sections.append(translate_result.unwrap())

        translated_document = TranslatedDocument(
            language=language, sections=tuple(translated_sections)
        )
        render_output_result = definition.output.renderer.render(
            context, translated_document, option, definition.renderer_options
        )
        if isinstance(render_output_result, Failure):
            return render_output_result
        render_output = render_output_result.unwrap()

        output_file_path = definition.output.filepath_resolver.resolve(
            project, language
        )
        if render_output.type == "text":
            write_result = write_text(
                path=output_file_path, content=render_output.content
            )
            if isinstance(write_result, Failure):
                error = write_result.failure()
                return Failure(
                    DocumentBuilderError(
                        "fail to write file",
                        phase="export",
                        package_name=context.analysis.package.name,
                        file_path=output_file_path,
                        context=caller,
                    ).chain(error)
                )

    return Success(None)
