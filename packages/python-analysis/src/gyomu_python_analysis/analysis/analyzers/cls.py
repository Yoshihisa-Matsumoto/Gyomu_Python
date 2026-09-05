from griffe import Attribute, Class, Function
from gyomu_python_analysis.analysis.analyzers.docstring import analyze_docstring
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
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis


def _retrieve_constructor_location(
    cls: Class, source_lines: list[str]
) -> SourceLocation | None:
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
    return constructor_location


def _build_class_variables(
    cls: Class, parent_location: SourceLocation | None, source_lines: list[str]
) -> list[ClassVariableAnalysis]:
    variables: list[ClassVariableAnalysis] = []
    for member_name, member in cls.members.items():
        if isinstance(member, Attribute):
            variables.append(
                _build_class_variable_analysis(
                    member=member,
                    name=member_name,
                    parent_location=parent_location,
                    source_lines=source_lines,
                )
            )
    return variables


def _build_class_variable_analysis(
    member: Attribute,
    name: str,
    parent_location: SourceLocation | None,
    source_lines: list[str],
) -> ClassVariableAnalysis:
    variable_common = build_member_common(
        symbol=member,
        name=name,
        parent_location=parent_location,
        source_lines=source_lines,
    )
    return ClassVariableAnalysis(
        **variable_common,
        docstring=analyze_docstring(
            member.docstring,
            source_lines=source_lines,
        ),
        decorators=tuple([]),
        kind=MemberKind.VARIABLE,
        type=analyze_type(member.annotation),
        value_source=str(member.value) if member.value is not None else None,
    )


def _build_class_method_analysis(
    member: Function,
    name: str,
    parent_location: SourceLocation | None,
    source_lines: list[str],
) -> MethodAnalysis:
    method_parameters: list[ParameterAnalysis] = []
    for param in member.parameters:
        method_parameters.append(
            ParameterAnalysis(
                name=param.name,
                kind=_get_function_parameter_kind(param.kind),
                type=analyze_type(param.annotation),
                default=None,
            )
        )
    method_common = build_member_common(
        symbol=member,
        name=name,
        parent_location=parent_location,
        source_lines=source_lines,
    )
    return MethodAnalysis(
        **method_common,
        kind=MemberKind.METHOD,
        docstring=analyze_docstring(
            member.docstring,
            source_lines=source_lines,
        ),
        decorators=tuple([]),
        parameters=tuple(method_parameters),
        return_type=None,
        is_async="async" in member.labels,
    )


def _build_class_methods(
    cls: Class, parent_location: SourceLocation | None, source_lines: list[str]
) -> list[MethodAnalysis]:
    methods: list[MethodAnalysis] = []
    for member_name, member in cls.members.items():
        if isinstance(member, Function):
            methods.append(
                _build_class_method_analysis(
                    member=member,
                    name=member_name,
                    parent_location=parent_location,
                    source_lines=source_lines,
                )
            )
    return methods


def _build_inner_classes(cls: Class, source_lines: list[str]) -> list[ClassAnalysis]:
    inner_classes: list[ClassAnalysis] = []
    for member_name, member in cls.members.items():
        if isinstance(member, Class):
            inner_classes.append(
                analyze_class(
                    cls=member,
                    name=member_name,
                    source_lines=source_lines,
                )
            )
    return inner_classes


def analyze_class(
    cls: Class,
    name: str,
    source_lines: list[str],
) -> ClassAnalysis:
    bases: list[TypeAnalysis] = [
        analyzed for base in cls.bases if (analyzed := analyze_type(base)) is not None
    ]

    constructor_location: SourceLocation | None = _retrieve_constructor_location(
        cls, source_lines
    )

    parameters: list[ClassVariableAnalysis] = _build_class_variables(
        cls=cls, parent_location=constructor_location, source_lines=source_lines
    )

    methods: list[MethodAnalysis] = _build_class_methods(
        cls=cls, parent_location=constructor_location, source_lines=source_lines
    )

    inner_classes: list[ClassAnalysis] = _build_inner_classes(
        cls=cls, source_lines=source_lines
    )

    # pprint(cls.as_dict())
    cls_common = build_symbol_common(
        symbol=cls,
        name=name,
        source_lines=source_lines,
    )
    return ClassAnalysis(
        **cls_common,
        kind=SymbolKind.CLASS,
        docstring=analyze_docstring(
            cls.docstring,
            source_lines=source_lines,
        ),
        decorators=tuple([]),
        dependencies=[],
        variables=tuple(parameters),
        bases=tuple(bases),
        methods=tuple(methods),
        pydantic=None,
        inner_classes=tuple(inner_classes),
    )
