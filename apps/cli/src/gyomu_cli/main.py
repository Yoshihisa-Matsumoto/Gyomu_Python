from os import getcwd
from pathlib import Path

import typer
from gyomu_ai.provider.pydantic_ai.google import (
    create_default_pydantic_ai_model_registry,
)
from gyomu_ai.provider.pydantic_ai.route_registry import AiConfiguration, initialize_ai
from gyomu_ai.provider.pydantic_ai.routing import (
    ModelRoute,
    ModelRouteId,
    ModelRoutes,
    RouteNode,
)
from gyomu_ai_compiler.pipelines.docstring_update import DocstringRouteId
from gyomu_ai_compiler.pipelines.document import DocumentRouteId
from gyomu_infra.logger import logger
from gyomu_schema.option.retry import RetryObserver
from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.models import (
    DocstringExecutionOption,
    FileFilter,
    SnapshotActionOption,
    SnapshotExecutionOption,
    SnapshotTargetOption,
)
from gyomu_workflow.snapshot.project import find_project_by_name
from gyomu_workflow.snapshot.workspace import get_workspace_context
from returns.result import Failure

from gyomu_cli.snapshot import run_snapshot_request

app = typer.Typer()
"""Main Typer application instance for the CLI."""


# @hello_app.command()
@app.command()
def greet(name: str = "World") -> None:
    """Greets the user with a hello message.

    Args:
        name (str): Name to greet.

    Returns:
        None: None
    """
    print(f"Hello, {name}!")


def register_google_routing(
    route_id_list: list[ModelRouteId],
    retry_observer: RetryObserver | None = None,
) -> None:
    """Registers Google routing configuration and initializes AI settings.

    Args:
        route_id_list (list[ModelRouteId]): List of model route IDs to register.
        retry_observer (RetryObserver | None): Optional retry observer for handling
            model retries.

    Returns:
        None: None
    """
    route: RouteNode = RouteNode(registry=create_default_pydantic_ai_model_registry())
    routes: dict[ModelRouteId, ModelRoute] = {}
    for route_id in route_id_list:
        routes[route_id] = ModelRoute((route,))
    initialize_ai(
        AiConfiguration(
            model_routes=ModelRoutes(routes=routes), retry_observer=retry_observer
        )
    )


@app.command()
def snapshot(
    package: str | None = None,
    docstring: bool = True,
    all: bool = False,
    commit: bool = True,
    filter: str | None = None,
    log_keyword: str | None = None,
) -> None:
    """Executes a code snapshot for the specified package.

    Args:
        package (str | None): Target package to snapshot.
            If omitted, all workspace projects are processed.
        docstring (bool): Whether to include docstrings.
        all (bool): Whether to process all files.
        commit (bool): Whether to commit the snapshot.
        filter (str | None): Optional file filter pattern.
        log_keyword (str | None): Optional keyword for logging.

    Returns:
        None: None
    """
    register_google_routing(route_id_list=[DocstringRouteId, DocumentRouteId])
    option = SnapshotExecutionOption(
        commit=commit,
        target=SnapshotTargetOption(
            all=all,
            file_filter=FileFilter(pattern=filter) if filter is not None else None,
        ),
        action=SnapshotActionOption(
            docstring=DocstringExecutionOption(
                enabled=docstring, log_keyword=log_keyword
            ),
            project_context=commit,
        ),
    )
    current_path = FullPath(Path(getcwd()))
    workspace_result = get_workspace_context(current_path)
    if isinstance(workspace_result, Failure):
        logger.error_object(workspace_result.failure())
        return
    workspace_context = workspace_result.unwrap()

    if package is not None:
        package_result = find_project_by_name(workspace_context, package)
        if isinstance(package_result, Failure):
            logger.error(f"{package} Not Found")
            logger.error_object(package_result.failure())
            return

        snapshot_result = run_snapshot_request(
            workspace_context, package_result.unwrap(), option
        )
        if isinstance(snapshot_result, Failure):
            return
    else:
        for project in workspace_context.projects:
            logger.info(f"Processing package: {project.config.name}")
            snapshot_result = run_snapshot_request(workspace_context, project, option)
            if isinstance(snapshot_result, Failure):
                return

    logger.info("Done")
    # logger.error_object(request.unwrap(), 3)


if __name__ == "__main__":
    app()
