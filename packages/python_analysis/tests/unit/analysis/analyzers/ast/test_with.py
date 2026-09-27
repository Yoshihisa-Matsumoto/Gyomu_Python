import ast

from gyomu_python_analysis.analysis.analyzers.ast.statement import analyze_statement
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_schema.schemas.python.type.expression import (
    AssignStatementAnalysis,
    AttributeExpressionAnalysis,
    CallExpressionAnalysis,
    NameExpressionAnalysis,
    NoneExpressionAnalysis,
    ReturnStatementAnalysis,
    StatementKind,
    WithStatementAnalysis,
)
from gyomu_schema.schemas.python.type.structure import LiteralValue

from packages.python_analysis.tests.unit.analysis.analyzers.ast.helper import (
    assert_expression_type,
    find_function,
)


def analyze_with_functions(
    context: SymbolContext,
    function_name: str,
) -> list[WithStatementAnalysis]:
    function = find_function("with", function_name)
    target_statements: list[WithStatementAnalysis] = []
    for stmt in function.body:
        if isinstance(stmt, ast.With):
            result = analyze_statement(stmt, context, None, False)
            assert isinstance(result, WithStatementAnalysis)
            target_statements.append(result)
    return target_statements


def test_simple_with(
    context: SymbolContext,
) -> None:
    results = analyze_with_functions(context, "simple_with")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.WITH
    assert result.type_comment is None

    assert len(result.items) == 1
    item = result.items[0]

    item.context_expr = assert_expression_type(
        item.context_expr,
        CallExpressionAnalysis,
    )
    item.context_expr.func = assert_expression_type(
        item.context_expr.func,
        AttributeExpressionAnalysis,
    )
    assert item.context_expr.func.attribute == "open"

    assert len(item.context_expr.args) == 1
    argument = assert_expression_type(
        item.context_expr.args[0],
        LiteralValue,
    )
    assert argument.value == "r"

    assert item.context_expr.keywords == ()

    item.optional_vars = assert_expression_type(
        item.optional_vars,
        NameExpressionAnalysis,
    )
    assert item.optional_vars.name == "file"

    assert len(result.body) == 1
    statement = result.body[0]

    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        CallExpressionAnalysis,
    )

    statement.value.func = assert_expression_type(
        statement.value.func,
        AttributeExpressionAnalysis,
    )
    assert statement.value.func.attribute == "read"
    assert statement.value.args == ()
    assert statement.value.keywords == ()


def test_with_multiple(
    context: SymbolContext,
) -> None:
    results = analyze_with_functions(context, "with_multiple")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.WITH
    assert result.type_comment is None
    assert len(result.items) == 2

    item = result.items[0]
    item.context_expr = assert_expression_type(
        item.context_expr,
        CallExpressionAnalysis,
    )
    item.context_expr.func = assert_expression_type(
        item.context_expr.func,
        AttributeExpressionAnalysis,
    )
    assert item.context_expr.func.attribute == "open"
    item.context_expr.func.value = assert_expression_type(
        item.context_expr.func.value,
        NameExpressionAnalysis,
    )
    assert item.context_expr.func.value.name == "path1"
    assert len(item.context_expr.args) == 1
    argument = assert_expression_type(item.context_expr.args[0], LiteralValue)
    assert argument.value == "r"
    assert item.context_expr.keywords == ()

    item.optional_vars = assert_expression_type(
        item.optional_vars,
        NameExpressionAnalysis,
    )
    assert item.optional_vars.name == "file1"

    item = result.items[1]
    item.context_expr = assert_expression_type(
        item.context_expr,
        CallExpressionAnalysis,
    )
    item.context_expr.func = assert_expression_type(
        item.context_expr.func,
        AttributeExpressionAnalysis,
    )
    assert item.context_expr.func.attribute == "open"
    item.context_expr.func.value = assert_expression_type(
        item.context_expr.func.value,
        NameExpressionAnalysis,
    )
    assert item.context_expr.func.value.name == "path2"
    assert len(item.context_expr.args) == 1
    argument = assert_expression_type(item.context_expr.args[0], LiteralValue)
    assert argument.value == "r"
    assert item.context_expr.keywords == ()

    item.optional_vars = assert_expression_type(
        item.optional_vars,
        NameExpressionAnalysis,
    )
    assert item.optional_vars.name == "file2"

    assert len(result.body) == 1
    statement = result.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)


