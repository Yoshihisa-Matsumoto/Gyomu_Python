from pathlib import Path

import pytest
from gyomu_concept.directory.internal.path import get_directory_concept_path
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptActionOption, ConceptOption
from gyomu_schema.schemas.python.types import ProjectRelativePath

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)


class TestGetPackageConceptPath:
    @pytest.fixture
    def context(self) -> ProjectContext:
        return _create_directory_project_context()

    def test_returns_concept_path(
        self,
        context: ProjectContext,
    ) -> None:
        result = get_directory_concept_path(
            context=context, target_directory=ProjectRelativePath(Path("test"))
        )

        assert (
            result
            == context.project_root / ".gyomu" / "concept" / "test" / "$Directory.json"
        )

    def test_returns_cache_path_when_write_to_temp_folder(
        self,
        context: ProjectContext,
    ) -> None:
        option = ConceptOption(
            action=ConceptActionOption(
                write_to_temp_folder=True,
            )
        )

        result = get_directory_concept_path(
            context=context,
            target_directory=ProjectRelativePath(Path("test")),
            option=option,
        )

        assert (
            result
            == context.project_root / ".gyomu" / "cache" / "test" / "$Directory.json"
        )
