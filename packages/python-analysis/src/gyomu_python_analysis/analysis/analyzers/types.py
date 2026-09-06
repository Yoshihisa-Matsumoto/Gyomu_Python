from __future__ import annotations

from griffe import Expr
from gyomu_schema.schemas.python.type.structure import NoneStructureAnalysis
from gyomu_schema.schemas.python.type.type_analysis import (
    TypeAnalysis,
)

from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_python_analysis.analysis.analyzers.expression.expr import analyze_expression


def analyze_type(
    annotation: str | Expr | None, context: SymbolContext
) -> TypeAnalysis | None:
    if annotation is None:
        return None
    if isinstance(annotation, str):
        # print(annotation)
        if annotation == "None":
            return TypeAnalysis(text=annotation, structure=NoneStructureAnalysis())
        return TypeAnalysis(text=annotation)
    if isinstance(annotation, Expr):
        text = str(annotation)
        print(annotation.as_dict())
        return TypeAnalysis(
            text=text, structure=analyze_expression(annotation, context)
        )
    raise ValueError(f"Unsupported annotation type: {type(annotation)}")
