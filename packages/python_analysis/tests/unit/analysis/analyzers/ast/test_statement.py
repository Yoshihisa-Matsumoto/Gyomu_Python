import ast

import pytest
from gyomu_python_analysis.analysis.analyzers.ast.statement import (
    analyze_expression,
    analyze_statement,
)
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_schema.schemas.python.type.expression import (
    NoneExpressionAnalysis,
    UnknownExpressionAnalysis,
    UnknownStatementAnalysis,
)
from pytest_mock import MockerFixture

from packages.schema.schema_test_support.helpers import create_declaration_identity


@pytest.fixture
def context() -> SymbolContext:
    return SymbolContext(
        declaration=create_declaration_identity("test"),
        dependencies=[],
        source_lines=[],
        line_start_offsets=[],
    )


@pytest.mark.parametrize(
    ("source", "analyzer_name"),
    [
        ("x = 1", "_analyze_assign"),
        ("return 1", "_analyze_return"),
        ("foo()", "_analyze_expression"),
        ("while x:\n    pass", "_analyze_while"),
        ("if x:\n    pass", "_analyze_if"),
        ("try:\n    pass\nexcept Exception:\n    pass", "_analyze_try"),
        ("assert x", "_analyze_assert"),
        ("raise ValueError()", "_analyze_raise"),
        ("x: int = 1", "_analyze_annotation_assign"),
        ("for x in xs:\n    pass", "_analyze_for"),
        ("with open('x'):\n    pass", "_analyze_with"),
        ("pass", None),
        ("break", None),
        ("continue", None),
        ("x += 1", "_analyze_augassign"),
        ("match x:\n    case 1:\n        pass", "_analyze_match"),
        ("def foo():\n    pass", "_analyze_function"),
        ("async def foo():\n    pass", "_analyze_function"),
        ("global x", None),
    ],
)
def test_analyze_statement_dispatches_to_correct_analyzer(
    source: str,
    analyzer_name: str | None,
    context: SymbolContext,
    mocker: MockerFixture,
) -> None:
    statement = ast.parse(source).body[0]

    if analyzer_name is None:
        result = analyze_statement(
            statement,
            context,
            None,
            need_registration_dependency=False,
        )

        assert result is not None
        return

    analyzer = mocker.patch(
        f"gyomu_python_analysis.analysis.analyzers.ast.statement.{analyzer_name}"
    )

    analyze_statement(
        statement,
        context,
        None,
        need_registration_dependency=False,
    )

    analyzer.assert_called_once_with(
        statement,
        context,
        None,
        False,
    )


