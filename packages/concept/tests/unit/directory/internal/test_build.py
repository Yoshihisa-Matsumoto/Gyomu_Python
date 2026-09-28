from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from gyomu_concept.directory.internal.build import (
    build_directory_concept_from_path,
)
from gyomu_concept.directory.types import BuildResult
from gyomu_concept.error.concept import ConceptError
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.concept.directory.concept import (
    DirectoryConcept,
    DirectoryImportance,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import create_file_summary


def create_context(
    project_root: Path,
    included_files: frozenset[ProjectRelativePath],
) -> ProjectContext:
    context = Mock(spec=ProjectContext)
    context.project_root = project_root
    context.included_files = included_files

    config = Mock()
    config.name = "test-package"
    context.config = config

    return context


def create_concept(summary: str = "test concept") -> DirectoryConcept:
    return DirectoryConcept(
        summary=summary,
        responsibilities=["test"],
        concepts=["test"],
        relationships=["test"],
        design_decisions=["test"],
        importance=DirectoryImportance.SUPPORTING,
    )


class TestBuildDirectoryConceptFromPath:
    @pytest.mark.asyncio
    async def test_returns_cached_concept(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        target_directory = tmp_path / "src"
        target_directory.mkdir()

        context = create_context(
            project_root=tmp_path,
            included_files=frozenset(),
        )

        concept = create_concept("cached")

        load = mocker.patch(
            "gyomu_concept.directory.internal.build.load_directory_concept",
            return_value=Success(concept),
        )
        process = mocker.patch(
            "gyomu_concept.directory.internal.build.process_directory_concept",
            new_callable=AsyncMock,
        )
        save = mocker.patch(
            "gyomu_concept.directory.internal.build.save_directory_concept",
        )

        result = await build_directory_concept_from_path(
            context=context,
            target_directory=FullPath(target_directory),
        )

        assert isinstance(result, Success)
        assert result.unwrap() == BuildResult(
            concept=concept,
            changed=False,
        )

        load.assert_called_once()
        process.assert_not_awaited()
        save.assert_not_called()

    @pytest.mark.asyncio
    async def test_generates_and_saves_when_cache_is_missing(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        target_directory = tmp_path / "src"
        target_directory.mkdir()

        context = create_context(
            project_root=tmp_path,
            included_files=frozenset(),
        )

        concept = create_concept("generated")

        mocker.patch(
            "gyomu_concept.directory.internal.build.load_directory_concept",
            return_value=Success(None),
        )
        process = mocker.patch(
            "gyomu_concept.directory.internal.build.process_directory_concept",
            new_callable=AsyncMock,
            return_value=Success(concept),
        )
        save = mocker.patch(
            "gyomu_concept.directory.internal.build.save_directory_concept",
            return_value=Success(None),
        )

        result = await build_directory_concept_from_path(
            context=context,
            target_directory=FullPath(target_directory),
        )

        assert isinstance(result, Success)
        assert result.unwrap() == BuildResult(
            concept=concept,
            changed=False,
        )

        process.assert_awaited_once()
        save.assert_called_once()

    @pytest.mark.asyncio
    async def test_rebuilds_when_directory_is_changed(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        target_directory = tmp_path / "src"
        target_directory.mkdir()

        context = create_context(
            project_root=tmp_path,
            included_files=frozenset(),
        )

        concept = create_concept("regenerated")

        mocker.patch(
            "gyomu_concept.directory.internal.build._is_directory_changed",
            return_value=True,
        )
        load = mocker.patch(
            "gyomu_concept.directory.internal.build.load_directory_concept",
            return_value=Success(create_concept("cached")),
        )
        process = mocker.patch(
            "gyomu_concept.directory.internal.build.process_directory_concept",
            new_callable=AsyncMock,
            return_value=Success(concept),
        )
        save = mocker.patch(
            "gyomu_concept.directory.internal.build.save_directory_concept",
            return_value=Success(None),
        )

        result = await build_directory_concept_from_path(
            context=context,
            target_directory=FullPath(target_directory),
        )

        assert isinstance(result, Success)
        assert result.unwrap() == BuildResult(
            concept=concept,
            changed=True,
        )

        load.assert_not_called()
        process.assert_awaited_once()
        save.assert_called_once()

    @pytest.mark.asyncio
    async def test_includes_only_included_files(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        target_directory = tmp_path / "src"
        target_directory.mkdir()

        included_file = target_directory / "included.py"
        excluded_file = target_directory / "excluded.py"

        included_file.write_text("")
        excluded_file.write_text("")

        included_path = ProjectRelativePath(included_file.relative_to(tmp_path))

        context = create_context(
            project_root=tmp_path,
            included_files=frozenset({included_path}),
        )

        file_context = Mock()
        file_summary = create_file_summary(
            path=included_path,
            exports=(),
            dependencies=(),
        )

        mocker.patch(
            "gyomu_concept.directory.internal.build.load_directory_concept",
            return_value=Success(None),
        )
        load_analysis = mocker.patch(
            "gyomu_concept.directory.internal.build.load_file_analysis_context",
            return_value=Success(file_context),
        )
        build_summary = mocker.patch(
            "gyomu_concept.directory.internal.build.build_file_summary_record",
            return_value=file_summary,
        )
        mocker.patch(
            "gyomu_concept.directory.internal.build.process_directory_concept",
            new_callable=AsyncMock,
            return_value=Success(create_concept()),
        )
        mocker.patch(
            "gyomu_concept.directory.internal.build.save_directory_concept",
            return_value=Success(None),
        )

        result = await build_directory_concept_from_path(
            context=context,
            target_directory=FullPath(target_directory),
        )

        assert isinstance(result, Success)

        load_analysis.assert_called_once_with(
            context=context,
            file_path=included_path,
        )
        build_summary.assert_called_once_with(
            project_context=context,
            file_context=file_context,
        )

    @pytest.mark.asyncio
    async def test_propagates_child_failure(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        target_directory = tmp_path / "src"
        child_directory = target_directory / "child"

        target_directory.mkdir()
        child_directory.mkdir()

        context = create_context(
            project_root=tmp_path,
            included_files=frozenset(),
        )

        error = ConceptError(
            message="child failed",
            file_path=ProjectRelativePath(child_directory.relative_to(tmp_path)),
            package_name="test-package",
            phase="directory-summary",
            identity=None,
        )

        mocker.patch(
            "gyomu_concept.directory.internal.build.load_directory_concept",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_concept.directory.internal.build.process_directory_concept",
            new_callable=AsyncMock,
            return_value=Failure(error),
        )

        result = await build_directory_concept_from_path(
            context=context,
            target_directory=FullPath(target_directory),
        )

        assert isinstance(result, Failure)
        assert result.failure() == error

    @pytest.mark.asyncio
    async def test_propagates_file_analysis_failure(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        target_directory = tmp_path / "src"
        target_directory.mkdir()

        source_file = target_directory / "example.py"
        source_file.write_text("")

        file_path = ProjectRelativePath(source_file.relative_to(tmp_path))

        context = create_context(
            project_root=tmp_path,
            included_files=frozenset({file_path}),
        )

        analysis_error = AnalysisError(
            message="test", file_path=FullPath(tmp_path), phase="analysis"
        )

        mocker.patch(
            "gyomu_concept.directory.internal.build.load_directory_concept",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_concept.directory.internal.build.load_file_analysis_context",
            return_value=Failure(analysis_error),
        )

        result = await build_directory_concept_from_path(
            context=context,
            target_directory=FullPath(target_directory),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, ConceptError)
        assert error.message == "fail to load file analysis context"
        assert error.file_path == file_path
        assert error.package_name == "test-package"
        assert error.phase == "directory-summary"
        assert error.identity is None

    @pytest.mark.asyncio
    async def test_propagates_generation_failure(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        target_directory = tmp_path / "src"
        target_directory.mkdir()

        context = create_context(
            project_root=tmp_path,
            included_files=frozenset(),
        )

        error = ConceptError(
            message="generation failed",
            file_path=ProjectRelativePath(Path("src")),
            package_name="test-package",
            phase="directory-summary",
            identity=None,
        )

        mocker.patch(
            "gyomu_concept.directory.internal.build.load_directory_concept",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_concept.directory.internal.build.process_directory_concept",
            new_callable=AsyncMock,
            return_value=Failure(error),
        )
        save = mocker.patch(
            "gyomu_concept.directory.internal.build.save_directory_concept",
        )

        result = await build_directory_concept_from_path(
            context=context,
            target_directory=FullPath(target_directory),
        )

        assert isinstance(result, Failure)
        assert result.failure() == error
        save.assert_not_called()

    @pytest.mark.asyncio
    async def test_propagates_save_failure(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        target_directory = tmp_path / "src"
        target_directory.mkdir()

        context = create_context(
            project_root=tmp_path,
            included_files=frozenset(),
        )

        concept = create_concept("generated")

        error = ConceptError(
            message="save failed",
            file_path=ProjectRelativePath(Path("src")),
            package_name="test-package",
            phase="directory-summary",
            identity=None,
        )

        mocker.patch(
            "gyomu_concept.directory.internal.build.load_directory_concept",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_concept.directory.internal.build.process_directory_concept",
            new_callable=AsyncMock,
            return_value=Success(concept),
        )
        mocker.patch(
            "gyomu_concept.directory.internal.build.save_directory_concept",
            return_value=Failure(error),
        )

        result = await build_directory_concept_from_path(
            context=context,
            target_directory=FullPath(target_directory),
        )

        assert isinstance(result, Failure)
        assert result.failure() == error
