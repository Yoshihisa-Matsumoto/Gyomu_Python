import ast

from gyomu_python_analysis.analysis.analyzers.ast.statement import analyze_statement
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_schema.schemas.python.type.expression import (
    BinaryOperator,
    BinOpExpressionAnalysis,
    CompareExpressionAnalysis,
    CompareOperator,
    DictionaryCompareExpressionAnalysis,
    GeneratorExpressionAnalysis,
    ListCompareExpressionAnalysis,
    NameExpressionAnalysis,
    ReturnStatementAnalysis,
    SetCompareExpressionAnalysis,
    StatementKind,
)
from gyomu_schema.schemas.python.type.structure import LiteralValue

from packages.python_analysis.tests.unit.analysis.analyzers.ast.helper import (
    assert_expression_type,
    find_function,
)


def analyze_comprehension_functions(
    context: SymbolContext,
    function_name: str,
) -> list[ReturnStatementAnalysis]:
    function = find_function("comprehension", function_name)
    target_statements: list[ReturnStatementAnalysis] = []

    for stmt in function.body:
        # logger.debug(f"{type(stmt).__name__}")
        # logger.debug_object(stmt, 6)
        if isinstance(stmt, ast.Return):
            result = analyze_statement(stmt, context, None, False)
            assert isinstance(result, ReturnStatementAnalysis)
            target_statements.append(result)

    return target_statements


def test_list_comprehension(
    context: SymbolContext,
) -> None:
    results = analyze_comprehension_functions(
        context,
        "list_comprehension",
    )

    assert len(results) == 1

    result = results[0]
    assert result.kind == StatementKind.RETURN
    assert isinstance(result, ReturnStatementAnalysis)

    result.value = assert_expression_type(
        result.value,
        ListCompareExpressionAnalysis,
    )

    assert len(result.value.generators) == 1

    generator = result.value.generators[0]

    generator.target = assert_expression_type(
        generator.target,
        NameExpressionAnalysis,
    )
    assert generator.target.name == "value"

    generator.iter = assert_expression_type(
        generator.iter,
        NameExpressionAnalysis,
    )
    assert generator.iter.name == "values"

    assert generator.ifs == ()
    assert generator.is_async is False

    result.value.element = assert_expression_type(
        result.value.element,
        BinOpExpressionAnalysis,
    )
    result.value.element.left = assert_expression_type(
        result.value.element.left,
        NameExpressionAnalysis,
    )
    assert result.value.element.left.name == "value"

    assert result.value.element.op == BinaryOperator.MULT

    result.value.element.right = assert_expression_type(
        result.value.element.right,
        LiteralValue,
    )
    assert result.value.element.right.value == 2


def test_list_comprehension_with_if(
    context: SymbolContext,
) -> None:
    results = analyze_comprehension_functions(
        context,
        "list_comprehension_with_if",
    )

    assert len(results) == 1

    result = results[0]
    assert result.kind == StatementKind.RETURN
    assert isinstance(result, ReturnStatementAnalysis)

    result.value = assert_expression_type(
        result.value,
        ListCompareExpressionAnalysis,
    )

    assert len(result.value.generators) == 1

    generator = result.value.generators[0]

    generator.target = assert_expression_type(
        generator.target,
        NameExpressionAnalysis,
    )
    assert generator.target.name == "value"

    generator.iter = assert_expression_type(
        generator.iter,
        NameExpressionAnalysis,
    )
    assert generator.iter.name == "values"

    assert len(generator.ifs) == 1

    condition = assert_expression_type(
        generator.ifs[0],
        CompareExpressionAnalysis,
    )
    condition.left = assert_expression_type(
        condition.left,
        NameExpressionAnalysis,
    )
    assert condition.left.name == "value"
    assert condition.ops == (CompareOperator.GT,)

    comparator = assert_expression_type(
        condition.comparators[0],
        LiteralValue,
    )
    assert comparator.value == 0

    assert generator.is_async is False

    result.value.element = assert_expression_type(
        result.value.element,
        BinOpExpressionAnalysis,
    )
    result.value.element.left = assert_expression_type(
        result.value.element.left,
        NameExpressionAnalysis,
    )
    assert result.value.element.left.name == "value"
    assert result.value.element.op == BinaryOperator.MULT

    result.value.element.right = assert_expression_type(
        result.value.element.right,
        LiteralValue,
    )
    assert result.value.element.right.value == 2