@pytest.mark.parametrize(
    ("expression", "analyzer_name"),
    [
        (ast.Constant(value=1), "_analyze_const"),
        (ast.Name(id="x"), "analyze_expression_name"),
        (ast.List(elts=[]), "analyze_array"),
        (ast.Dict(keys=[], values=[]), "analyze_dictionary"),
        (
            ast.Call(
                func=ast.Name(id="foo"),
                args=[],
                keywords=[],
            ),
            "_analyze_call",
        ),
        (
            ast.Attribute(
                value=ast.Name(id="foo"),
                attr="bar",
            ),
            "_analyze_attribute",
        ),
        (
            ast.JoinedStr(values=[]),
            "_analyze_joinedstr",
        ),
        (
            ast.Tuple(elts=[]),
            "analyze_tuple",
        ),
        (
            ast.BinOp(
                left=ast.Constant(value=1),
                op=ast.Add(),
                right=ast.Constant(value=2),
            ),
            "_analyze_binop",
        ),
        (
            ast.BoolOp(
                op=ast.And(),
                values=[
                    ast.Name(id="x"),
                    ast.Name(id="y"),
                ],
            ),
            "_analyze_boolop",
        ),
        (
            ast.FormattedValue(
                value=ast.Name(id="x"),
                conversion=114,
            ),
            "_analyze_formatted_value",
        ),
        (
            ast.Compare(
                left=ast.Name(id="x"),
                ops=[ast.Eq()],
                comparators=[ast.Constant(value=1)],
            ),
            "_analyze_compare",
        ),
        (
            ast.Await(
                value=ast.Call(
                    func=ast.Name(id="foo"),
                    args=[],
                    keywords=[],
                ),
            ),
            "_analyze_await",
        ),
        (
            ast.Subscript(
                value=ast.Name(id="x"),
                slice=ast.Constant(value=0),
            ),
            "_analyze_subscript",
        ),
        (
            ast.DictComp(
                key=ast.Name(id="key"),
                value=ast.Name(id="value"),
                generators=[],
            ),
            "_analyze_dict_compare",
        ),
        (
            ast.ListComp(
                elt=ast.Name(id="x"),
                generators=[],
            ),
            "_analyze_list_compare",
        ),
        (
            ast.UnaryOp(
                op=ast.USub(),
                operand=ast.Name(id="x"),
            ),
            "_analyze_unaryop",
        ),
        (
            ast.Starred(
                value=ast.Name(id="x"),
                ctx=ast.Load(),
            ),
            "_analyze_starred",
        ),
        (
            ast.Set(elts=[]),
            "analyze_set",
        ),
        (
            ast.SetComp(
                elt=ast.Name(id="x"),
                generators=[],
            ),
            "_analyze_set_compare",
        ),
        (
            ast.Lambda(
                args=ast.arguments(
                    posonlyargs=[],
                    args=[],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=ast.Constant(value=1),
            ),
            "_analyze_lambda",
        ),
        (
            ast.YieldFrom(
                value=ast.Name(id="x"),
            ),
            "_analyze_yieldfrom",
        ),
        (
            ast.IfExp(
                test=ast.Name(id="condition"),
                body=ast.Constant(value=1),
                orelse=ast.Constant(value=2),
            ),
            "_analyze_ifexp",
        ),
        (
            ast.Yield(
                value=ast.Name(id="x"),
            ),
            "_analyze_yield",
        ),
        (
            ast.GeneratorExp(
                elt=ast.Name(id="x"),
                generators=[],
            ),
            "_analyze_generator_expression",
        ),
        (
            ast.Slice(
                lower=ast.Constant(value=1),
                upper=ast.Constant(value=10),
                step=None,
            ),
            "analyze_slice",
        ),
        (
            ast.NamedExpr(
                target=ast.Name(id="x", ctx=ast.Store()),
                value=ast.Constant(value=1),
            ),
            "_analyze_named",
        ),
    ],
)
def test_analyze_expression_dispatches_to_correct_analyzer2(
    expression: ast.expr,
    analyzer_name: str,
    context: SymbolContext,
    mocker: MockerFixture,
):
    analyzer = mocker.patch(
        f"gyomu_python_analysis.analysis.analyzers.ast.statement.{analyzer_name}",
        return_value=UnknownExpressionAnalysis(),
    )

    analyze_expression(
        expression,
        context,
        None,
        False,
    )

    analyzer.assert_called_once_with(
        expression,
        context,
        None,
        False,
    )


def test_analyze_expression_none_returns_none_expression_analysis(
    context: SymbolContext,
) -> None:
    result = analyze_expression(
        None,
        context,
        None,
        need_registration_dependency=False,
    )

    assert isinstance(result, NoneExpressionAnalysis)


class UnsupportedExpression(ast.expr):
    pass


def test_analyze_expression_unsupported_returns_unknown(
    context: SymbolContext,
) -> None:
    result = analyze_expression(
        UnsupportedExpression(),
        context,
        None,
        need_registration_dependency=False,
    )

    assert isinstance(result, UnknownExpressionAnalysis)


class UnsupportedStatement(ast.stmt):
    pass


def test_analyze_statement_unsupported_returns_unknown(
    context: SymbolContext,
) -> None:
    result = analyze_statement(
        UnsupportedStatement(),
        context,
        None,
        need_registration_dependency=False,
    )

    assert isinstance(result, UnknownStatementAnalysis)
