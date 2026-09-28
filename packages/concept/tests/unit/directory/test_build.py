from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from gyomu_concept.directory.build import build_directory_concept
from gyomu_concept.directory.types import BuildResult, BuildRootResult
from gyomu_concept.error.concept import ConceptError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.directory.concept import (
    DirectoryConcept,
    DirectoryImportance,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success


def create_context(
    project_root: Path,
    source_root: ProjectRelativePath,
) -> Mock:
    context = Mock()
    context.project_root = project_root
    context.source_root = source_root
    context.package_roots = (source_root,)

    return context


def create_concept() -> DirectoryConcept:
    return DirectoryConcept(
        summary="test",
        responsibilities=["test"],
        concepts=["test"],
        relationships=["test"],
        design_decisions=["test"],
        importance=DirectoryImportance.SUPPORTING,
    )


class TestBuildDirectoryConcept:
    @pytest.mark.asyncio
    async def test_uses_source_root_when_target_folder_is_not_specified(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        source_root = ProjectRelativePath(Path("src"))

        context = create_context(
            project_root=tmp_path,
            source_root=source_root,
        )

        build_result = BuildResult(
            concept=create_concept(),
            changed=False,
        )

        build = mocker.patch(
            "gyomu_concept.directory.build.build_directory_concept_from_path",
            new_callable=AsyncMock,
            return_value=Success(build_result),
        )

        option = ConceptOption()

        result = await build_directory_concept(
            context=context,
            option=option,
        )

        assert result == Success(
            BuildRootResult(concepts=(build_result.concept,), changed=False)
        )

        build.assert_awaited_once_with(
            context,
            FullPath(tmp_path / source_root),
            option,
        )

    @pytest.mark.asyncio
    async def test_uses_target_folder_when_specified(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        source_root = ProjectRelativePath(Path("src"))

        context = create_context(
            project_root=tmp_path,
            source_root=source_root,
        )

        target_folder = ProjectRelativePath(Path("packages/foo"))

        option = ConceptOption(
            target_folder=target_folder,
        )

        build_result = BuildResult(
            concept=create_concept(),
            changed=True,
        )

        build = mocker.patch(
            "gyomu_concept.directory.build.build_directory_concept_from_path",
            new_callable=AsyncMock,
            return_value=Success(build_result),
        )

        result = await build_directory_concept(
            context=context,
            option=option,
        )

        assert result == Success(
            BuildRootResult(concepts=(build_result.concept,), changed=True)
        )

        build.assert_awaited_once_with(
            context,
            FullPath(tmp_path / target_folder),
            option,
        )

    @pytest.mark.asyncio
    async def test_propagates_failure(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        source_root = ProjectRelativePath(Path("src"))

        context = create_context(
            project_root=tmp_path,
            source_root=source_root,
        )

        error = ConceptError(
            message="failed to build directory concept",
            file_path=ProjectRelativePath(Path("src")),
            package_name="test-package",
            phase="directory-summary",
            identity=None,
        )

        mocker.patch(
            "gyomu_concept.directory.build.build_directory_concept_from_path",
            new_callable=AsyncMock,
            return_value=Failure(error),
        )

        result = await build_directory_concept(
            context=context,
        )

        assert result == Failure(error)

    @pytest.mark.asyncio
    async def test_uses_source_root_when_option_is_none(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        source_root = ProjectRelativePath(Path("src"))

        context = create_context(
            project_root=tmp_path,
            source_root=source_root,
        )

        build_result = BuildResult(
            concept=create_concept(),
            changed=False,
        )

        build = mocker.patch(
            "gyomu_concept.directory.build.build_directory_concept_from_path",
            new_callable=AsyncMock,
            return_value=Success(build_result),
        )

        result = await build_directory_concept(context=context)

        assert result == Success(
            BuildRootResult(
                concepts=(build_result.concept,), changed=build_result.changed
            )
        )

        build.assert_awaited_once_with(
            context,
            FullPath(tmp_path / source_root),
            None,
        )
