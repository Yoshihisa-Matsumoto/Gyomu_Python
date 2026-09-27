from typing import Annotated

from pydantic import Field

from gyomu_schema.schemas.python.class_analysis import (
    ClassAnalysis,
    ClassTypeAliasAnalysis,
    ClassVariableAnalysis,
    InnerClassAnalysis,
)
from gyomu_schema.schemas.python.function_analysis import (
    FunctionAnalysis,
)
from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.variable import VariableAnalysis

type SymbolAnalysis = Annotated[
    VariableAnalysis | ClassAnalysis | FunctionAnalysis | TypeAliasAnalysis,
    Field(discriminator="kind"),
]
"""Defines a discriminated union of Python symbol analysis types including variables,
classes, functions, and type aliases.
"""

type MemberAnalysis = Annotated[
    InnerClassAnalysis
    | ClassVariableAnalysis
    | ClassTypeAliasAnalysis
    | MethodAnalysis,
    Field(discriminator="kind"),
]
"""Defines a discriminated union of Python class member analysis types including inner
classes, class variables, class type aliases, and methods.
"""
