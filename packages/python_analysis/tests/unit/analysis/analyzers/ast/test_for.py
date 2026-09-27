import ast

from gyomu_python_analysis.analysis.analyzers.ast.statement import analyze_statement
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_schema.schemas.python.type.expression import (
    AugAssignStatementAnalysis,
    BinaryOperator,
    BreakStatementAnalysis,
    CompareExpressionAnalysis,
    CompareOperator,
    ForStatementAnalysis,
    IfStatementAnalysis,
    NameExpressionAnalysis,
    StatementKind,
)
from gyomu_schema.schemas.python.type.structure import LiteralValue

from packages.python_analysis.tests.unit.analysis.analyzers.ast.helper import (
    assert_expression_type,
    find_function,
)


def analyze_for_functions(
    context: SymbolContext,
    function_name: str,
) -> list[ForStatementAnalysis]:
    function = find_function("for", function_name)
    target_statements: list[ForStatementAnalysis] = []
    for stmt in function.body:
        if isinstance(stmt, ast.For):
            result = analyze_statement(stmt, context, None, False)
            assert isinstance(result, ForStatementAnalysis)
            target_statements.append(result)

    return target_statements


def test_simple_for(
    context: SymbolContext,
) -> None:
    results = analyze_for_functions(context, "simple_for")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.FOR
    assert result.orelse == ()
    assert result.type_comment is None

    result.target = assert_expression_type(
        result.target,
        NameExpressionAnalysis,
    )
    assert result.target.name == "value"

    result.iter = assert_expression_type(
        result.iter,
        NameExpressionAnalysis,
    )
    assert result.iter.name == "values"

    assert len(result.body) == 1

    statement = result.body[0]
    assert statement.kind == StatementKind.AUGASSIGN
    assert isinstance(statement, AugAssignStatementAnalysis)

    statement.target = assert_expression_type(
        statement.target,
        NameExpressionAnalysis,
    )
    assert statement.target.name == "total"

    assert statement.op == BinaryOperator.ADD

    statement.value = assert_expression_type(
        statement.value,
        NameExpressionAnalysis,
    )
    assert statement.value.name == "value"


def test_for_with_else(
    context: SymbolContext,
) -> None:
    results = analyze_for_functions(context, "for_with_else")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.FOR
    assert result.type_comment is None

    result.target = assert_expression_type(
        result.target,
        NameExpressionAnalysis,
    )
    assert result.target.name == "value"

    result.iter = assert_expression_type(
        result.iter,
        NameExpressionAnalysis,
    )
    assert result.iter.name == "values"

    assert len(result.body) == 1
    assert len(result.orelse) == 1

    statement = result.body[0]
    assert statement.kind == StatementKind.AUGASSIGN
    assert isinstance(statement, AugAssignStatementAnalysis)

    statement.target = assert_expression_type(
        statement.target,
        NameExpressionAnalysis,
    )
    assert statement.target.name == "total"

    assert statement.op == BinaryOperator.ADD

    statement.value = assert_expression_type(
        statement.value,
        NameExpressionAnalysis,
    )
    assert statement.value.name == "value"

    statement = result.orelse[0]
    assert statement.kind == StatementKind.AUGASSIGN
    assert isinstance(statement, AugAssignStatementAnalysis)

    statement.target = assert_expression_type(
        statement.target,
        NameExpressionAnalysis,
    )
    assert statement.target.name == "total"

    assert statement.op == BinaryOperator.ADD

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == 1


def test_for_with_break(
    context: SymbolContext,
) -> None:
    results = analyze_for_functions(context, "for_with_break")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.FOR
    assert result.orelse == ()
    assert result.type_comment is None

    result.target = assert_expression_type(
        result.target,
        NameExpressionAnalysis,
    )
    assert result.target.name == "value"

    result.iter = assert_expression_type(
        result.iter,
        NameExpressionAnalysis,
    )
    assert result.iter.name == "values"

    assert len(result.body) == 2

    statement = result.body[0]
    assert statement.kind == StatementKind.IF
    assert isinstance(statement, IfStatementAnalysis)

    statement.test = assert_expression_type(
        statement.test,
        CompareExpressionAnalysis,
    )

    statement.test.left = assert_expression_type(
        statement.test.left,
        NameExpressionAnalysis,
    )
    assert statement.test.left.name == "value"

    assert statement.test.ops == (CompareOperator.LT,)

    assert len(statement.test.comparators) == 1

    comparator = assert_expression_type(
        statement.test.comparators[0],
        LiteralValue,
    )
    assert comparator.value == 0

    assert len(statement.body) == 1
    assert statement.orelse == ()

    nested_statement = statement.body[0]
    assert nested_statement.kind == StatementKind.BREAK
    assert isinstance(nested_statement, BreakStatementAnalysis)

    statement = result.body[1]
    assert statement.kind == StatementKind.AUGASSIGN
    assert isinstance(statement, AugAssignStatementAnalysis)

    statement.target = assert_expression_type(
        statement.target,
        NameExpressionAnalysis,
    )
    assert statement.target.name == "total"

    assert statement.op == BinaryOperator.ADD

    statement.value = assert_expression_type(
        statement.value,
        NameExpressionAnalysis,
    )
    assert statement.value.name == "value"


def test_nested_for(
    context: SymbolContext,
) -> None:
    results = analyze_for_functions(context, "nested_for")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.FOR
    assert result.orelse == ()
    assert result.type_comment is None

    result.target = assert_expression_type(
        result.target,
        NameExpressionAnalysis,
    )
    assert result.target.name == "items"

    result.iter = assert_expression_type(
        result.iter,
        NameExpressionAnalysis,
    )
    assert result.iter.name == "values"

    assert len(result.body) == 1

    statement = result.body[0]
    assert statement.kind == StatementKind.FOR
    assert isinstance(statement, ForStatementAnalysis)

    statement.target = assert_expression_type(
        statement.target,
        NameExpressionAnalysis,
    )
    assert statement.target.name == "value"

    statement.iter = assert_expression_type(
        statement.iter,
        NameExpressionAnalysis,
    )
    assert statement.iter.name == "items"

    assert statement.orelse == ()
    assert statement.type_comment is None

    assert len(statement.body) == 1

    nested_statement = statement.body[0]
    assert nested_statement.kind == StatementKind.AUGASSIGN
    assert isinstance(nested_statement, AugAssignStatementAnalysis)

    nested_statement.target = assert_expression_type(
        nested_statement.target,
        NameExpressionAnalysis,
    )
    assert nested_statement.target.name == "total"

    assert nested_statement.op == BinaryOperator.ADD

    nested_statement.value = assert_expression_type(
        nested_statement.value,
        NameExpressionAnalysis,
    )
    assert nested_statement.value.name == "value"
