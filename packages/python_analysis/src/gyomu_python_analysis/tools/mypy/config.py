from pathlib import Path

from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.mypy.models import MypyCheckConfig, MypyTarget


def for_file(
    workspace_relative_file_path: ProjectRelativePath,
    target_project_context: ProjectContext,
    workspace_root_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> MypyCheckConfig:
    return MypyCheckConfig(
        targets=(workspace_relative_file_path,),
        config_file=_get_workspace_pyproject_toml(workspace_context=workspace_context),
        cache_dir=None,
        explicit_package_bases=True,
        working_directory=workspace_root_project_context.project_root,
        mypy_path=_gather_workspace_projects_src_path(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        ),
    )


def for_project(
    target: MypyTarget,
    target_project_context: ProjectContext,
    workspace_root_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> MypyCheckConfig:
    cache_dir = target_project_context.project_root / ".mypy_cache" / str(target)
    match target:
        case MypyTarget.SOURCE:
            return MypyCheckConfig(
                targets=_collect_source_dirs_from_package(
                    target_project_context=target_project_context
                ),
                config_file=_get_workspace_pyproject_toml(
                    workspace_context=workspace_context
                ),
                cache_dir=cache_dir,
                explicit_package_bases=False,
                working_directory=workspace_root_project_context.project_root,
                mypy_path=None,
            )
        case MypyTarget.TEST_SUPPORT:
            return MypyCheckConfig(
                targets=_collect_test_support_files_from_package(
                    target_project_context=target_project_context
                ),
                config_file=_get_workspace_pyproject_toml(
                    workspace_context=workspace_context
                ),
                cache_dir=cache_dir,
                explicit_package_bases=True,
                working_directory=workspace_root_project_context.project_root,
                mypy_path=_gather_workspace_projects_src_path(
                    target_project_context=target_project_context,
                    workspace_context=workspace_context,
                ),
            )
        case MypyTarget.TESTS:
            return MypyCheckConfig(
                targets=_collect_test_dirs_from_package(
                    target_project_context=target_project_context
                ),
                config_file=_get_workspace_mypy_test_ini(
                    workspace_context=workspace_context
                ),
                cache_dir=cache_dir,
                explicit_package_bases=True,
                working_directory=workspace_root_project_context.project_root,
                mypy_path=_gather_workspace_projects_src_path(
                    target_project_context=target_project_context,
                    workspace_context=workspace_context,
                ),
            )


def for_workspace(
    workspace_context: WorkspaceContext,
    target: MypyTarget,
) -> MypyCheckConfig:
    cache_dir = workspace_context.workspace_root.path / ".mypy_cache" / str(target)
    match target:
        case MypyTarget.SOURCE:
            return MypyCheckConfig(
                targets=_collect_source_dirs(workspace_context=workspace_context),
                config_file=_get_workspace_pyproject_toml(
                    workspace_context=workspace_context
                ),
                cache_dir=cache_dir,
                explicit_package_bases=False,
                working_directory=workspace_context.workspace_root.path,
                mypy_path=None,
            )
        case MypyTarget.TEST_SUPPORT:
            return MypyCheckConfig(
                targets=_collect_test_support_files(
                    workspace_context=workspace_context
                ),
                config_file=_get_workspace_pyproject_toml(
                    workspace_context=workspace_context
                ),
                cache_dir=cache_dir,
                explicit_package_bases=True,
                working_directory=workspace_context.workspace_root.path,
                mypy_path=(workspace_context.workspace_root.path,),
            )
        case MypyTarget.TESTS:
            return MypyCheckConfig(
                targets=_collect_test_dirs(workspace_context=workspace_context),
                config_file=_get_workspace_mypy_test_ini(
                    workspace_context=workspace_context
                ),
                cache_dir=cache_dir,
                explicit_package_bases=True,
                working_directory=workspace_context.workspace_root.path,
                mypy_path=(workspace_context.workspace_root.path,),
            )


def _collect_test_dirs(workspace_context: WorkspaceContext) -> tuple[Path, ...]:
    paths: list[Path] = []
    for project in workspace_context.projects:
        project_context = workspace_context.get_project_context(project.config.name)
        if project_context is not None:
            test_dir = project_context.project_root / "tests"
            if test_dir.exists():
                paths.append(test_dir)
    return tuple(sorted(paths))


def _collect_test_dirs_from_package(
    target_project_context: ProjectContext,
) -> tuple[Path, ...]:
    test_dir = target_project_context.project_root / "tests"
    if test_dir.exists():
        return (test_dir,)
    return ()


def _collect_source_dirs(workspace_context: WorkspaceContext) -> tuple[Path, ...]:
    paths: list[Path] = []
    for project in workspace_context.projects:
        project_context = workspace_context.get_project_context(project.config.name)
        if project_context is not None:
            paths.append(project_context.project_root / project_context.source_root)
    return tuple(sorted(paths))


def _collect_source_dirs_from_package(
    target_project_context: ProjectContext,
) -> tuple[Path, ...]:
    return (target_project_context.project_root / target_project_context.source_root,)


def _collect_test_support_files(
    workspace_context: WorkspaceContext,
) -> tuple[Path, ...]:
    paths: list[Path] = []
    for project in workspace_context.projects:
        project_context = workspace_context.get_project_context(project.config.name)
        if project_context is not None:
            support_dir = project_context.project_root / "test_support"
            if support_dir.exists() and support_dir.is_dir():
                for file in support_dir.glob("*.py"):
                    if file.is_file():
                        paths.append(file)
    return tuple(sorted(paths))


def _collect_test_support_files_from_package(
    target_project_context: ProjectContext,
) -> tuple[Path, ...]:
    """Collect Python files directly under each test_support directory."""
    return tuple(
        sorted(
            file
            for support_dir in (target_project_context.project_root / "test_support",)
            if support_dir.exists() and support_dir.is_dir()
            for file in support_dir.glob("*.py")
            if file.is_file()
        )
    )


def _gather_workspace_projects_src_path(
    target_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> tuple[Path, ...]:
    target_paths: list[Path] = []

    target_paths.append(
        target_project_context.project_root / target_project_context.source_root
    )

    dependencies = target_project_context.config.get_attribute(
        "project.dependencies", list[str]
    )
    if dependencies is not None:
        for dependency in dependencies:
            dependency_context = workspace_context.get_project_context(dependency)
            if dependency_context is not None:
                target_paths.append(
                    dependency_context.project_root / dependency_context.source_root
                )

    return tuple(target_paths)


def _get_workspace_pyproject_toml(workspace_context: WorkspaceContext) -> FullPath:
    return workspace_context.workspace_root.path / "pyproject.toml"


def _get_workspace_mypy_test_ini(workspace_context: WorkspaceContext) -> FullPath:
    return workspace_context.workspace_root.path / "mypy-tests.ini"
