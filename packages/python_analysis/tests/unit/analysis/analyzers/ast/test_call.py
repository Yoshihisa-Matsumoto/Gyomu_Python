from gyomu_python_analysis.analysis.analyzers.ast.statement import analyze_statement
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_schema.schemas.python.type.expression import (
    AttributeExpressionAnalysis,
    CallExpressionAnalysis,
    DictionaryExpressionAnalysis,
    ExpressionKind,
    ExpressionWithoutConstant,
    NameExpressionAnalysis,
    ReturnStatementAnalysis,
    StarredExpressionAnalysis,
    StatementKind,
)
from gyomu_schema.schemas.python.type.structure import LiteralValue

from packages.python_analysis.tests.unit.analysis.analyzers.ast.helper import (
    assert_expression_type,
    find_function,
    get_function_statement,
)


def analyze_call_function(
    context: SymbolContext,
    function_name: str,
) -> ExpressionWithoutConstant:
    function = find_function("call", function_name)
    statement = get_function_statement(function, 0)

    result = analyze_statement(statement, context, None, False)

    assert result.kind == StatementKind.RETURN
    assert isinstance(result, ReturnStatementAnalysis)
    assert not isinstance(result.value, LiteralValue)
    return result.value


def test_simple_call(
    context: SymbolContext,
) -> None:
    result = analyze_call_function(context, "simple_call")
    result = assert_expression_type(result, CallExpressionAnalysis)
    result.func = assert_expression_type(result.func, NameExpressionAnalysis)
    assert result.func.name == "convert"

    assert len(result.args) == 1

    argument = assert_expression_type(result.args[0], NameExpressionAnalysis)

    assert argument.name == "value"

    assert result.keywords == ()


def test_positional_call(
    context: SymbolContext,
) -> None:
    result = analyze_call_function(context, "positional_call")

    result = assert_expression_type(result, CallExpressionAnalysis)

    result.func = assert_expression_type(result.func, NameExpressionAnalysis)
    assert result.func.name == "combine"

    assert len(result.args) == 2

    first = assert_expression_type(result.args[0], NameExpressionAnalysis)
    assert first.kind == ExpressionKind.NAME
    assert first.name == "value"

    second = assert_expression_type(result.args[1], CallExpressionAnalysis)
    assert second.kind == ExpressionKind.CALL
    second.func = assert_expression_type(second.func, NameExpressionAnalysis)
    assert second.func.kind == ExpressionKind.NAME
    assert second.func.name == "convert"

    assert len(second.args) == 1
    arg = assert_expression_type(second.args[0], NameExpressionAnalysis)

    assert arg.name == "value"

    assert result.keywords == ()


def test_keyword_call(
    context: SymbolContext,
) -> None:
    result = analyze_call_function(context, "keyword_call")

    result = assert_expression_type(result, CallExpressionAnalysis)

    result.func = assert_expression_type(result.func, NameExpressionAnalysis)
    assert result.func.name == "combine"

    assert len(result.args) == 1

    argument = assert_expression_type(result.args[0], NameExpressionAnalysis)
    assert argument.name == "value"

    assert len(result.keywords) == 2

    prefix = result.keywords[0]
    assert prefix.arg == "prefix"
    prefix.value = assert_expression_type(prefix.value, LiteralValue)
    assert prefix.value.value == "value"

    suffix = result.keywords[1]
    assert suffix.arg == "suffix"
    suffix.value = assert_expression_type(suffix.value, LiteralValue)
    assert suffix.value.value == "!"


def test_attribute_call(
    context: SymbolContext,
) -> None:
    result = analyze_call_function(context, "attribute_call")

    result = assert_expression_type(result, CallExpressionAnalysis)

    result.func = assert_expression_type(result.func, AttributeExpressionAnalysis)
    assert result.func.attribute == "execute"

    result.func.value = assert_expression_type(
        result.func.value,
        NameExpressionAnalysis,
    )
    assert result.func.value.name == "service"

    assert len(result.args) == 1

    argument = assert_expression_type(result.args[0], NameExpressionAnalysis)
    assert argument.name == "value"

    assert result.keywords == ()


