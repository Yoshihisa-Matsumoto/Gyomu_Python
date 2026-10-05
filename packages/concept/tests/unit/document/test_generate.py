from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from gyomu_concept.document.generate import generate_document
from gyomu_concept.document.models import (
    DocumentDefinition,
    DocumentOutput,
    FilepathResolver,
)
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.error.translation import TranslationError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.document.section import (
    BuiltSection,
    Section,
    SectionNoTranslation,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)
from packages.schema.schema_test_support.concept_helpers import (
    create_document_base_context,
)


@pytest.fixture
def project() -> ProjectContext:
    return _create_directory_project_context()


@pytest.mark.asyncio
async def test_generate_document(
    mocker: MockerFixture, project: ProjectContext
) -> None:
    sections = (
        BuiltSection(
            section=Section(
                id="overview",
                title="Overview",
                contents=(),
            ),
            translation=SectionNoTranslation(),
        ),
    )

    translated_section = Section(
        id="overview",
        title="Overview",
        contents=(),
    )

    renderer = mocker.Mock()
    renderer.render.return_value = Success(mocker.Mock(type="text", content="# README"))

    filepath_resolver = mocker.Mock()
    filepath_resolver.resolve.return_value = Path("README.md")

    definition = mocker.Mock(spec=DocumentDefinition)
    create_context = mocker.Mock(return_value=Success(False))
    is_scope_of_debug = mocker.Mock(return_value=False)
    output = mocker.Mock(spec=DocumentOutput)

    definition.create_context = create_context
    definition.section_builders = ()
    definition.supported_languages = ("en",)
    definition.is_scope_of_debug = is_scope_of_debug
    definition.output = output
    definition.output.renderer = renderer
    definition.output.filepath_resolver = filepath_resolver
    definition.renderer_options = mocker.Mock()
    definition.log_prefix = "README"

    option = ConceptOption()

    build_sections_mock = mocker.patch(
        "gyomu_concept.document.generate.build_sections",
        new_callable=AsyncMock,
        return_value=Success(sections),
    )

    translate_mock = mocker.patch(
        "gyomu_concept.document.generate.translate_section",
        new_callable=AsyncMock,
        return_value=Success(translated_section),
    )

    write_mock = mocker.patch(
        "gyomu_concept.document.generate.write_text",
        return_value=Success(None),
    )

    result = await generate_document(
        definition=definition,
        project=project,
        option=option,
    )

    assert isinstance(result, Success)
    assert result.unwrap() is None

    build_sections_mock.assert_awaited_once_with(
        context=False,
        builders=(),
        option=option,
    )

    translate_mock.assert_awaited_once_with(
        sections[0],
        "en",
        option,
    )

    filepath_resolver.resolve.assert_called_once_with(
        project,
        "en",
    )

    renderer.render.assert_called_once()

    write_mock.assert_called_once_with(
        path=Path("README.md"),
        content="# README",
    )


@pytest.mark.asyncio
async def test_generate_document_returns_context_error(
    mocker: MockerFixture,
) -> None:
    error = DocumentBuilderError(
        "fail to create context",
        phase="context-build",
    )

    definition = mocker.Mock(spec=DocumentDefinition)
    create_context = mocker.Mock(return_value=Failure(error))
    definition.create_context = create_context

    project = mocker.Mock(spec=ProjectContext)
    option = mocker.Mock(spec=ConceptOption)

    build_sections_mock = mocker.patch(
        "gyomu_concept.document.generate.build_sections",
        new_callable=AsyncMock,
    )

    result = await generate_document(
        definition=definition,
        project=project,
        option=option,
    )

    assert isinstance(result, Failure)
    assert result.failure() is error

    build_sections_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_document_returns_build_sections_error(
    mocker: MockerFixture,
) -> None:
    context = mocker.Mock(spec=DocumentBaseContext)

    error = DocumentBuilderError(
        "fail to build sections",
        phase="context-build",
    )

    definition = mocker.Mock(spec=DocumentDefinition)
    create_context = mocker.Mock(return_value=Success(context))

    definition.create_context = create_context
    definition.section_builders = ()

    build_sections_mock = mocker.patch(
        "gyomu_concept.document.generate.build_sections",
        new_callable=AsyncMock,
        return_value=Failure(error),
    )

    translate_mock = mocker.patch(
        "gyomu_concept.document.generate.translate_section",
        new_callable=AsyncMock,
    )

    result = await generate_document(
        definition=definition,
        project=mocker.Mock(spec=ProjectContext),
        option=mocker.Mock(spec=ConceptOption),
    )

    assert isinstance(result, Failure)
    assert result.failure() is error

    build_sections_mock.assert_awaited_once_with(
        context=context,
        builders=(),
        option=mocker.ANY,
    )

    translate_mock.assert_not_called()


