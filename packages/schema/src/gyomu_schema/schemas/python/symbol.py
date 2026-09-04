from typing import Annotated

from pydantic import Field

from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.function_analysis import (
    FunctionAnalysis,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis

type SymbolAnalysis = Annotated[
    VariableAnalysis | ClassAnalysis | FunctionAnalysis,
    Field(discriminator="kind"),
]