def test_list_comprehension_multiple_for(
    context: SymbolContext,
) -> None:
    results = analyze_comprehension_functions(
        context,
        "list_comprehension_multiple_for",
    )

    assert len(results) == 1

    result = results[0]
    assert result.kind == StatementKind.RETURN
    assert isinstance(result, ReturnStatementAnalysis)

    result.value = assert_expression_type(
        result.value,
        ListCompareExpressionAnalysis,
    )

    assert len(result.value.generators) == 2

    generator = result.value.generators[0]

    generator.target = assert_expression_type(
        generator.target,
        NameExpressionAnalysis,
    )
    assert generator.target.name == "items"

    generator.iter = assert_expression_type(
        generator.iter,
        NameExpressionAnalysis,
    )
    assert generator.iter.name == "values"

    assert generator.ifs == ()
    assert generator.is_async is False

    generator = result.value.generators[1]

    generator.target = assert_expression_type(
        generator.target,
        NameExpressionAnalysis,
    )
    assert generator.target.name == "value"

    generator.iter = assert_expression_type(
        generator.iter,
        NameExpressionAnalysis,
    )
    assert generator.iter.name == "items"

    assert generator.ifs == ()
    assert generator.is_async is False

    result.value.element = assert_expression_type(
        result.value.element,
        NameExpressionAnalysis,
    )
    assert result.value.element.name == "value"


def test_set_comprehension(
    context: SymbolContext,
) -> None:
    results = analyze_comprehension_functions(
        context,
        "set_comprehension",
    )

    assert len(results) == 1

    result = results[0]
    assert result.kind == StatementKind.RETURN
    assert isinstance(result, ReturnStatementAnalysis)

    result.value = assert_expression_type(
        result.value,
        SetCompareExpressionAnalysis,
    )

    assert len(result.value.generators) == 1

    generator = result.value.generators[0]

    generator.target = assert_expression_type(
        generator.target,
        NameExpressionAnalysis,
    )
    assert generator.target.name == "value"

    generator.iter = assert_expression_type(
        generator.iter,
        NameExpressionAnalysis,
    )
    assert generator.iter.name == "values"

    assert generator.ifs == ()
    assert generator.is_async is False

    result.value.elt = assert_expression_type(
        result.value.elt,
        BinOpExpressionAnalysis,
    )
    result.value.elt.left = assert_expression_type(
        result.value.elt.left,
        NameExpressionAnalysis,
    )
    assert result.value.elt.left.name == "value"
    assert result.value.elt.op == BinaryOperator.MULT

    result.value.elt.right = assert_expression_type(
        result.value.elt.right,
        LiteralValue,
    )
    assert result.value.elt.right.value == 2


def test_dict_comprehension(
    context: SymbolContext,
) -> None:
    results = analyze_comprehension_functions(
        context,
        "dict_comprehension",
    )

    assert len(results) == 1

    result = results[0]
    assert result.kind == StatementKind.RETURN
    assert isinstance(result, ReturnStatementAnalysis)

    result.value = assert_expression_type(
        result.value,
        DictionaryCompareExpressionAnalysis,
    )

    assert len(result.value.generators) == 1

    generator = result.value.generators[0]

    generator.target = assert_expression_type(
        generator.target,
        NameExpressionAnalysis,
    )
    assert generator.target.name == "value"

    generator.iter = assert_expression_type(
        generator.iter,
        NameExpressionAnalysis,
    )
    assert generator.iter.name == "values"

    assert generator.ifs == ()
    assert generator.is_async is False

    result.value.key = assert_expression_type(
        result.value.key,
        NameExpressionAnalysis,
    )
    assert result.value.key.name == "value"

    result.value.value = assert_expression_type(
        result.value.value,
        BinOpExpressionAnalysis,
    )
    result.value.value.left = assert_expression_type(
        result.value.value.left,
        NameExpressionAnalysis,
    )
    assert result.value.value.left.name == "value"
    assert result.value.value.op == BinaryOperator.MULT

    result.value.value.right = assert_expression_type(
        result.value.value.right,
        LiteralValue,
    )
    assert result.value.value.right.value == 2