@pytest.mark.asyncio
async def test_generate_document_wraps_translation_error(
    mocker: MockerFixture,
) -> None:
    context = create_document_base_context()

    section = mocker.Mock()
    section.section.id = "overview"

    translation_error = TranslationError(
        message="test",
        phase="translate",
        section_id="1",
        content_type="AB",
    )

    definition = mocker.Mock(spec=DocumentDefinition)
    create_context = mocker.Mock(return_value=Success(context))
    is_scope_of_debug = mocker.Mock(return_value=False)
    definition.is_scope_of_debug = is_scope_of_debug
    definition.create_context = create_context
    definition.section_builders = ()
    definition.supported_languages = ("en",)

    build_sections_mock = mocker.patch(
        "gyomu_concept.document.generate.build_sections",
        new_callable=AsyncMock,
        return_value=Success((section,)),
    )

    translate_mock = mocker.patch(
        "gyomu_concept.document.generate.translate_section",
        new_callable=AsyncMock,
        return_value=Failure(translation_error),
    )

    result = await generate_document(
        definition=definition,
        project=mocker.Mock(spec=ProjectContext),
        option=ConceptOption(),
    )

    assert isinstance(result, Failure)

    error = result.failure()

    assert isinstance(error, DocumentBuilderError)
    assert error.phase == "translate"
    assert error.section_id == "overview"
    assert error.__cause__ is translation_error

    build_sections_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_document_returns_renderer_error(
    mocker: MockerFixture,
) -> None:
    context = mocker.Mock(spec=DocumentBaseContext)

    section = mocker.Mock()
    translated_section = mocker.Mock(spec=Section)

    renderer_error = DocumentBuilderError(
        "fail to render",
        phase="render",
    )

    renderer = mocker.Mock()
    renderer.render.return_value = Failure(renderer_error)

    definition = mocker.Mock(spec=DocumentDefinition)
    create_context = mocker.Mock(return_value=Success(context))
    is_scope_of_debug = mocker.Mock(return_value=False)
    output = mocker.Mock(spec=DocumentOutput)
    definition.create_context = create_context
    definition.section_builders = ()
    definition.supported_languages = ("en",)
    definition.output = output
    definition.output.renderer = renderer
    definition.is_scope_of_debug = is_scope_of_debug
    definition.renderer_options = mocker.Mock()

    build_sections_mock = mocker.patch(
        "gyomu_concept.document.generate.build_sections",
        new_callable=AsyncMock,
        return_value=Success((section,)),
    )

    mocker.patch(
        "gyomu_concept.document.generate.translate_section",
        new_callable=AsyncMock,
        return_value=Success(translated_section),
    )

    write_mock = mocker.patch(
        "gyomu_concept.document.generate.write_text",
    )

    result = await generate_document(
        definition=definition,
        project=mocker.Mock(spec=ProjectContext),
        option=ConceptOption(),
    )

    assert isinstance(result, Failure)
    assert result.failure() is renderer_error

    build_sections_mock.assert_awaited_once()

    write_mock.assert_not_called()


