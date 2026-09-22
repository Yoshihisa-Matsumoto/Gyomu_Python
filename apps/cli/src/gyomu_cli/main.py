import typer
from gyomu_infra.logger import logger
from returns.result import Failure

from gyomu_cli.snapshot.models import FileFilter, SnapshotExecutionOption
from gyomu_cli.snapshot.translate import translate_snapshot_request

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
    no_docstring: bool = False,
    all: bool = False,
    no_commit: bool = False,
    filter: str | None = None,
    log_keyword: str | None = None,
) -> None:

    option = SnapshotExecutionOption(
        commit=not no_commit,
        docstring=not no_docstring,
        all=all,
        file_filter=(FileFilter(pattern=filter) if filter is not None else None),
        log_keyword=log_keyword,
    )
    request = translate_snapshot_request(package, option)
    if isinstance(request, Failure):
        logger.error_object(request.failure())
        return

    # value = request.unwrap()

    # logger.error_object(value.project_context)
    # logger.error(f"project_root={value.project_context.project_root!r}")
    logger.error_object(request.unwrap(), 4)


if __name__ == "__main__":
    app()
