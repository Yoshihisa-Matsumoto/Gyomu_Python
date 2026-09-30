from gyomu_concept.error.concept import ConceptError
from gyomu_concept.package.internal.save import save_package_concept
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)
from packages.schema.schema_test_support.concept_helpers import (
    create_capability_concept,
    create_package_concept,
)


def test_save_package_concept_success(
    mocker,
) -> None:
    context = _create_directory_project_context()
    concept = create_package_concept(
        summary="Example package.",
        responsibilities=["Provide example functionality."],
        capabilities=[create_capability_concept()],
        usage_guidance=["usage guidance"],
        design_decisions=["design decision"],
    )
    concept_path = context.project_root / ".gyomu" / "concept" / "$Package.json"

    mocker.patch(
        "gyomu_concept.package.internal.save.get_package_concept_path",
        return_value=concept_path,
    )
    write_json = mocker.patch(
        "gyomu_concept.package.internal.save.write_json",
        return_value=Success(None),
    )

    result = save_package_concept(
        context=context,
        concept=concept,
    )

    assert result == Success(None)
    write_json.assert_called_once_with(
        path=concept_path,
        value_type=PackageConcept,
        value=concept,
    )


def test_save_package_concept_failure(
    mocker,
) -> None:
    context = _create_directory_project_context()
    concept = create_package_concept(
        summary="Example package.",
        responsibilities=["Provide example functionality."],
        capabilities=[create_capability_concept()],
        usage_guidance=["usage guidance"],
        design_decisions=["design decision"],
    )
    concept_path = context.project_root / ".gyomu" / "concept" / "$Package.json"
    io_error = GyomuIOError(
        message="failed to write",
        layer=IOLayer.FILESYSTEM,
        operation=IOOperation.WRITE,
    )

    mocker.patch(
        "gyomu_concept.package.internal.save.get_package_concept_path",
        return_value=concept_path,
    )
    mocker.patch(
        "gyomu_concept.package.internal.save.write_json",
        return_value=Failure(io_error),
    )

    result = save_package_concept(
        context=context,
        concept=concept,
    )

    assert isinstance(result, Failure)

    error = result.failure()
    assert isinstance(error, ConceptError)
    assert error.message == "fail to save Package Concept"
    assert error.file_path == concept_path
    assert error.package_name == context.config.name
    assert error.phase == "package-concept"
    assert error.identity is None
    assert error.__cause__ is io_error
