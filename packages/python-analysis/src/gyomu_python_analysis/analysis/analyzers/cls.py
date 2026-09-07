from griffe import Attribute, Class, Function, TypeAlias
from gyomu_infra.logger import logger
from gyomu_schema.schemas.python.class_analysis import (
    ClassAnalysis,
    ClassCommon,
    ClassTypeAliasAnalysis,
    ClassVariableAnalysis,
    InnerClassAnalysis,
)
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.member_analysis import MemberKind
from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis
from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.symbol_base import SymbolKind
from gyomu_schema.schemas.python.type.structure import NameStructureAnalysis
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis

from gyomu_python_analysis.analysis.analyzers.context import (
    MemberPath,
    SymbolContext,
    build_declaration_identity,
)
from gyomu_python_analysis.analysis.analyzers.expression.expr import (
    analyze_type_expression,
)
from gyomu_python_analysis.analysis.analyzers.functions import (
    _get_function_parameter_kind,
)
from gyomu_python_analysis.analysis.analyzers.internal.common import (
    build_member_common,
    build_symbol_common,
)
from gyomu_python_analysis.analysis.analyzers.pydantic import analyze_pydantic
from gyomu_python_analysis.analysis.analyzers.types import analyze_type


def _retrieve_constructor_location(
    cls: Class,
    source_lines: list[str],
    context: SymbolContext,
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
                context=context,
            )
            constructor_location = constructor_common["location"]
    return constructor_location


def _build_class_type_aliases(
    cls: Class,
    parent_location: SourceLocation | None,
    source_lines: list[str],
    context: SymbolContext,
    member_path: MemberPath,
) -> list[ClassTypeAliasAnalysis]:
    aliases: list[ClassTypeAliasAnalysis] = []
    for member_name, member in cls.members.items():
        if isinstance(member, TypeAlias):
            aliases.append(
                _build_class_type_alias_analysis(
                    member=member,
                    name=member_name,
                    parent_location=parent_location,
                    source_lines=source_lines,
                    context=context,
                    member_path=member_path,
                )
            )
    return aliases


def _build_class_type_alias_analysis(
    member: TypeAlias,
    name: str,
    parent_location: SourceLocation | None,
    source_lines: list[str],
    context: SymbolContext,
    member_path: MemberPath,
) -> ClassTypeAliasAnalysis:
    new_member_path = (*member_path, name)
    alias_common = build_member_common(
        symbol=member,
        name=name,
        parent_location=parent_location,
        source_lines=source_lines,
        context=context,
    )
    return ClassTypeAliasAnalysis(
        **alias_common,
        kind=MemberKind.TYPEALIAS,
        alias_type=analyze_type(member.value, context),
        identity=build_declaration_identity(
            context=context, member_path=new_member_path
        ),
    )


def _build_class_variables(
    cls: Class,
    parent_location: SourceLocation | None,
    source_lines: list[str],
    context: SymbolContext,
    member_path: MemberPath,
    is_pydantic_base_class: bool,
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
                    context=context,
                    member_path=member_path,
                    is_pydantic_base_class=is_pydantic_base_class,
                )
            )
    return variables


def _build_class_variable_analysis(
    member: Attribute,
    name: str,
    parent_location: SourceLocation | None,
    source_lines: list[str],
    context: SymbolContext,
    member_path: MemberPath,
    is_pydantic_base_class: bool,
) -> ClassVariableAnalysis:
    new_member_path = (*member_path, name)
    variable_common = build_member_common(
        symbol=member,
        name=name,
        parent_location=parent_location,
        source_lines=source_lines,
        context=context,
    )
    variable_type = analyze_type(member.annotation, context)
    value_expression = (
        analyze_type_expression(member.value, context)
        if member.value is not None
        else None
    )
    pydantic: PydanticFieldAnalysis | None = None
    logger.info(f"pydantic_base:{is_pydantic_base_class}")
    if (
        value_expression
        and variable_type
        and variable_type.structure
        and is_pydantic_base_class
    ):
        print(repr(variable_type.structure))
        print(repr(value_expression))
        pydantic = analyze_pydantic(variable_type.structure, value_expression)

    return ClassVariableAnalysis(
        **variable_common,
        kind=MemberKind.VARIABLE,
        type=variable_type,
        value_source=str(member.value) if member.value is not None else None,
        value_expression=analyze_type_expression(member.value, context)
        if member.value is not None
        else None,
        pydantic=pydantic,
        identity=build_declaration_identity(
            context=context, member_path=new_member_path
        ),
    )


