from griffe import Attribute, Class, Function
from gyomu_python_analysis.analysis.analyzers.functions import (
    _get_function_parameter_kind,
)
from gyomu_python_analysis.analysis.analyzers.internal.common import (
    build_member_common,
    build_symbol_common,
)
from gyomu_python_analysis.analysis.analyzers.types import analyze_type
from gyomu_schema.schemas.python.class_analysis import (
    ClassAnalysis,
    ClassVariableAnalysis,
)
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.member_analysis import MemberKind
from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis
from gyomu_schema.schemas.python.symbol_base import SymbolKind


def analyze_class(
    cls: Class,
    name: str,
    source_lines: list[str],
) -> ClassAnalysis:
    parameters: list[ClassVariableAnalysis] = []
    methods: list[MethodAnalysis] = []
    inner_classes: list[ClassAnalysis] = []
    # retrieve constructor location if it exists
    constructor_location: SourceLocation | None = None
    if "__init__" in cls.members:
        init_member = cls.members["__init__"]
        if isinstance(init_member, Function):
            constructor_common = build_member_common(
                symbol=init_member,
                name="__init__",
                parent_location=None,
                source_lines=source_lines,
            )
            constructor_location = constructor_common["location"]

    # retrieve class variables
    for member_name, member in cls.members.items():
        if isinstance(member, Attribute):
            print(member_name)
            parameters.append(
                ClassVariableAnalysis(
                    **build_member_common(
                        symbol=member,
                        name=member_name,
                        parent_location=constructor_location,
                        source_lines=source_lines,
                    ),
                    docstring=None,
                    decorators=tuple([]),
                    kind=MemberKind.VARIABLE,
                    type=analyze_type(member.annotation),
                    value_source=str(member.value)
                    if member.value is not None
                    else None,
                )
            )

    # retrieve class methods
    for method_name, method in cls.members.items():
        if isinstance(method, Function):
            method_parameters: list[ParameterAnalysis] = []
            for param in method.parameters:
                method_parameters.append(
                    ParameterAnalysis(
                        name=param.name,
                        kind=_get_function_parameter_kind(param.kind),
                        type=analyze_type(param.annotation),
                        default=None,
                    )
                )
            methods.append(
                MethodAnalysis(
                    **build_member_common(
                        symbol=method,
                        name=method_name,
                        parent_location=constructor_location,
                        source_lines=source_lines,
                    ),
                    kind=MemberKind.METHOD,
                    docstring=None,
                    decorators=tuple([]),
                    parameters=tuple(method_parameters),
                    return_type=None,
                    is_async="async" in method.labels,
                )
            )
    # retrieve inner classes
    for inner_class_name, inner_class in cls.members.items():
        if isinstance(inner_class, Class):
            inner_classes.append(
                analyze_class(
                    cls=inner_class,
                    name=inner_class_name,
                    source_lines=source_lines,
                )
            )

    # pprint(cls.as_dict())
    return ClassAnalysis(
        **build_symbol_common(
            symbol=cls,
            name=name,
            source_lines=source_lines,
        ),
        kind=SymbolKind.CLASS,
        docstring=None,
        decorators=tuple([]),
        dependencies=[],
        variables=tuple(parameters),
        bases=tuple([]),
        methods=tuple(methods),
        pydantic=None,
        inner_classes=tuple(inner_classes),
    )
