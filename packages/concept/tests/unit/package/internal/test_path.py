import pytest
from gyomu_concept.package.internal.path import get_package_concept_path
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptActionOption, ConceptOption

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
        result = get_package_concept_path(context=context)

        assert result == context.project_root / ".gyomu" / "concept" / "$Package.json"

    def test_returns_cache_path_when_write_to_temp_folder(
        self,
        context: ProjectContext,
    ) -> None:
        option = ConceptOption(
            action=ConceptActionOption(
                write_to_temp_folder=True,
            )
        )

        result = get_package_concept_path(
            context=context,
            option=option,
        )

        assert result == context.project_root / ".gyomu" / "cache" / "$Package.json"