@pytest.mark.asyncio
async def test_generate_document_wraps_write_error(
    mocker: MockerFixture,
    project: ProjectContext,
) -> None:
    context = create_document_base_context()

    section = mocker.Mock()
    translated_section = mocker.Mock(spec=Section)

    write_error = GyomuIOError(
        message="test",
        layer=IOLayer.FILESYSTEM,
        operation=IOOperation.WRITE,
    )

    renderer = mocker.Mock()
    renderer.render.return_value = Success(
        mocker.Mock(
            type="text",
            content="# README",
        )
    )

    definition = mocker.Mock(spec=DocumentDefinition)
    create_context = mocker.Mock(return_value=Success(context))
    is_scope_of_debug = mocker.Mock(return_value=False)
    output = mocker.Mock(spec=DocumentOutput)
    filepath_resolver = mocker.Mock(spec=FilepathResolver)
    definition.create_context = create_context
    definition.section_builders = ()
    definition.supported_languages = ("en",)
    definition.output = output
    definition.output.renderer = renderer
    definition.output.filepath_resolver = filepath_resolver
    definition.output.filepath_resolver.resolve = mocker.Mock(
        return_value=Path("README.md")
    )
    definition.is_scope_of_debug = is_scope_of_debug
    definition.renderer_options = mocker.Mock()

    build_sections_mock = mocker.patch(
        "gyomu_concept.document.generate.build_sections",
        new_callable=AsyncMock,
        return_value=Success((section,)),
    )

    mocker.patch(
        "gyomu_concept.document.generate.translate_section",
        new_callable=AsyncMock,
        return_value=Success(translated_section),
    )

    mocker.patch(
        "gyomu_concept.document.generate.write_text",
        return_value=Failure(write_error),
    )

    result = await generate_document(
        definition=definition,
        project=project,
        option=ConceptOption(),
    )

    assert isinstance(result, Failure)

    error = result.failure()

    assert isinstance(error, DocumentBuilderError)
    assert error.phase == "export"
    assert error.file_path == Path("README.md")
    assert error.__cause__ is write_error

    build_sections_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_document_generates_each_language(
    mocker: MockerFixture,
) -> None:
    context = create_document_base_context()
    section = mocker.Mock()
    translated_en = mocker.Mock(spec=Section)
    translated_ja = mocker.Mock(spec=Section)

    definition = mocker.Mock(spec=DocumentDefinition)
    create_context = mocker.Mock(return_value=Success(context))
    is_scope_of_debug = mocker.Mock(return_value=False)
    output = mocker.Mock(spec=DocumentOutput)
    filepath_resolver = mocker.Mock(spec=FilepathResolver)
    definition.create_context = create_context
    definition.section_builders = ()
    definition.supported_languages = ("en", "ja")
    definition.is_scope_of_debug = is_scope_of_debug
    definition.output = output
    definition.output.filepath_resolver = filepath_resolver
    definition.output.filepath_resolver.resolve = mocker.Mock(
        side_effect=[
            Path("README.md"),
            Path("README.ja.md"),
        ]
    )
    definition.renderer_options = mocker.Mock()

    build_sections_mock = mocker.patch(
        "gyomu_concept.document.generate.build_sections",
        new_callable=AsyncMock,
        return_value=Success((section,)),
    )

    translate_mock = mocker.patch(
        "gyomu_concept.document.generate.translate_section",
        new_callable=AsyncMock,
        side_effect=[
            Success(translated_en),
            Success(translated_ja),
        ],
    )

    renderer = mocker.Mock()
    renderer.render.side_effect = [
        Success(mocker.Mock(type="text", content="EN")),
        Success(mocker.Mock(type="text", content="JA")),
    ]
    definition.output.renderer = renderer

    write_mock = mocker.patch(
        "gyomu_concept.document.generate.write_text",
        return_value=Success(None),
    )

    result = await generate_document(
        definition=definition,
        project=mocker.Mock(spec=ProjectContext),
        option=ConceptOption(),
    )

    assert isinstance(result, Success)

    build_sections_mock.assert_awaited_once_with(
        context=context,
        builders=(),
        option=mocker.ANY,
    )

    assert translate_mock.await_count == 2

    first_call = translate_mock.await_args_list[0]
    second_call = translate_mock.await_args_list[1]

    assert first_call.args == (section, "en", mocker.ANY)
    assert second_call.args == (section, "ja", mocker.ANY)

    assert renderer.render.call_count == 2
    assert write_mock.call_count == 2
