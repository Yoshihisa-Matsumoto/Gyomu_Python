from importlib.resources import files

from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from returns.result import Failure, Result, Success


def load_prompt(name: str) -> Result[str, GyomuIOError]:
    try:
        return Success(
            files("gyomu_docstring.prompts").joinpath(name).read_text(encoding="utf-8")
        )
    except Exception as e:
        return Failure(
            GyomuIOError(
                "fail to load prompt",
                layer=IOLayer.FILESYSTEM,
                operation=IOOperation.READ,
                target=name,
            ).chain(e)
        )
