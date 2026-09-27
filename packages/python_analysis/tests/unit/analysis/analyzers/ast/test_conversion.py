import ast

import pytest
from gyomu_python_analysis.analysis.analyzers.ast.statement import (
    _convert_binop_operator,
    _convert_boolop_operator,
    _convert_compare_operator,
    _convert_formatted_value_conversion,
    _convert_unary_operator,
)
from gyomu_schema.schemas.python.type.expression import (
    BinaryOperator,
    BoolOperator,
    CompareOperator,
    FormattedConversion,
    UnaryOperator,
)


@pytest.mark.parametrize(
    ("operator", "expected"),
    [
        (ast.Add(), BinaryOperator.ADD),
        (ast.Sub(), BinaryOperator.SUB),
        (ast.Mult(), BinaryOperator.MULT),
        (ast.MatMult(), BinaryOperator.MAT_MULT),
        (ast.Div(), BinaryOperator.DIV),
        (ast.Mod(), BinaryOperator.MOD),
        (ast.Pow(), BinaryOperator.POW),
        (ast.LShift(), BinaryOperator.L_SHIFT),
        (ast.RShift(), BinaryOperator.R_SHIFT),
        (ast.BitOr(), BinaryOperator.BIT_OR),
        (ast.BitXor(), BinaryOperator.BIT_XOR),
        (ast.BitAnd(), BinaryOperator.BIT_AND),
        (ast.FloorDiv(), BinaryOperator.FLOOR_DIV),
    ],
)
def test_convert_binop_operator(
    operator: ast.operator,
    expected: BinaryOperator,
):
    assert _convert_binop_operator(operator) == expected


def test_convert_binop_operator_unsupported():
    with pytest.raises(ValueError, match="Unsupported binary operator: USub"):
        _convert_binop_operator(ast.USub())  # type: ignore


@pytest.mark.parametrize(
    ("operator", "expected"),
    [
        (ast.Invert(), UnaryOperator.INVERT),
        (ast.Not(), UnaryOperator.NOT),
        (ast.UAdd(), UnaryOperator.U_ADD),
        (ast.USub(), UnaryOperator.U_SUB),
    ],
)
def test_convert_unary_operator(
    operator: ast.unaryop,
    expected: UnaryOperator,
):
    assert _convert_unary_operator(operator) == expected


def test_convert_unary_operator_unsupported():
    with pytest.raises(ValueError, match="Unsupported unary operator: Add"):
        _convert_unary_operator(ast.Add())  # type: ignore


@pytest.mark.parametrize(
    ("operator", "expected"),
    [
        (ast.And(), BoolOperator.AND),
        (ast.Or(), BoolOperator.OR),
    ],
)
def test_convert_boolop_operator(
    operator: ast.boolop,
    expected: BoolOperator,
):
    assert _convert_boolop_operator(operator) == expected


def test_convert_boolop_operator_unsupported():
    with pytest.raises(ValueError, match="Unsupported bool operator: Add"):
        _convert_boolop_operator(ast.Add())  # type: ignore


@pytest.mark.parametrize(
    ("operator", "expected"),
    [
        (ast.Eq(), CompareOperator.EQ),
        (ast.NotEq(), CompareOperator.NOT_EQ),
        (ast.Lt(), CompareOperator.LT),
        (ast.LtE(), CompareOperator.LT_E),
        (ast.Gt(), CompareOperator.GT),
        (ast.GtE(), CompareOperator.GT_E),
        (ast.Is(), CompareOperator.IS),
        (ast.IsNot(), CompareOperator.IS_NOT),
        (ast.In(), CompareOperator.IN),
        (ast.NotIn(), CompareOperator.NOT_IN),
    ],
)
def test_convert_compare_operator(
    operator: ast.cmpop,
    expected: CompareOperator,
):
    assert _convert_compare_operator(operator) == expected


def test_convert_compare_operator_unsupported():
    with pytest.raises(ValueError, match="Unsupported comparison operator: Add"):
        _convert_compare_operator(ast.Add())  # type: ignore


@pytest.mark.parametrize(
    ("conversion", "expected"),
    [
        (115, FormattedConversion.STR),
        (114, FormattedConversion.REPR),
        (97, FormattedConversion.ASCII),
        (-1, FormattedConversion.NONE),
    ],
)
def test_convert_formatted_value_conversion(
    conversion: int,
    expected: FormattedConversion,
):
    assert _convert_formatted_value_conversion(conversion) == expected


def test_convert_formatted_value_conversion_unsupported():
    with pytest.raises(
        ValueError,
        match="Unsupported formatted value conversion: 120",
    ):
        _convert_formatted_value_conversion(120)
