import pytest
from gyomu_python_analysis.analysis.analyzers.context import (
    build_declaration_identity,
    build_symbol_id,
    initialize_symbol_context,
)
from gyomu_schema.schemas.python.types import PythonPath

MODULE_NAME = PythonPath("gyomu_schema.schemas.python.user")


def test_initialize_symbol_context() -> None:
    context = initialize_symbol_context(
        module_name=MODULE_NAME,
        name="User",
    )

    assert context.dependencies == []
    assert context.declaration.symbol_id == "gyomu_schema.schemas.python.user::User"


def test_build_symbol_id() -> None:
    result = build_symbol_id(
        module_name=MODULE_NAME,
        name="User",
    )

    assert result == "gyomu_schema.schemas.python.user::User"


def test_build_symbol_id_for_empty_name() -> None:
    result = build_symbol_id(
        module_name=MODULE_NAME,
        name="",
    )

    assert result == MODULE_NAME


@pytest.mark.parametrize(
    ("member_path", "expected_declaration_id"),
    [
        ((), "."),
        (("name",), ".::name"),
        (("get_name",), ".::get_name"),
        (("Address",), ".::Address"),
        (("Address", "to_string"), ".::Address::to_string"),
        (("get_name", "$parameter", "user_id"), ".::get_name::$parameter::user_id"),
        (("get_name", "$return"), ".::get_name::$return"),
    ],
)
def test_build_declaration_identity(
    member_path: tuple[str, ...],
    expected_declaration_id: str,
) -> None:
    context = initialize_symbol_context(
        module_name=MODULE_NAME,
        name="User",
    )

    result = build_declaration_identity(
        context=context,
        member_path=member_path,
    )

    assert result.symbol_id == context.declaration.symbol_id
    assert result.declaration_id == expected_declaration_id
