import pytest
from gyomu_ai_compiler.prompts.load import load_docstring_update_base_prompt
from returns.result import Success


@pytest.mark.package
@pytest.mark.integration
def test_load_docstring_update_base_prompt_from_installed_package() -> None:
    result = load_docstring_update_base_prompt()

    assert isinstance(result, Success)
    assert result.unwrap()
