import pytest
from gyomu_concept.package.internal.dependency import collect_dependencies
from gyomu_schema.schemas.concept.package.analysis import PackageDependencyAnalysis

from packages.concept.concept_test_support.helpers import (
    create_monorepo_project_context,
    create_workspace_context,
)


@pytest.fixture
def workspace_context():
    return create_workspace_context()


@pytest.fixture
def project_a_context():
    return create_monorepo_project_context("project_a")


def test_collect_runtime_dependencies(
    project_a_context,
    workspace_context,
):
    actual = collect_dependencies(
        project_a_context,
        workspace_context,
    )

    assert actual[:3] == (
        PackageDependencyAnalysis(
            package_name="project-b",
            kind="workspace",
            source="dependency",
            required_version=None,
        ),
        PackageDependencyAnalysis(
            package_name="pydantic",
            kind="version",
            source="dependency",
            required_version="<3,>=2",
        ),
        PackageDependencyAnalysis(
            package_name="returns",
            kind="version",
            source="dependency",
            required_version="<1,>=0.29.0",
        ),
    )


def test_collect_dependencies(
    project_a_context,
    workspace_context,
):
    actual = collect_dependencies(
        project_a_context,
        workspace_context,
    )

    assert actual == (
        PackageDependencyAnalysis(
            package_name="project-b",
            kind="workspace",
            source="dependency",
            required_version=None,
        ),
        PackageDependencyAnalysis(
            package_name="pydantic",
            kind="version",
            source="dependency",
            required_version="<3,>=2",
        ),
        PackageDependencyAnalysis(
            package_name="returns",
            kind="version",
            source="dependency",
            required_version="<1,>=0.29.0",
        ),
        PackageDependencyAnalysis(
            package_name="project-b",
            kind="workspace",
            source="devDependency",
            required_version=None,
        ),
        PackageDependencyAnalysis(
            package_name="pytest",
            kind="version",
            source="devDependency",
            required_version=">=9",
        ),
        PackageDependencyAnalysis(
            package_name="python-dotenv",
            kind="version",
            source="devDependency",
            required_version="<2,>=1.2.3",
        ),
    )


def test_collect_dependencies_without_workspace(
    project_a_context,
):
    actual = collect_dependencies(project_a_context, None)

    assert actual == (
        PackageDependencyAnalysis(
            package_name="project-b",
            kind="version",
            source="dependency",
            required_version="",
        ),
        PackageDependencyAnalysis(
            package_name="pydantic",
            kind="version",
            source="dependency",
            required_version="",
        ),
        PackageDependencyAnalysis(
            package_name="returns",
            kind="version",
            source="dependency",
            required_version=">=0.28",
        ),
        PackageDependencyAnalysis(
            package_name="project-b",
            kind="version",
            source="devDependency",
            required_version="",
        ),
        PackageDependencyAnalysis(
            package_name="pytest",
            kind="version",
            source="devDependency",
            required_version=">=9",
        ),
        PackageDependencyAnalysis(
            package_name="python-dotenv",
            kind="version",
            source="devDependency",
            required_version="",
        ),
    )
