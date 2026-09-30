from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from gyomu_concept.error.concept import ConceptError
from gyomu_concept.package.analysis import build_package_analysis
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceRootKind
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    create_monorepo_project_context,
)


@pytest.fixture
def project_a_context():
    return create_monorepo_project_context("project_a")


class TestBuildPackageAnalysis:
    def test(self, project_a_context: ProjectContext) -> None:
        result = build_package_analysis(context=project_a_context)

        assert isinstance(result, Success)

        analysis = result.unwrap()

        # package
        assert analysis.package.name == "project-a"
        assert analysis.package.version == "0.1.0"
        assert analysis.package.description == "Project A"
        assert analysis.package.license == "MIT"

        # dependencies
        dependencies = {
            (item.package_name, item.source): item for item in analysis.dependencies
        }

        assert dependencies[("project-b", "dependency")].kind == "workspace"
        assert dependencies[("project-b", "dependency")].required_version is None

        assert dependencies[("pydantic", "dependency")].kind == "version"
        assert dependencies[("pydantic", "dependency")].required_version == "<3,>=2"

        assert dependencies[("returns", "dependency")].kind == "version"
        assert dependencies[("returns", "dependency")].required_version == "<1,>=0.29.0"

        assert dependencies[("project-b", "devDependency")].kind == "workspace"
        assert dependencies[("project-b", "devDependency")].required_version is None

        assert dependencies[("pytest", "devDependency")].kind == "version"
        assert dependencies[("pytest", "devDependency")].required_version == ">=9"

        assert dependencies[("python-dotenv", "devDependency")].kind == "version"
        assert (
            dependencies[("python-dotenv", "devDependency")].required_version
            == "<2,>=1.2.3"
        )

        # directories
        directories = {item.path: item for item in analysis.directories}
        project_a_directory = directories[ProjectRelativePath(Path("src/project_a"))]
        assert project_a_directory.concept.summary == "Project A source package"
        assert project_a_directory.fact.file_count == 2
        assert project_a_directory.fact.total_symbol_count == 1
        assert project_a_directory.fact.public_symbol_count == 1

        submodule_directory = directories[
            ProjectRelativePath(Path("src/project_a/submodule"))
        ]
        assert submodule_directory.concept.summary == "Project A submodule"
        assert submodule_directory.fact.file_count == 2
        assert submodule_directory.fact.total_symbol_count == 16
        assert submodule_directory.fact.public_symbol_count == 6

        # public files
        public_files = {item.path: item for item in analysis.public_files}

        assert set(public_files) == {
            ProjectRelativePath(Path("src/project_a/__init__.py")),
            ProjectRelativePath(Path("src/project_a/module.py")),
            ProjectRelativePath(Path("src/project_a/submodule/__init__.py")),
            ProjectRelativePath(Path("src/project_a/submodule/service.py")),
        }

    def test_find_root_failure(
        self,
        project_a_context: ProjectContext,
    ) -> None:
        error = AnalysisError(
            "find root failed",
            file_path=FullPath(Path("/tmp/test.py")),
            phase="analysis",
        )

        with patch(
            "gyomu_concept.package.analysis.find_root",
            return_value=Failure(error),
        ):
            result = build_package_analysis(context=project_a_context)

        assert isinstance(result, Failure)

        concept_error = result.failure()
        assert concept_error.phase == "package-concept"
        assert concept_error.package_name == "project-a"
        assert concept_error.__cause__ is error

    def test_initialize_workspace_context_failure(
        self,
        project_a_context: ProjectContext,
    ) -> None:
        workspace = MagicMock()
        workspace.kind = WorkspaceRootKind.UV_WORKSPACE

        error = AnalysisError(
            "find root failed",
            file_path=FullPath(Path("/tmp/test.py")),
            phase="analysis",
        )

        with (
            patch(
                "gyomu_concept.package.analysis.find_root",
                return_value=Success(workspace),
            ),
            patch(
                "gyomu_concept.package.analysis.initialize_workspace_context",
                return_value=Failure(error),
            ),
        ):
            result = build_package_analysis(context=project_a_context)

        assert isinstance(result, Failure)

        concept_error = result.failure()
        assert concept_error.phase == "package-concept"
        assert concept_error.package_name == "project-a"

    def test_aggregate_concept_error(
        self,
        project_a_context: ProjectContext,
    ) -> None:
        error = ConceptError(
            message="directory concept failed",
            file_path=project_a_context.project_root,
            package_name=project_a_context.config.name,
            phase="directory-summary",
            identity=None,
            context=None,
        )

        with patch(
            "gyomu_concept.package.analysis._aggregate_file_and_load_directory",
            return_value=Failure(error),
        ):
            result = build_package_analysis(context=project_a_context)

        assert isinstance(result, Failure)

        assert result.failure() is error

    def test_aggregate_analysis_error(
        self,
        project_a_context: ProjectContext,
    ) -> None:
        error = AnalysisError(
            "find root failed",
            file_path=FullPath(Path("/tmp/test.py")),
            phase="analysis",
        )

        with patch(
            "gyomu_concept.package.analysis._aggregate_file_and_load_directory",
            return_value=Failure(error),
        ):
            result = build_package_analysis(context=project_a_context)

        assert isinstance(result, Failure)

        concept_error = result.failure()
        assert concept_error.phase == "package-concept"
        assert concept_error.package_name == "project-a"
