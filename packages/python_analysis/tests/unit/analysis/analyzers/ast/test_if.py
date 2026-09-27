import ast

from gyomu_python_analysis.analysis.analyzers.ast.statement import analyze_statement
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_schema.schemas.python.type.expression import (
    AssignStatementAnalysis,
    AugAssignStatementAnalysis,
    CompareExpressionAnalysis,
    CompareOperator,
    IfStatementAnalysis,
    NameExpressionAnalysis,
    ReturnStatementAnalysis,
    StatementKind,
)
from gyomu_schema.schemas.python.type.structure import LiteralValue

from packages.python_analysis.tests.unit.analysis.analyzers.ast.helper import (
    assert_expression_type,
    find_function,
)


def analyze_if_functions(
    context: SymbolContext,
    function_name: str,
) -> list[IfStatementAnalysis]:
    function = find_function("if", function_name)
    target_statements: list[IfStatementAnalysis] = []
    for stmt in function.body:
        if isinstance(stmt, ast.If):
            result = analyze_statement(stmt, context, None, False)
            assert isinstance(result, IfStatementAnalysis)
            target_statements.append(result)

    return target_statements


def test_simple_if(
    context: SymbolContext,
) -> None:
    results = analyze_if_functions(context, "simple_if")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.IF
    assert len(result.body) == 1
    assert result.orelse == ()

    result.test = assert_expression_type(
        result.test,
        CompareExpressionAnalysis,
    )

    result.test.left = assert_expression_type(
        result.test.left,
        NameExpressionAnalysis,
    )
    assert result.test.left.name == "value"

    assert result.test.ops == (CompareOperator.GT,)

    assert len(result.test.comparators) == 1

    comparator = assert_expression_type(result.test.comparators[0], LiteralValue)

    assert comparator.value == 0

    statement = result.body[0]
    assert statement.kind == StatementKind.RETURN

    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "positive"


def test_if_else(
    context: SymbolContext,
) -> None:
    results = analyze_if_functions(context, "if_else")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.IF
    assert len(result.body) == 1
    assert len(result.orelse) == 1

    result.test = assert_expression_type(
        result.test,
        CompareExpressionAnalysis,
    )

    result.test.left = assert_expression_type(
        result.test.left,
        NameExpressionAnalysis,
    )
    assert result.test.left.name == "value"

    assert result.test.ops == (CompareOperator.GT,)

    assert len(result.test.comparators) == 1

    comparator = assert_expression_type(result.test.comparators[0], LiteralValue)

    assert comparator.value == 0

    statement = result.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "positive"

    statement = result.orelse[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "non-positive"


def test_if_elif_else(
    context: SymbolContext,
) -> None:
    results = analyze_if_functions(context, "if_elif_else")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.IF
    assert len(result.body) == 1
    assert len(result.orelse) == 1

    result.test = assert_expression_type(
        result.test,
        CompareExpressionAnalysis,
    )

    result.test.left = assert_expression_type(
        result.test.left,
        NameExpressionAnalysis,
    )
    assert result.test.left.name == "value"

    assert result.test.ops == (CompareOperator.GT,)

    assert len(result.test.comparators) == 1

    comparator = assert_expression_type(result.test.comparators[0], LiteralValue)

    assert comparator.value == 0

    statement = result.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "positive"

    statement = result.orelse[0]
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

    assert statement.test.ops == (CompareOperator.EQ,)

    assert len(statement.test.comparators) == 1

    comparator = assert_expression_type(
        statement.test.comparators[0],
        LiteralValue,
    )
    assert comparator.value == 0

    assert len(statement.body) == 1
    assert len(statement.orelse) == 1

    nested_statement = statement.body[0]
    assert nested_statement.kind == StatementKind.RETURN
    assert isinstance(nested_statement, ReturnStatementAnalysis)

    nested_statement.value = assert_expression_type(
        nested_statement.value,
        LiteralValue,
    )
    assert nested_statement.value.value == "zero"

    nested_statement = statement.orelse[0]
    assert nested_statement.kind == StatementKind.RETURN
    assert isinstance(nested_statement, ReturnStatementAnalysis)

    nested_statement.value = assert_expression_type(
        nested_statement.value,
        LiteralValue,
    )
    assert nested_statement.value.value == "negative"


def test_nested_if(
    context: SymbolContext,
) -> None:
    results = analyze_if_functions(context, "nested_if")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.IF
    assert len(result.body) == 1
    assert result.orelse == ()

    result.test = assert_expression_type(
        result.test,
        CompareExpressionAnalysis,
    )

    result.test.left = assert_expression_type(
        result.test.left,
        NameExpressionAnalysis,
    )
    assert result.test.left.name == "value"

    assert result.test.ops == (CompareOperator.GT,)

    assert len(result.test.comparators) == 1

    comparator = assert_expression_type(
        result.test.comparators[0],
        LiteralValue,
    )
    assert comparator.value == 0

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

    assert statement.test.ops == (CompareOperator.GT_E,)

    assert len(statement.test.comparators) == 1

    comparator = assert_expression_type(
        statement.test.comparators[0],
        NameExpressionAnalysis,
    )
    assert comparator.name == "threshold"

    assert len(statement.body) == 1
    assert len(statement.orelse) == 1

    nested_statement = statement.body[0]
    assert nested_statement.kind == StatementKind.RETURN
    assert isinstance(nested_statement, ReturnStatementAnalysis)

    nested_statement.value = assert_expression_type(
        nested_statement.value,
        LiteralValue,
    )
    assert nested_statement.value.value == "large"

    nested_statement = statement.orelse[0]
    assert nested_statement.kind == StatementKind.RETURN
    assert isinstance(nested_statement, ReturnStatementAnalysis)

    nested_statement.value = assert_expression_type(
        nested_statement.value,
        LiteralValue,
    )
    assert nested_statement.value.value == "small"


def test_if_with_multiple_statements(
    context: SymbolContext,
) -> None:
    results = analyze_if_functions(context, "if_with_multiple_statements")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.IF
    assert len(result.body) == 3
    assert result.orelse == ()

    result.test = assert_expression_type(
        result.test,
        CompareExpressionAnalysis,
    )

    result.test.left = assert_expression_type(
        result.test.left,
        NameExpressionAnalysis,
    )
    assert result.test.left.name == "value"

    assert result.test.ops == (CompareOperator.GT,)

    assert len(result.test.comparators) == 1

    comparator = assert_expression_type(
        result.test.comparators[0],
        LiteralValue,
    )
    assert comparator.value == 0

    statement = result.body[0]
    assert statement.kind == StatementKind.ASSIGN
    assert isinstance(statement, AssignStatementAnalysis)

    assert len(statement.targets) == 1

    target = assert_expression_type(
        statement.targets[0],
        NameExpressionAnalysis,
    )
    assert target.name == "result"

    statement.value = assert_expression_type(
        statement.value,
        NameExpressionAnalysis,
    )
    assert statement.value.name == "value"

    statement = result.body[1]
    assert statement.kind == StatementKind.AUGASSIGN
    assert isinstance(statement, AugAssignStatementAnalysis)

    statement.target = assert_expression_type(
        statement.target,
        NameExpressionAnalysis,
    )
    assert statement.target.name == "result"

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == 1

    statement = result.body[2]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        NameExpressionAnalysis,
    )
    assert statement.value.name == "result"
