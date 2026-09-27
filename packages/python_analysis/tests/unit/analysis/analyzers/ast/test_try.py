import ast

from gyomu_python_analysis.analysis.analyzers.ast.statement import analyze_statement
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_schema.schemas.python.type.expression import (
    AssignStatementAnalysis,
    AugAssignStatementAnalysis,
    BinaryOperator,
    CallExpressionAnalysis,
    NameExpressionAnalysis,
    ReturnStatementAnalysis,
    StatementKind,
    TryStatementAnalysis,
    UnaryOperator,
    UnaryOpExpressionAnalysis,
)
from gyomu_schema.schemas.python.type.structure import LiteralValue

from packages.python_analysis.tests.unit.analysis.analyzers.ast.helper import (
    assert_expression_type,
    find_function,
)


def analyze_try_functions(
    context: SymbolContext,
    function_name: str,
) -> list[TryStatementAnalysis]:
    function = find_function("try", function_name)
    target_statements: list[TryStatementAnalysis] = []
    for stmt in function.body:
        if isinstance(stmt, ast.Try):
            result = analyze_statement(stmt, context, None, False)
            assert isinstance(result, TryStatementAnalysis)
            target_statements.append(result)

    return target_statements


def test_simple_try(
    context: SymbolContext,
) -> None:
    results = analyze_try_functions(context, "simple_try")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.TRY
    assert result.orelse == ()
    assert result.finalbody == ()

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
        NameExpressionAnalysis,
    )
    assert statement.value.func.name == "int"

    assert len(statement.value.args) == 1

    argument = assert_expression_type(
        statement.value.args[0],
        NameExpressionAnalysis,
    )
    assert argument.name == "value"

    assert statement.value.keywords == ()

    assert len(result.handlers) == 1

    handler = result.handlers[0]

    assert handler.name is None

    handler.exception_type = assert_expression_type(
        handler.exception_type,
        NameExpressionAnalysis,
    )
    assert handler.exception_type.name == "ValueError"

    assert len(handler.body) == 1

    statement = handler.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == 0


def test_try_except_as(
    context: SymbolContext,
) -> None:
    results = analyze_try_functions(context, "try_except_as")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.TRY
    assert result.orelse == ()
    assert result.finalbody == ()

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
        NameExpressionAnalysis,
    )
    assert statement.value.func.name == "int"

    assert len(statement.value.args) == 1

    argument = assert_expression_type(
        statement.value.args[0],
        NameExpressionAnalysis,
    )
    assert argument.name == "value"

    assert statement.value.keywords == ()

    assert len(result.handlers) == 1

    handler = result.handlers[0]

    assert handler.name == "error"

    handler.exception_type = assert_expression_type(
        handler.exception_type,
        NameExpressionAnalysis,
    )
    assert handler.exception_type.name == "ValueError"

    assert len(handler.body) == 1

    statement = handler.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == 0


def test_try_multiple_except(
    context: SymbolContext,
) -> None:
    results = analyze_try_functions(context, "try_multiple_except")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.TRY
    assert result.orelse == ()
    assert result.finalbody == ()

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
        NameExpressionAnalysis,
    )
    assert statement.value.func.name == "int"

    assert len(statement.value.args) == 1

    argument = assert_expression_type(
        statement.value.args[0],
        NameExpressionAnalysis,
    )
    assert argument.name == "value"

    assert statement.value.keywords == ()

    assert len(result.handlers) == 2

    handler = result.handlers[0]

    assert handler.name is None

    handler.exception_type = assert_expression_type(
        handler.exception_type,
        NameExpressionAnalysis,
    )
    assert handler.exception_type.name == "ValueError"

    assert len(handler.body) == 1

    statement = handler.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == 0

    handler = result.handlers[1]

    assert handler.name is None

    handler.exception_type = assert_expression_type(
        handler.exception_type,
        NameExpressionAnalysis,
    )
    assert handler.exception_type.name == "TypeError"

    assert len(handler.body) == 1

    statement = handler.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        UnaryOpExpressionAnalysis,
    )
    assert statement.value.op == UnaryOperator.U_SUB

    statement.value.operand = assert_expression_type(
        statement.value.operand,
        LiteralValue,
    )
    assert statement.value.operand.value == 1


def test_try_except_else(
    context: SymbolContext,
) -> None:
    results = analyze_try_functions(context, "try_except_else")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.TRY
    assert result.finalbody == ()

    assert len(result.body) == 1

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
        CallExpressionAnalysis,
    )

    statement.value.func = assert_expression_type(
        statement.value.func,
        NameExpressionAnalysis,
    )
    assert statement.value.func.name == "int"

    assert len(statement.value.args) == 1

    argument = assert_expression_type(
        statement.value.args[0],
        NameExpressionAnalysis,
    )
    assert argument.name == "value"

    assert statement.value.keywords == ()

    assert len(result.handlers) == 1

    handler = result.handlers[0]

    assert handler.name is None

    handler.exception_type = assert_expression_type(
        handler.exception_type,
        NameExpressionAnalysis,
    )
    assert handler.exception_type.name == "ValueError"

    assert len(handler.body) == 1

    statement = handler.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == 0

    assert len(result.orelse) == 1

    statement = result.orelse[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        NameExpressionAnalysis,
    )
    assert statement.value.name == "result"


def test_try_except_finally(
    context: SymbolContext,
) -> None:
    results = analyze_try_functions(context, "try_except_finally")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.TRY
    assert result.orelse == ()

    assert len(result.body) == 1

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
        CallExpressionAnalysis,
    )

    statement.value.func = assert_expression_type(
        statement.value.func,
        NameExpressionAnalysis,
    )
    assert statement.value.func.name == "int"

    assert len(statement.value.args) == 1

    argument = assert_expression_type(
        statement.value.args[0],
        NameExpressionAnalysis,
    )
    assert argument.name == "value"

    assert statement.value.keywords == ()

    assert len(result.handlers) == 1

    handler = result.handlers[0]

    assert handler.name is None

    handler.exception_type = assert_expression_type(
        handler.exception_type,
        NameExpressionAnalysis,
    )
    assert handler.exception_type.name == "ValueError"

    assert len(handler.body) == 1

    statement = handler.body[0]
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
        LiteralValue,
    )
    assert statement.value.value == 0

    assert len(result.finalbody) == 1

    statement = result.finalbody[0]
    assert statement.kind == StatementKind.AUGASSIGN
    assert isinstance(statement, AugAssignStatementAnalysis)

    statement.target = assert_expression_type(
        statement.target,
        NameExpressionAnalysis,
    )
    assert statement.target.name == "result"

    assert statement.op == BinaryOperator.ADD

    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == 1
