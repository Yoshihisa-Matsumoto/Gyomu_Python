import asyncio

import typer
from gyomu_infra.logger import logger
from gyomu_workflow.snapshot.models import (
    DocstringExecutionOption,
    FileFilter,
    SnapshotActionOption,
    SnapshotExecutionOption,
    SnapshotTargetOption,
)
from gyomu_workflow.snapshot.run import run_snapshot
from gyomu_workflow.snapshot.translate import translate_snapshot_request
from gyomu_workflow.snapshot.validate import validate_snapshot_request
from returns.result import Failure

app = typer.Typer()

hello_app = typer.Typer()
app.add_typer(hello_app, name="hello")


# @hello_app.command()
@app.command()
def greet(name: str = "World") -> None:
    print(f"Hello, {name}!")


@app.command()
def greet2(name: str = "World") -> None:
    print(f"Hello, {name}!")


@hello_app.command("greet")
def greet3(name: str = "World") -> None:
    print(f"Hello, {name}!")


@app.command()
def snapshot(
    package: str,
    docstring: bool = True,
    all: bool = False,
    commit: bool = True,
    filter: str | None = None,
    log_keyword: str | None = None,
) -> None:

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
        ),
    )
    request_result = translate_snapshot_request(package, option)
    if isinstance(request_result, Failure):
        logger.error_object(request_result.failure())
        return
    request = request_result.unwrap()
    logger.info(
        f"commit: {request.option.commit}, "
        f"docstring:{request.option.action.docstring.enabled}, "
        f"all={request.option.target.all}"
    )
    if filter:
        assert option.target.file_filter
        logger.info(f"filter: {option.target.file_filter.pattern}")
    if log_keyword:
        logger.info(f"log_keyword: {request.option.action.docstring.log_keyword}")

    validation_result = validate_snapshot_request(request)
    if isinstance(validation_result, Failure):
        logger.error_object(validation_result.failure())
        return

    snapshot_result = asyncio.run(run_snapshot(request))
    if isinstance(snapshot_result, Failure):
        logger.error_object(snapshot_result.failure())
        return

    logger.info("Done")
    # logger.error_object(request.unwrap(), 3)


if __name__ == "__main__":
    app()
