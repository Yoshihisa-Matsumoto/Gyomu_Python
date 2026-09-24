import ast
from dataclasses import dataclass

from gyomu_schema.schemas.python.types import PythonPath


@dataclass(frozen=True)
class AstClassFunctionKey:
    name: str
    end_line: int


def _analyze_ast_module(
    source: str, source_path: PythonPath
) -> dict[AstClassFunctionKey, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef]:
    tree = ast.parse(source=source, filename=source_path)
    return build_class_function_index(tree)


def get_ast_index(
    index: dict[
        AstClassFunctionKey, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
    ]
    | None,
    source: str,
    source_path: PythonPath,
) -> dict[AstClassFunctionKey, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef]:
    if index is not None:
        return index
    return _analyze_ast_module(source=source, source_path=source_path)


def build_class_function_index(
    tree: ast.Module | ast.ClassDef,
) -> dict[AstClassFunctionKey, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef]:
    index: dict[
        AstClassFunctionKey, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
    ] = {}

    for child in ast.iter_child_nodes(tree):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            assert child.end_lineno
            key = AstClassFunctionKey(
                child.name,
                child.end_lineno,
            )
            index[key] = child
    return index
