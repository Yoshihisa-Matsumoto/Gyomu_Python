import ast
from dataclasses import dataclass

from gyomu_schema.schemas.python.types import PythonPath


@dataclass(frozen=True)
class AstClassFunctionKey:
    """Represents a lookup key for a class or function based on its name and end
    line.
    """

    name: str
    """The name of the class or function."""

    end_line: int
    """The end line number of the class or function definition."""


def _analyze_ast_module(
    source: str, source_path: PythonPath
) -> dict[AstClassFunctionKey, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef]:
    """Analyzes a Python module from source code and builds a class/function index.

    Args:
        source (str): The Python source code content.
        source_path (PythonPath): The file path of the source code.

    Returns:
        dict[AstClassFunctionKey, ast.ClassDef | ast.FunctionDef |
            ast.AsyncFunctionDef]: A dictionary mapping AST class or function keys to
            their definitions.
    """
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
    """Returns the provided AST index if available, otherwise analyzes the module to
    build one.

    Args:
        index (dict[AstClassFunctionKey, ast.ClassDef | ast.FunctionDef |
            ast.AsyncFunctionDef] | None): An existing index to reuse, if available.
        source (str): The Python source code content.
        source_path (PythonPath): The file path of the source code.

    Returns:
        dict[AstClassFunctionKey, ast.ClassDef | ast.FunctionDef |
            ast.AsyncFunctionDef]: The AST class and function index.
    """
    if index is not None:
        return index
    return _analyze_ast_module(source=source, source_path=source_path)


def build_class_function_index(
    tree: ast.Module | ast.ClassDef,
) -> dict[AstClassFunctionKey, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef]:
    """Builds an index of classes and functions from an AST tree.

    Args:
        tree (ast.Module | ast.ClassDef): The AST module or class definition node to
            process.

    Returns:
        dict[AstClassFunctionKey, ast.ClassDef | ast.FunctionDef |
            ast.AsyncFunctionDef]: A dictionary mapping AstClassFunctionKey to class and
            function definitions.
    """
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