def test_with_without_as(
    context: SymbolContext,
) -> None:
    results = analyze_with_functions(context, "with_without_as")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.WITH
    assert result.type_comment is None
    assert len(result.items) == 1

    item = result.items[0]

    item.context_expr = assert_expression_type(
        item.context_expr,
        CallExpressionAnalysis,
    )
    item.context_expr.func = assert_expression_type(
        item.context_expr.func,
        AttributeExpressionAnalysis,
    )
    assert item.context_expr.func.attribute == "open"

    item.context_expr.func.value = assert_expression_type(
        item.context_expr.func.value,
        NameExpressionAnalysis,
    )
    assert item.context_expr.func.value.name == "path"

    assert len(item.context_expr.args) == 1
    argument = assert_expression_type(item.context_expr.args[0], LiteralValue)
    assert argument.value == "r"
    assert item.context_expr.keywords == ()

    assert isinstance(item.optional_vars, NoneExpressionAnalysis)

    assert len(result.body) == 1
    assert result.body[0].kind == StatementKind.PASS


def test_nested_with(
    context: SymbolContext,
) -> None:
    results = analyze_with_functions(context, "nested_with")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.WITH
    assert result.type_comment is None
    assert len(result.items) == 1

    item = result.items[0]
    item.context_expr = assert_expression_type(
        item.context_expr,
        CallExpressionAnalysis,
    )
    item.context_expr.func = assert_expression_type(
        item.context_expr.func,
        AttributeExpressionAnalysis,
    )
    assert item.context_expr.func.attribute == "open"
    item.context_expr.func.value = assert_expression_type(
        item.context_expr.func.value,
        NameExpressionAnalysis,
    )
    assert item.context_expr.func.value.name == "path1"

    item.optional_vars = assert_expression_type(
        item.optional_vars,
        NameExpressionAnalysis,
    )
    assert item.optional_vars.name == "file1"

    assert len(result.body) == 1

    nested = result.body[0]
    assert nested.kind == StatementKind.WITH
    assert isinstance(nested, WithStatementAnalysis)

    assert nested.type_comment is None
    assert len(nested.items) == 1

    nested_item = nested.items[0]

    nested_item.context_expr = assert_expression_type(
        nested_item.context_expr,
        CallExpressionAnalysis,
    )
    nested_item.context_expr.func = assert_expression_type(
        nested_item.context_expr.func,
        AttributeExpressionAnalysis,
    )
    assert nested_item.context_expr.func.attribute == "open"
    nested_item.context_expr.func.value = assert_expression_type(
        nested_item.context_expr.func.value,
        NameExpressionAnalysis,
    )
    assert nested_item.context_expr.func.value.name == "path2"

    nested_item.optional_vars = assert_expression_type(
        nested_item.optional_vars,
        NameExpressionAnalysis,
    )
    assert nested_item.optional_vars.name == "file2"

    assert len(nested.body) == 1
    statement = nested.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)


def test_with_multiple_statements(
    context: SymbolContext,
) -> None:
    results = analyze_with_functions(context, "with_multiple_statements")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.WITH
    assert result.type_comment is None
    assert len(result.items) == 1

    item = result.items[0]

    item.context_expr = assert_expression_type(
        item.context_expr,
        CallExpressionAnalysis,
    )
    item.context_expr.func = assert_expression_type(
        item.context_expr.func,
        AttributeExpressionAnalysis,
    )
    assert item.context_expr.func.attribute == "open"

    item.context_expr.func.value = assert_expression_type(
        item.context_expr.func.value,
        NameExpressionAnalysis,
    )
    assert item.context_expr.func.value.name == "path"

    assert len(item.context_expr.args) == 1
    argument = assert_expression_type(item.context_expr.args[0], LiteralValue)
    assert argument.value == "r"
    assert item.context_expr.keywords == ()

    item.optional_vars = assert_expression_type(
        item.optional_vars,
        NameExpressionAnalysis,
    )
    assert item.optional_vars.name == "file"

    assert len(result.body) == 3

    statement = result.body[0]
    assert statement.kind == StatementKind.ASSIGN
    assert isinstance(statement, AssignStatementAnalysis)
    first_assignment_target = assert_expression_type(
        statement.targets[0],
        NameExpressionAnalysis,
    )
    assert first_assignment_target.name == "content"
    statement.value = assert_expression_type(
        statement.value,
        CallExpressionAnalysis,
    )

    statement = result.body[1]
    assert statement.kind == StatementKind.ASSIGN
    assert isinstance(statement, AssignStatementAnalysis)
    first_assignment_target = assert_expression_type(
        statement.targets[0],
        NameExpressionAnalysis,
    )
    assert first_assignment_target.name == "content"
    statement.value = assert_expression_type(
        statement.value,
        CallExpressionAnalysis,
    )
    statement.value.func = assert_expression_type(
        statement.value.func,
        AttributeExpressionAnalysis,
    )
    assert statement.value.func.attribute == "strip"

    statement = result.body[2]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        NameExpressionAnalysis,
    )
    assert statement.value.name == "content"
