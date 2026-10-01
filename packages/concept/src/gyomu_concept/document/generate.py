from pathlib import Path

from gyomu_concept.document.builder.section import build_sections
from gyomu_concept.document.models import DocumentDefinition
from gyomu_concept.document.translation.document import TranslatedDocument
from gyomu_concept.document.translation.section import translate_section
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_infra.filesystem.file_io import write_json, write_text
from gyomu_infra.logger import logger
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.document.section import BuiltSection, Section
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success


async def generate_document[
    TSectionId: str,
    TContext: DocumentBaseContext,
    TOption: ConceptOption,
    TRendererOption,
](
    definition: DocumentDefinition[TSectionId, TContext, TOption, TRendererOption],
    project: ProjectContext,
    option: TOption,
) -> Result[None, DocumentBuilderError]:
    caller = caller_context()
    context_result = definition.create_context(project, option)
    if isinstance(context_result, Failure):
        return context_result
    context = context_result.unwrap()

    sections_result = build_sections(context, definition.section_builders, option)
    if isinstance(sections_result, Failure):
        return sections_result
    sections = sections_result.unwrap()

    if (
        option is not None
        and option.debug_info is not None
        and definition.is_scope_of_debug(option)
    ):
        if option.debug_info.dump_to_file:
            write_json(
                Path("log") / f"{definition.log_prefix}Sections.json",
                sections,
                tuple[BuiltSection, ...],
            )
        else:
            logger.debug_object(sections, depth=6)

    for language in definition.supported_languages:
        translated_sections: list[Section] = []
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
