import ast

import pytest
from gyomu_python_analysis.analysis.analyzers.ast.statement import (
    analyze_expression_name,
)
from gyomu_python_analysis.analysis.analyzers.context import DependencyInformation
from gyomu_python_analysis.analysis.analyzers.dependency import (
    PYTHON_RESERVED_TYPE_NAMES,
)
from gyomu_schema.schemas.python.type.expression import ExpressionKind


def test_name_without_dependency_registration(context):
    expression = ast.Name(id="value", ctx=ast.Load())

    result = analyze_expression_name(
        expression,
        context,
        None,
        False,
    )

    assert result.kind == ExpressionKind.NAME
    assert result.name == "value"
    assert context.dependencies == []


def test_name_with_dependency_registration(context):
    expression = ast.Name(id="value", ctx=ast.Load())

    result = analyze_expression_name(
        expression,
        context,
        None,
        True,
    )

    assert result.kind == ExpressionKind.NAME
    assert result.name == "value"

    assert context.dependencies == [
        DependencyInformation(
            source=context.declaration,
            target_name="value",
        )
    ]


@pytest.mark.parametrize(
    "name",
    sorted(PYTHON_RESERVED_TYPE_NAMES),
)
def test_name_with_reserved_type_does_not_register_dependency(
    context,
    name,
):
    expression = ast.Name(id=name, ctx=ast.Load())

    result = analyze_expression_name(
        expression,
        context,
        None,
        True,
    )

    assert result.kind == ExpressionKind.NAME
    assert result.name == name
    assert context.dependencies == []
