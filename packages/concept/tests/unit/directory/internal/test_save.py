from pathlib import Path

from gyomu_concept.directory.internal.save import save_directory_concept
from gyomu_concept.error.concept import ConceptError
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.concept.directory.concept import (
    DirectoryConcept,
    DirectoryImportance,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)
from packages.schema.schema_test_support.concept_helpers import (
    create_directory_concept,
)


def test_save_directory_concept_success(
    mocker,
) -> None:
    context = _create_directory_project_context()
    target_directory = ProjectRelativePath(Path("gyomu"))
    concept = create_directory_concept(
        summary="Test directory",
        responsibilities=["Test responsibility"],
        concepts=["Test concept"],
        relationships=["Test relationship"],
        design_decisions=["Test design decision"],
        importance=DirectoryImportance.CORE,
    )
    concept_path = context.project_root / ".gyomu" / "concept" / "gyomu.json"

    mocker.patch(
        "gyomu_concept.directory.internal.save.get_directory_concept_path",
        return_value=concept_path,
    )
    write_json = mocker.patch(
        "gyomu_concept.directory.internal.save.write_json",
        return_value=Success(None),
    )

    result = save_directory_concept(
        context=context,
        target_directory=target_directory,
        concept=concept,
    )

    assert result == Success(None)
    write_json.assert_called_once_with(
        path=concept_path,
        value_type=DirectoryConcept,
        value=concept,
    )


def test_save_directory_concept_failure(
    mocker,
) -> None:
    context = _create_directory_project_context()
    target_directory = ProjectRelativePath(Path("gyomu"))
    concept = create_directory_concept(
        summary="Test directory",
        responsibilities=["Test responsibility"],
        concepts=["Test concept"],
        relationships=["Test relationship"],
        design_decisions=["Test design decision"],
        importance=DirectoryImportance.CORE,
    )
    concept_path = context.project_root / ".gyomu" / "concept" / "gyomu.json"
    io_error = GyomuIOError(
        message="failed to write",
        layer=IOLayer.FILESYSTEM,
        operation=IOOperation.WRITE,
    )

    mocker.patch(
        "gyomu_concept.directory.internal.save.get_directory_concept_path",
        return_value=concept_path,
    )
    mocker.patch(
        "gyomu_concept.directory.internal.save.write_json",
        return_value=Failure(io_error),
    )

    result = save_directory_concept(
        context=context,
        target_directory=target_directory,
        concept=concept,
    )

    assert isinstance(result, Failure)

    error = result.failure()
    assert isinstance(error, ConceptError)
    assert error.message == "fail to save Directory Concept"
    assert error.file_path == target_directory
    assert error.package_name == context.config.name
    assert error.phase == "directory-summary"
    assert error.identity is None
    assert error.__cause__ is io_error