def test_generator_expression(
    context: SymbolContext,
) -> None:
    results = analyze_comprehension_functions(
        context,
        "generator_expression",
    )

    assert len(results) == 1

    result = results[0]
    assert result.kind == StatementKind.RETURN
    assert isinstance(result, ReturnStatementAnalysis)

    result.value = assert_expression_type(
        result.value,
        GeneratorExpressionAnalysis,
    )

    assert len(result.value.generators) == 1

    generator = result.value.generators[0]

    generator.target = assert_expression_type(
        generator.target,
        NameExpressionAnalysis,
    )
    assert generator.target.name == "value"

    generator.iter = assert_expression_type(
        generator.iter,
        NameExpressionAnalysis,
    )
    assert generator.iter.name == "values"

    assert generator.ifs == ()
    assert generator.is_async is False

    result.value.elt = assert_expression_type(
        result.value.elt,
        BinOpExpressionAnalysis,
    )
    result.value.elt.left = assert_expression_type(
        result.value.elt.left,
        NameExpressionAnalysis,
    )
    assert result.value.elt.left.name == "value"
    assert result.value.elt.op == BinaryOperator.MULT

    result.value.elt.right = assert_expression_type(
        result.value.elt.right,
        LiteralValue,
    )
    assert result.value.elt.right.value == 2


def test_nested_comprehension(
    context: SymbolContext,
) -> None:
    results = analyze_comprehension_functions(
        context,
        "nested_comprehension",
    )

    assert len(results) == 1

    result = results[0]
    assert result.kind == StatementKind.RETURN
    assert isinstance(result, ReturnStatementAnalysis)

    result.value = assert_expression_type(
        result.value,
        ListCompareExpressionAnalysis,
    )

    assert len(result.value.generators) == 2

    generator = result.value.generators[0]

    generator.target = assert_expression_type(
        generator.target,
        NameExpressionAnalysis,
    )
    assert generator.target.name == "items"

    generator.iter = assert_expression_type(
        generator.iter,
        NameExpressionAnalysis,
    )
    assert generator.iter.name == "values"

    assert generator.ifs == ()
    assert generator.is_async is False

    generator = result.value.generators[1]

    generator.target = assert_expression_type(
        generator.target,
        NameExpressionAnalysis,
    )
    assert generator.target.name == "value"

    generator.iter = assert_expression_type(
        generator.iter,
        NameExpressionAnalysis,
    )
    assert generator.iter.name == "items"

    assert len(generator.ifs) == 1

    condition = assert_expression_type(
        generator.ifs[0],
        CompareExpressionAnalysis,
    )
    condition.left = assert_expression_type(
        condition.left,
        NameExpressionAnalysis,
    )
    assert condition.left.name == "value"
    assert condition.ops == (CompareOperator.GT,)

    comparator = assert_expression_type(
        condition.comparators[0],
        LiteralValue,
    )
    assert comparator.value == 0

    assert generator.is_async is False

    result.value.element = assert_expression_type(
        result.value.element,
        BinOpExpressionAnalysis,
    )
    result.value.element.left = assert_expression_type(
        result.value.element.left,
        NameExpressionAnalysis,
    )
    assert result.value.element.left.name == "value"
    assert result.value.element.op == BinaryOperator.MULT

    result.value.element.right = assert_expression_type(
        result.value.element.right,
        LiteralValue,
    )
    assert result.value.element.right.value == 2
