import ast
from pathlib import Path

from gyomu_schema.schemas.python.type.expression import ExpressionAnalysis

from packages.python_analysis.python_analysis_test_support.helpers import FIXTURES_ROOT


def get_module(module_name: str) -> ast.Module:
    source_file_path = FIXTURES_ROOT / Path("src/analysis/ast") / f"{module_name}.py"
    source = source_file_path.read_text()
    module = ast.parse(source)
    return module


def find_function(module_name: str, function_name: str) -> ast.FunctionDef:
    target_method: ast.FunctionDef | None = None
    for method in ast.iter_child_nodes(get_module(module_name)):
        if isinstance(method, ast.FunctionDef) and method.name == function_name:
            target_method = method

    assert target_method is not None
    return target_method


def get_function_statement(method: ast.FunctionDef, index: int) -> ast.stmt:
    statement = method.body[index]
    assert statement

    return statement


def assert_expression_type[T: ExpressionAnalysis](
    expression: ExpressionAnalysis,
    expected_type: type[T],
) -> T:
    assert isinstance(expression, expected_type)
    return expression
