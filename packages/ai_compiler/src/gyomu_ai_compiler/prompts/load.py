from importlib.resources import files

from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from returns.result import Failure, Result, Success


def load_prompt(name: str) -> Result[str, GyomuIOError]:
    try:
        return Success(
            files("gyomu_ai_compiler.prompts")
            .joinpath(name)
            .read_text(encoding="utf-8")
        )
    except OSError as e:
        return Failure(
            GyomuIOError(
                "fail to load prompt",
                layer=IOLayer.FILESYSTEM,
                operation=IOOperation.READ,
                target=name,
            ).chain(e)
        )


def load_docstring_update_base_prompt() -> Result[str, GyomuIOError]:
    return load_prompt("docstring-update-base.md")
