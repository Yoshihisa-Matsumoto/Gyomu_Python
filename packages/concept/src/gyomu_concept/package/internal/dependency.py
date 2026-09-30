from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.concept.package.analysis import (
    PackageDependencyAnalysis,
    PackageDependencyKind,
)
from packaging.requirements import Requirement


def collect_dependencies(
    context: ProjectContext, workspace_context: WorkspaceContext | None
) -> tuple[PackageDependencyAnalysis, ...]:
    """Collects and analyzes project dependencies and development dependencies.

    Args:
        context (ProjectContext): The project context containing configuration and
            dependencies.
        workspace_context (WorkspaceContext | None): Optional workspace context
            containing workspace-level projects and constraints.

    Returns:
        tuple[PackageDependencyAnalysis, ...]: A tuple of package dependency analyses.
    """
    dependencies: list[PackageDependencyAnalysis] = []

    workspace_dependency_constraints = (
        workspace_context.config.get_attribute(
            "tool.uv.constraint-dependencies", return_type=list[str]
        )
        if workspace_context is not None
        else None
    )
    workspace_project_names = (
        [item.config.name for item in workspace_context.projects]
        if workspace_context is not None
        else []
    )
    constraints_dependencies: dict[str, str] = {}
    if workspace_dependency_constraints is not None:
        for item in workspace_dependency_constraints:
            requirement = Requirement(item)
            constraints_dependencies[requirement.name] = str(requirement.specifier)

    project_dependencies = context.config.get_attribute(
        "project.dependencies", return_type=list[str]
    )
    if project_dependencies is not None:
        for item in project_dependencies:
            requirement = Requirement(item)
            kind: PackageDependencyKind = (
                "workspace"
                if requirement.name in workspace_project_names
                else "version"
            )
            required_version: str | None = None
            if kind == "workspace":
                required_version = None
            else:
                if requirement.name in constraints_dependencies:
                    required_version = constraints_dependencies[requirement.name]
                else:
                    required_version = str(requirement.specifier)

            dependencies.append(
                PackageDependencyAnalysis(
                    package_name=requirement.name,
                    kind=kind,
                    source="dependency",
                    required_version=required_version,
                )
            )

    project_dev_dependencies = context.config.get_attribute(
        "dependency-groups.dev", list[str]
    )
    if project_dev_dependencies is not None:
        for item in project_dev_dependencies:
            requirement = Requirement(item)
            dev_kind: PackageDependencyKind = (
                "workspace"
                if requirement.name in workspace_project_names
                else "version"
            )
            dev_required_version: str | None = None
            if dev_kind == "workspace":
                dev_required_version = None
            else:
                if requirement.name in constraints_dependencies:
                    dev_required_version = constraints_dependencies[requirement.name]
                else:
                    dev_required_version = str(requirement.specifier)

            dependencies.append(
                PackageDependencyAnalysis(
                    package_name=requirement.name,
                    kind=dev_kind,
                    source="devDependency",
                    required_version=dev_required_version,
                )
            )
    return tuple(dependencies)
