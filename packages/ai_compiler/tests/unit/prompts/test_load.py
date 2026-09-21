from gyomu_ai_compiler.prompts.load import (
    load_docstring_update_base_prompt,
    load_prompt,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from returns.pipeline import is_successful
from returns.result import Failure, Success


def test_load_prompt() -> None:
    result = load_prompt("docstring-update-base.md")

    if not is_successful(result):
        print(result.failure())
    assert isinstance(result, Success)
    assert result.unwrap()


def test_load_prompt_when_not_found() -> None:
    result = load_prompt("not-found.md")

    assert isinstance(result, Failure)

    error = result.failure()
    assert isinstance(error, GyomuIOError)
    assert error.layer is IOLayer.FILESYSTEM
    assert error.operation is IOOperation.READ
    assert error.target == "not-found.md"


def test_load_docstring_update_base_prompt() -> None:
    result = load_docstring_update_base_prompt()

    assert isinstance(result, Success)
    assert result.unwrap()