def _build_class_method_analysis(
    member: Function,
    name: str,
    parent_location: SourceLocation | None,
    source_lines: list[str],
    context: SymbolContext,
    member_path: MemberPath,
) -> MethodAnalysis:
    new_member_path = (*member_path, name)
    method_parameters: list[ParameterAnalysis] = []
    for param in member.parameters:
        method_parameters.append(
            ParameterAnalysis(
                name=param.name,
                kind=_get_function_parameter_kind(param.kind),
                type=analyze_type(param.annotation, context),
                default=None,
            )
        )
    method_common = build_member_common(
        symbol=member,
        name=name,
        parent_location=parent_location,
        source_lines=source_lines,
        context=context,
    )

    return MethodAnalysis(
        **method_common,
        kind=MemberKind.METHOD,
        parameters=tuple(method_parameters),
        return_type=analyze_type(member.returns, context),
        is_async="async" in member.labels,
        identity=build_declaration_identity(
            context=context, member_path=new_member_path
        ),
    )


def _build_class_methods(
    cls: Class,
    parent_location: SourceLocation | None,
    source_lines: list[str],
    context: SymbolContext,
    member_path: MemberPath,
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
                    context=context,
                    member_path=member_path,
                )
            )
    return methods


def _build_inner_classes(
    cls: Class, source_lines: list[str], context: SymbolContext, member_path: MemberPath
) -> list[InnerClassAnalysis]:
    inner_classes: list[InnerClassAnalysis] = []
    for member_name, member in cls.members.items():
        if isinstance(member, Class):
            inner_classes.append(
                _analyze_inner_class(
                    cls=member,
                    name=member_name,
                    source_lines=source_lines,
                    context=context,
                    member_path=member_path,
                )
            )
    return inner_classes


def _is_pydantic_base_class(bases: list[TypeAnalysis]) -> bool:
    for base in bases:
        if (
            isinstance(base.structure, NameStructureAnalysis)
            and base.structure.name == "BaseModel"
        ):
            return True

    return False


def _analyze_class_common(
    cls: Class,
    name: str,
    source_lines: list[str],
    context: SymbolContext,
    member_path: MemberPath,
) -> ClassCommon:
    bases: list[TypeAnalysis] = [
        analyzed
        for base in cls.bases
        if (analyzed := analyze_type(base, context)) is not None
    ]

    is_pydantic_base_class = _is_pydantic_base_class(bases)

    constructor_location: SourceLocation | None = _retrieve_constructor_location(
        cls, source_lines, context
    )

    parameters: list[ClassVariableAnalysis] = _build_class_variables(
        cls=cls,
        parent_location=constructor_location,
        source_lines=source_lines,
        context=context,
        member_path=member_path,
        is_pydantic_base_class=is_pydantic_base_class,
    )

    methods: list[MethodAnalysis] = _build_class_methods(
        cls=cls,
        parent_location=constructor_location,
        source_lines=source_lines,
        context=context,
        member_path=member_path,
    )

    type_aliases: list[ClassTypeAliasAnalysis] = _build_class_type_aliases(
        cls=cls,
        parent_location=constructor_location,
        source_lines=source_lines,
        context=context,
        member_path=member_path,
    )

    inner_classes: list[InnerClassAnalysis] = _build_inner_classes(
        cls=cls, source_lines=source_lines, context=context, member_path=member_path
    )

    return {
        "bases": tuple(bases),
        "inner_classes": tuple(inner_classes),
        "methods": tuple(methods),
        "variables": tuple(parameters),
        "type_aliases": tuple(type_aliases),
    }


def _analyze_inner_class(
    cls: Class,
    name: str,
    source_lines: list[str],
    context: SymbolContext,
    member_path: MemberPath,
) -> InnerClassAnalysis:
    new_member_path = (*member_path, name)
    class_common = _analyze_class_common(
        cls, name, source_lines, context, member_path=new_member_path
    )
    # pprint(cls.as_dict())
    base_common = build_member_common(
        symbol=cls,
        name=name,
        parent_location=None,
        source_lines=source_lines,
        context=context,
    )
    return InnerClassAnalysis(
        **base_common,
        **class_common,
        kind=MemberKind.CLASS,
        identity=build_declaration_identity(
            context=context, member_path=new_member_path
        ),
    )


def analyze_class(
    cls: Class, name: str, source_lines: list[str], context: SymbolContext
) -> ClassAnalysis:
    member_path: MemberPath = ()
    class_common = _analyze_class_common(cls, name, source_lines, context, member_path)
    # pprint(cls.as_dict())
    base_common = build_symbol_common(
        symbol=cls, name=name, source_lines=source_lines, context=context
    )

    return ClassAnalysis(
        **base_common,
        **class_common,
        kind=SymbolKind.CLASS,
        dependencies=tuple(),
        identity=context.declaration,
    )
