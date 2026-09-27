import ast

from gyomu_python_analysis.analysis.analyzers.ast.statement import analyze_statement
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_schema.schemas.python.type.expression import (
    BinOpExpressionAnalysis,
    CallExpressionAnalysis,
    FunctionDefStatementAnalysis,
    NameExpressionAnalysis,
    ReturnStatementAnalysis,
    StatementKind,
)

from packages.python_analysis.tests.unit.analysis.analyzers.ast.helper import (
    assert_expression_type,
    find_function,
)


def analyze_function_functions(
    context: SymbolContext,
    function_name: str,
) -> list[FunctionDefStatementAnalysis]:
    function = find_function("function", function_name)
    target_statements: list[FunctionDefStatementAnalysis] = []
    for stmt in function.body:
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef):
            result = analyze_statement(stmt, context, None, False)
            assert isinstance(result, FunctionDefStatementAnalysis)
            target_statements.append(result)

    return target_statements


def test_outer(
    context: SymbolContext,
) -> None:
    results = analyze_function_functions(context, "outer")

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.FUNCTIONDEF
    assert result.name == "inner"
    assert result.is_async is False
    assert result.decorator_list == ()
    assert result.type_comment is None
    assert result.type_params == ()

    assert result.args.vararg is None
    assert result.args.kwarg is None
    assert result.args.posonlyargs == ()
    assert result.args.kwonlyargs == ()
    assert result.args.defaults == ()
    assert result.args.kw_defaults == ()

    assert len(result.args.args) == 1

    argument = result.args.args[0]
    assert argument.arg == "value"
    assert argument.type_comment is None

    argument.annotation = assert_expression_type(
        argument.annotation,
        NameExpressionAnalysis,
    )
    assert argument.annotation.name == "int"

    result.returns = assert_expression_type(
        result.returns,
        NameExpressionAnalysis,
    )
    assert result.returns.name == "str"

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
    assert statement.value.func.name == "str"

    assert len(statement.value.args) == 1

    argument = assert_expression_type(
        statement.value.args[0],
        NameExpressionAnalysis,
    )
    assert argument.name == "value"

    assert statement.value.keywords == ()


def test_outer_with_multiple_functions(
    context: SymbolContext,
) -> None:
    results = analyze_function_functions(
        context,
        "outer_with_multiple_functions",
    )

    assert len(results) == 2

    add = results[0]

    assert add.kind == StatementKind.FUNCTIONDEF
    assert add.name == "add"
    assert add.is_async is False
    assert add.decorator_list == ()
    assert add.type_comment is None
    assert add.type_params == ()

    assert add.args.vararg is None
    assert add.args.kwarg is None
    assert add.args.posonlyargs == ()
    assert add.args.kwonlyargs == ()
    assert add.args.defaults == ()
    assert add.args.kw_defaults == ()

    assert len(add.args.args) == 2

    argument = add.args.args[0]
    assert argument.arg == "left"
    assert argument.type_comment is None

    argument.annotation = assert_expression_type(
        argument.annotation,
        NameExpressionAnalysis,
    )
    assert argument.annotation.name == "int"

    argument = add.args.args[1]
    assert argument.arg == "right"
    assert argument.type_comment is None

    argument.annotation = assert_expression_type(
        argument.annotation,
        NameExpressionAnalysis,
    )
    assert argument.annotation.name == "int"

    add.returns = assert_expression_type(
        add.returns,
        NameExpressionAnalysis,
    )
    assert add.returns.name == "int"

    assert len(add.body) == 1

    statement = add.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        BinOpExpressionAnalysis,
    )

    statement.value.left = assert_expression_type(
        statement.value.left,
        NameExpressionAnalysis,
    )
    assert statement.value.left.name == "left"

    statement.value.right = assert_expression_type(
        statement.value.right,
        NameExpressionAnalysis,
    )
    assert statement.value.right.name == "right"

    multiply = results[1]

    assert multiply.kind == StatementKind.FUNCTIONDEF
    assert multiply.name == "multiply"
    assert multiply.is_async is False
    assert multiply.decorator_list == ()
    assert multiply.type_comment is None
    assert multiply.type_params == ()

    assert multiply.args.vararg is None
    assert multiply.args.kwarg is None
    assert multiply.args.posonlyargs == ()
    assert multiply.args.kwonlyargs == ()
    assert multiply.args.defaults == ()
    assert multiply.args.kw_defaults == ()

    assert len(multiply.args.args) == 2

    argument = multiply.args.args[0]
    assert argument.arg == "left"
    assert argument.type_comment is None

    argument.annotation = assert_expression_type(
        argument.annotation,
        NameExpressionAnalysis,
    )
    assert argument.annotation.name == "int"

    argument = multiply.args.args[1]
    assert argument.arg == "right"
    assert argument.type_comment is None

    argument.annotation = assert_expression_type(
        argument.annotation,
        NameExpressionAnalysis,
    )
    assert argument.annotation.name == "int"

    multiply.returns = assert_expression_type(
        multiply.returns,
        NameExpressionAnalysis,
    )
    assert multiply.returns.name == "int"

    assert len(multiply.body) == 1

    statement = multiply.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    statement.value = assert_expression_type(
        statement.value,
        BinOpExpressionAnalysis,
    )

    statement.value.left = assert_expression_type(
        statement.value.left,
        NameExpressionAnalysis,
    )
    assert statement.value.left.name == "left"

    statement.value.right = assert_expression_type(
        statement.value.right,
        NameExpressionAnalysis,
    )
    assert statement.value.right.name == "right"


def test_outer_with_async_function(
    context: SymbolContext,
) -> None:
    results = analyze_function_functions(
        context,
        "outer_with_async_function",
    )

    assert len(results) == 1

    result = results[0]

    assert result.kind == StatementKind.FUNCTIONDEF
    assert result.name == "inner"
    assert result.is_async is True

    assert result.decorator_list == ()
    assert result.type_comment is None
    assert result.type_params == ()

    assert result.args.vararg is None
    assert result.args.kwarg is None
    assert result.args.posonlyargs == ()
    assert result.args.kwonlyargs == ()
    assert result.args.defaults == ()
    assert result.args.kw_defaults == ()

    assert len(result.args.args) == 1

    argument = result.args.args[0]
    assert argument.arg == "value"
    assert argument.type_comment is None

    argument.annotation = assert_expression_type(
        argument.annotation,
        NameExpressionAnalysis,
    )
    assert argument.annotation.name == "int"

    result.returns = assert_expression_type(
        result.returns,
        NameExpressionAnalysis,
    )
    assert result.returns.name == "str"

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
    assert statement.value.func.name == "str"

    assert len(statement.value.args) == 1

    argument = assert_expression_type(
        statement.value.args[0],
        NameExpressionAnalysis,
    )
    assert argument.name == "value"

    assert statement.value.keywords == ()