def test_nested_call(
    context: SymbolContext,
) -> None:
    result = analyze_call_function(context, "nested_call")

    result = assert_expression_type(result, CallExpressionAnalysis)

    result.func = assert_expression_type(result.func, AttributeExpressionAnalysis)
    assert result.func.attribute == "execute"

    result.func.value = assert_expression_type(
        result.func.value,
        NameExpressionAnalysis,
    )
    assert result.func.value.name == "service"

    assert len(result.args) == 1

    argument = assert_expression_type(result.args[0], CallExpressionAnalysis)

    argument.func = assert_expression_type(
        argument.func,
        NameExpressionAnalysis,
    )
    assert argument.func.name == "create_value"

    assert len(argument.args) == 1

    nested_argument = assert_expression_type(
        argument.args[0],
        NameExpressionAnalysis,
    )
    assert nested_argument.name == "value"

    assert len(result.keywords) == 1

    option = result.keywords[0]
    assert option.arg == "option"

    option.value = assert_expression_type(
        option.value,
        CallExpressionAnalysis,
    )
    option.value.func = assert_expression_type(
        option.value.func,
        NameExpressionAnalysis,
    )
    assert option.value.func.name == "build_option"

    assert len(option.value.args) == 1
    option_argument = assert_expression_type(
        option.value.args[0],
        NameExpressionAnalysis,
    )
    assert option_argument.name == "value"


def test_starred_call(
    context: SymbolContext,
) -> None:
    result = analyze_call_function(context, "starred_call")

    result = assert_expression_type(result, CallExpressionAnalysis)

    result.func = assert_expression_type(result.func, NameExpressionAnalysis)
    assert result.func.name == "combine"

    assert len(result.args) == 1

    argument = assert_expression_type(result.args[0], StarredExpressionAnalysis)

    argument.value = assert_expression_type(
        argument.value,
        NameExpressionAnalysis,
    )
    assert argument.value.name == "values"

    assert result.keywords == ()


def test_double_starred_call(
    context: SymbolContext,
) -> None:
    result = analyze_call_function(context, "double_starred_call")

    result = assert_expression_type(result, CallExpressionAnalysis)

    result.func = assert_expression_type(result.func, NameExpressionAnalysis)
    assert result.func.name == "combine"

    assert result.args == ()

    assert len(result.keywords) == 1

    keyword = result.keywords[0]
    assert keyword.arg is None

    keyword.value = assert_expression_type(
        keyword.value,
        NameExpressionAnalysis,
    )
    assert keyword.value.name == "options"


def test_complex_call(
    context: SymbolContext,
) -> None:
    result = analyze_call_function(context, "complex_call")

    result = assert_expression_type(result, CallExpressionAnalysis)

    result.func = assert_expression_type(result.func, AttributeExpressionAnalysis)
    assert result.func.attribute == "execute"

    result.func.value = assert_expression_type(
        result.func.value,
        NameExpressionAnalysis,
    )
    assert result.func.value.name == "service"

    assert len(result.args) == 2

    first = assert_expression_type(result.args[0], CallExpressionAnalysis)
    first.func = assert_expression_type(first.func, NameExpressionAnalysis)
    assert first.func.name == "convert"

    assert len(first.args) == 1
    first_arg = assert_expression_type(
        first.args[0],
        NameExpressionAnalysis,
    )
    assert first_arg.name == "value"

    second = assert_expression_type(result.args[1], StarredExpressionAnalysis)
    second.value = assert_expression_type(
        second.value,
        NameExpressionAnalysis,
    )
    assert second.value.name == "values"

    assert len(result.keywords) == 2

    option = result.keywords[0]
    assert option.arg == "option"

    option.value = assert_expression_type(
        option.value,
        CallExpressionAnalysis,
    )
    option.value.func = assert_expression_type(
        option.value.func,
        NameExpressionAnalysis,
    )
    assert option.value.func.name == "build_option"

    assert len(option.value.args) == 1
    option_arg = assert_expression_type(
        option.value.args[0],
        NameExpressionAnalysis,
    )
    assert option_arg.name == "value"

    expanded = result.keywords[1]
    assert expanded.arg is None

    expanded.value = assert_expression_type(
        expanded.value,
        DictionaryExpressionAnalysis,
    )
