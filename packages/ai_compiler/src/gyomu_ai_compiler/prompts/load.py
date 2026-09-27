from importlib.resources import files

from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from returns.result import Failure, Result, Success


def load_prompt(name: str) -> Result[str, GyomuIOError]:
    """Load a prompt template by name.

    Loads a prompt template by name from the prompts package.

    Args:
        name (str): Name of the prompt file to load.

    Returns:
        Result[str, GyomuIOError]: A Result containing the prompt content as a string on
            success, or a GyomuIOError on failure.
    """
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
    """Load the base prompt for docstring updates.

    Loads the base prompt used for docstring updates.

    Returns:
        Result[str, GyomuIOError]: A Result containing the docstring update base prompt
            content on success, or a GyomuIOError on failure.
    """
    return load_prompt("docstring-update-base.md")
