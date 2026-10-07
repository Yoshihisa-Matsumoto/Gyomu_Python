import ast
from dataclasses import dataclass

from gyomu_schema.schemas.python.types import PythonPath

type AstTargetSymbolType = (
    ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef | ast.Assign | ast.AnnAssign
)
"""Represents target AST nodes for symbol analysis."""


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
) -> dict[
    AstClassFunctionKey,
    AstTargetSymbolType,
]:
    """Analyzes a Python module from source code and builds a class/function index.

    Args:
        source (str): The Python source code content.
        source_path (PythonPath): The file path of the source code.

    Returns:
        dict[AstClassFunctionKey, AstTargetSymbolType]: A dictionary mapping AST class
            or function keys to
            their definitions.
    """
    tree = ast.parse(source=source, filename=source_path)
    return build_class_function_index(tree)


def get_ast_index(
    index: dict[
        AstClassFunctionKey,
        AstTargetSymbolType,
    ]
    | None,
    source: str,
    source_path: PythonPath,
) -> dict[
    AstClassFunctionKey,
    AstTargetSymbolType,
]:
    """Returns the provided AST index if available, otherwise analyzes the module to
    build one.

    Args:
        index (str): The Python source code content.
        source (str): The Python source code content.
        source_path (PythonPath): The file path of the source code.

    Returns:
        dict[AstClassFunctionKey, AstTargetSymbolType]: The AST class and function
            index.
    """
    if index is not None:
        return index
    return _analyze_ast_module(source=source, source_path=source_path)


def build_class_function_index(
    tree: ast.Module | ast.ClassDef,
) -> dict[
    AstClassFunctionKey,
    AstTargetSymbolType,
]:
    """Builds an index of classes and functions from an AST tree.

    Args:
        tree (ast.Module | ast.ClassDef): The AST module or class definition node to
            process.

    Returns:
        dict[AstClassFunctionKey, AstTargetSymbolType]: A dictionary mapping
            AstClassFunctionKey to class and
            function definitions.
    """
    index: dict[
        AstClassFunctionKey,
        AstTargetSymbolType,
    ] = {}

    # logger.debug("build_class_function_index")
    for child in ast.iter_child_nodes(tree):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            assert child.end_lineno
            key = AstClassFunctionKey(
                child.name,
                child.end_lineno,
            )
            index[key] = child
        if isinstance(child, ast.Assign):  # noqa: SIM102
            # logger.debug_object(child)
            if child.end_lineno is not None:
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        key = AstClassFunctionKey(target.id, child.end_lineno)
                        index[key] = child
        if isinstance(child, ast.AnnAssign):  # noqa: SIM102
            # logger.debug_object(child)
            if child.end_lineno is not None:  # noqa: SIM102
                if isinstance(child.target, ast.Name):
                    key = AstClassFunctionKey(child.target.id, child.end_lineno)
                    index[key] = child
    return index
