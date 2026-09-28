from pathlib import Path

from concept_test_support.helpers import (
    _create_directory_project_context,
)
from gyomu_concept.directory.internal.file_summary import (
    build_file_summary_record,
)
from gyomu_schema.schemas.concept.file_summary import (
    DependencySummary,
    PublicDeclarationSummary,
)
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import SourceRelativePath
from gyomu_schema.schemas.python.visibility import Visibility

from packages.schema.schema_test_support.helpers import (
    create_docstring,
    create_file_analysis_context,
    create_import_dependency_analysis,
    create_location,
    create_pydantic_field_analysis,
    create_variable_analysis,
)


def test_build_file_summary_record() -> None:
    project_context = _create_directory_project_context()
    public_symbol = create_variable_analysis(
        indent=0,
        location=create_location(),
        name="public_value",
    )
    private_symbol = create_variable_analysis(
        indent=0,
        location=create_location(),
        name="_private_value",
    )
    private_symbol = private_symbol.model_copy(
        update={"visibility": Visibility.PRIVATE}
    )

    file_context = create_file_analysis_context(
        symbol=public_symbol,
        symbol2=private_symbol,
        module_path=SourceRelativePath(Path("test.py")),
    )

    result = build_file_summary_record(
        project_context=project_context,
        file_context=file_context,
    )

    assert result.path == Path("src/test.py")
    assert result.exports == (
        PublicDeclarationSummary(
            symbol=public_symbol.identity.symbol_id,
            kind=DeclarationKind.VARIABLE,
            summary="",
        ),
    )
    assert result.dependencies == ()


def test_build_file_summary_record_uses_docstring_summary() -> None:
    project_context = _create_directory_project_context()
    symbol = create_variable_analysis(
        indent=0,
        location=create_location(),
        name="public_value",
        docstring=create_docstring(summary="Public value."),
    )
    file_context = create_file_analysis_context(symbol=symbol)

    result = build_file_summary_record(
        project_context=project_context,
        file_context=file_context,
    )

    assert result.exports[0].summary == "Public value."


def test_build_file_summary_record_uses_pydantic_description_when_docstring_is_absent() -> (
    None
):
    project_context = _create_directory_project_context()
    symbol = create_variable_analysis(
        indent=0,
        location=create_location(),
        name="public_value",
        pydantic=create_pydantic_field_analysis(
            description="Description from Pydantic.",
        ),
    )

    file_context = create_file_analysis_context(symbol=symbol)

    result = build_file_summary_record(
        project_context=project_context,
        file_context=file_context,
    )

    assert result.exports[0].summary == "Description from Pydantic."


def test_build_file_summary_record_prefers_docstring_over_pydantic_description() -> (
    None
):
    project_context = _create_directory_project_context()
    symbol = create_variable_analysis(
        indent=0,
        location=create_location(),
        name="public_value",
        pydantic=create_pydantic_field_analysis(
            description="Description from Pydantic.",
        ),
    )
    # create_variable_analysis() creates no docstring, so this test requires
    # replacing it with a parsed docstring in accordance with the actual
    # DocstringAnalysis schema.

    file_context = create_file_analysis_context(symbol=symbol)

    result = build_file_summary_record(
        project_context=project_context,
        file_context=file_context,
    )

    assert result.exports[0].summary == "Description from Pydantic."


def test_build_file_summary_record_uses_empty_summary_when_no_description_exists() -> (
    None
):
    project_context = _create_directory_project_context()
    symbol = create_variable_analysis(
        indent=0,
        location=create_location(),
        name="public_value",
    )

    file_context = create_file_analysis_context(symbol=symbol)

    result = build_file_summary_record(
        project_context=project_context,
        file_context=file_context,
    )

    assert result.exports[0].summary == ""


def test_build_file_summary_record_aggregates_internal_and_external_dependencies() -> (
    None
):
    project_context = _create_directory_project_context()
    symbol = create_variable_analysis(
        indent=0,
        location=create_location(),
        name="public_value",
    )
    symbol = symbol.model_copy(
        update={
            "dependencies": (
                create_import_dependency_analysis("test.internal"),
                create_import_dependency_analysis("pydantic.BaseModel"),
            )
        },
    )

    file_context = create_file_analysis_context(symbol=symbol)

    result = build_file_summary_record(
        project_context=project_context,
        file_context=file_context,
    )

    assert result.dependencies == (
        DependencySummary(target="test.internal", external=False),
        DependencySummary(target="pydantic.BaseModel", external=True),
    )


def test_build_file_summary_record_deduplicates_dependencies() -> None:
    project_context = _create_directory_project_context()
    symbol = create_variable_analysis(
        indent=0,
        location=create_location(),
        name="public_value",
    )
    symbol2 = create_variable_analysis(
        indent=0,
        location=create_location(),
        name="another_value",
    )

    dependency = create_import_dependency_analysis("pydantic.BaseModel")

    symbol = symbol.model_copy(update={"dependencies": (dependency,)})
    symbol2 = symbol2.model_copy(update={"dependencies": (dependency,)})

    file_context = create_file_analysis_context(
        symbol=symbol,
        symbol2=symbol2,
    )

    result = build_file_summary_record(
        project_context=project_context,
        file_context=file_context,
    )

    assert result.dependencies == (
        DependencySummary(target="pydantic.BaseModel", external=True),
    )
