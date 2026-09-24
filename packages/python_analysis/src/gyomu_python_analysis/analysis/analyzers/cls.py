import ast

from griffe import Attribute, Class, Function, TypeAlias
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.class_analysis import (
    ClassAnalysis,
    ClassCommon,
    ClassTypeAliasAnalysis,
    ClassVariableAnalysis,
    InnerClassAnalysis,
)
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis
from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.type.expression import StatementAnalysis
from gyomu_schema.schemas.python.type.structure import NameStructureAnalysis
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis
from gyomu_schema.utility.fromatting import format_object

from gyomu_python_analysis.analysis.analyzers.ast.statement import analyze_statement
from gyomu_python_analysis.analysis.analyzers.ast.symbol import (
    AstClassFunctionKey,
    build_class_function_index,
)
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
    check_ellipsis_only,
)
from gyomu_python_analysis.analysis.analyzers.internal.common import (
    build_member_common,
    build_symbol_common,
)
from gyomu_python_analysis.analysis.analyzers.pydantic import analyze_pydantic
from gyomu_python_analysis.analysis.analyzers.types import analyze_type


def _retrieve_constructor_location(
    cls: Class,
    context: SymbolContext,
    option: AnalysisOption | None,
) -> SourceLocation | None:
    constructor_location: SourceLocation | None = None
    if "__init__" in cls.members:
        init_member = cls.members["__init__"]
        if isinstance(init_member, Function):
            constructor_common = build_member_common(
                symbol=init_member,
                name="__init__",
                parent_location=None,
                context=context,
                option=option,
            )
            constructor_location = constructor_common["location"]
    return constructor_location


def _build_class_type_aliases(
    cls: Class,
    parent_location: SourceLocation | None,
    context: SymbolContext,
    member_path: MemberPath,
    option: AnalysisOption | None,
) -> list[ClassTypeAliasAnalysis]:
    aliases: list[ClassTypeAliasAnalysis] = []
    for member_name, member in cls.members.items():
        if isinstance(member, TypeAlias):
            aliases.append(
                _build_class_type_alias_analysis(
                    member=member,
                    name=member_name,
                    parent_location=parent_location,
                    context=context,
                    member_path=member_path,
                    option=option,
                )
            )
    return aliases


def _build_class_type_alias_analysis(
    member: TypeAlias,
    name: str,
    parent_location: SourceLocation | None,
    context: SymbolContext,
    member_path: MemberPath,
    option: AnalysisOption | None,
) -> ClassTypeAliasAnalysis:
    new_member_path = (*member_path, name)
    alias_common = build_member_common(
        symbol=member,
        name=name,
        parent_location=parent_location,
        context=context,
        option=option,
    )
    return ClassTypeAliasAnalysis(
        **alias_common,
        alias_type=analyze_type(member.value, context, option),
        identity=build_declaration_identity(
            context=context, member_path=new_member_path
        ),
    )


def _build_class_variables(
    cls: Class,
    parent_location: SourceLocation | None,
    context: SymbolContext,
    member_path: MemberPath,
    is_pydantic_base_class: bool,
    option: AnalysisOption | None,
) -> list[ClassVariableAnalysis]:
    variables: list[ClassVariableAnalysis] = []
    for member_name, member in cls.members.items():
        if isinstance(member, Attribute):
            variables.append(
                _build_class_variable_analysis(
                    member=member,
                    name=member_name,
                    parent_location=parent_location,
                    context=context,
                    member_path=member_path,
                    is_pydantic_base_class=is_pydantic_base_class,
                    option=option,
                )
            )
    return variables


def _build_class_variable_analysis(
    member: Attribute,
    name: str,
    parent_location: SourceLocation | None,
    context: SymbolContext,
    member_path: MemberPath,
    is_pydantic_base_class: bool,
    option: AnalysisOption | None,
) -> ClassVariableAnalysis:
    new_member_path = (*member_path, name)
    variable_common = build_member_common(
        symbol=member,
        name=name,
        parent_location=parent_location,
        context=context,
        option=option,
    )
    variable_type = analyze_type(member.annotation, context, option)
    value_expression = (
        analyze_type_expression(member.value, context, option)
        if member.value is not None
        else None
    )
    pydantic: PydanticFieldAnalysis | None = None
    # logger.info(f"pydantic_base:{is_pydantic_base_class}")
    if (
        value_expression
        and variable_type
        and variable_type.structure
        and is_pydantic_base_class
    ):
        # print(repr(variable_type.structure))
        # print(repr(value_expression))
        pydantic = analyze_pydantic(variable_type.structure, value_expression)

    return ClassVariableAnalysis(
        **variable_common,
        type=variable_type,
        value_source=str(member.value) if member.value is not None else None,
        value_expression=analyze_type_expression(member.value, context, option)
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
    context: SymbolContext,
    member_path: MemberPath,
    ast_function: ast.FunctionDef | ast.AsyncFunctionDef,
    option: AnalysisOption | None,
) -> MethodAnalysis:
    new_member_path = (*member_path, name)
    method_parameters: list[ParameterAnalysis] = []
    for param in member.parameters:
        method_parameters.append(
            ParameterAnalysis(
                name=param.name,
                kind=_get_function_parameter_kind(param.kind),
                type=analyze_type(param.annotation, context, option),
                default=None,
            )
        )
    method_common = build_member_common(
        symbol=member,
        name=name,
        parent_location=parent_location,
        context=context,
        option=option,
    )

    statements: list[StatementAnalysis] = [
        analyze_statement(statement, context, option, False)
        for statement in ast_function.body
    ]
    is_ellipsis_only = check_ellipsis_only(statements)
    return MethodAnalysis(
        **method_common,
        parameters=tuple(method_parameters),
        return_type=analyze_type(member.returns, context, option),
        is_async="async" in member.labels,
        identity=build_declaration_identity(
            context=context, member_path=new_member_path
        ),
        is_ellipsis_only=is_ellipsis_only,
        statements=tuple(statements),
    )


def _build_class_methods(
    cls: Class,
    parent_location: SourceLocation | None,
    context: SymbolContext,
    member_path: MemberPath,
    ast_symbols: dict[
        AstClassFunctionKey, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
    ],
    option: AnalysisOption | None,
) -> list[MethodAnalysis]:
    methods: list[MethodAnalysis] = []
    for member_name, member in cls.members.items():
        if (
            isinstance(member, Function)
            and member.endlineno is not None
            and member.endlineno != 0
        ):
            # if member.endlineno is None:
            #     print(f"{cls.name} inside {member.name}")
            #     print(member.name)

            ast_function = ast_symbols.get(
                AstClassFunctionKey(name=member_name, end_line=member.endlineno)
            )
            if ast_function is None:
                print(f"{member_name} not found on {cls.name}")
                print(format_object(member))
            # print(repr(ast_symbols.keys()))
            assert isinstance(ast_function, (ast.FunctionDef, ast.AsyncFunctionDef))
            methods.append(
                _build_class_method_analysis(
                    member=member,
                    name=member_name,
                    parent_location=parent_location,
                    context=context,
                    member_path=member_path,
                    ast_function=ast_function,
                    option=option,
                )
            )
    return methods


def _build_inner_classes(
    cls: Class,
    context: SymbolContext,
    member_path: MemberPath,
    ast_symbols: dict[
        AstClassFunctionKey, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
    ],
    option: AnalysisOption | None,
) -> list[InnerClassAnalysis]:
    inner_classes: list[InnerClassAnalysis] = []
    for member_name, member in cls.members.items():
        if isinstance(member, Class):
            assert member.endlineno
            ast_class = ast_symbols.get(
                AstClassFunctionKey(name=member_name, end_line=member.endlineno)
            )
            assert isinstance(ast_class, ast.ClassDef)
            inner_classes.append(
                _analyze_inner_class(
                    cls=member,
                    name=member_name,
                    context=context,
                    member_path=member_path,
                    ast_class=ast_class,
                    option=option,
                )
            )
    return inner_classes


def is_base_class_pydantic(bases: list[TypeAnalysis]) -> bool:
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
    context: SymbolContext,
    member_path: MemberPath,
    ast_class: ast.ClassDef,
    option: AnalysisOption | None = None,
) -> ClassCommon:
    ast_symbols = build_class_function_index(ast_class)

    bases: list[TypeAnalysis] = [
        analyzed
        for base in cls.bases
        if (analyzed := analyze_type(base, context, option)) is not None
    ]

    is_pydantic_base_class = is_base_class_pydantic(bases)

    constructor_location: SourceLocation | None = _retrieve_constructor_location(
        cls, context, option
    )

    parameters: list[ClassVariableAnalysis] = _build_class_variables(
        cls=cls,
        parent_location=constructor_location,
        context=context,
        member_path=member_path,
        is_pydantic_base_class=is_pydantic_base_class,
        option=option,
    )

    methods: list[MethodAnalysis] = _build_class_methods(
        cls=cls,
        parent_location=constructor_location,
        context=context,
        member_path=member_path,
        ast_symbols=ast_symbols,
        option=option,
    )

    type_aliases: list[ClassTypeAliasAnalysis] = _build_class_type_aliases(
        cls=cls,
        parent_location=constructor_location,
        context=context,
        member_path=member_path,
        option=option,
    )

    inner_classes: list[InnerClassAnalysis] = _build_inner_classes(
        cls=cls,
        context=context,
        member_path=member_path,
        ast_symbols=ast_symbols,
        option=option,
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
    context: SymbolContext,
    member_path: MemberPath,
    ast_class: ast.ClassDef,
    option: AnalysisOption | None = None,
) -> InnerClassAnalysis:
    new_member_path = (*member_path, name)
    class_common = _analyze_class_common(
        cls,
        name,
        context,
        member_path=new_member_path,
        ast_class=ast_class,
        option=option,
    )
    # pprint(cls.as_dict())
    base_common = build_member_common(
        symbol=cls, name=name, parent_location=None, context=context, option=option
    )
    return InnerClassAnalysis(
        **base_common,
        **class_common,
        identity=build_declaration_identity(
            context=context, member_path=new_member_path
        ),
    )


def analyze_class(
    cls: Class,
    name: str,
    context: SymbolContext,
    ast: ast.ClassDef,
    option: AnalysisOption | None = None,
) -> ClassAnalysis:
    member_path: MemberPath = ()
    class_common = _analyze_class_common(cls, name, context, member_path, ast, option)
    # pprint(cls.as_dict())
    base_common = build_symbol_common(
        symbol=cls, name=name, context=context, option=option
    )

    return ClassAnalysis(
        **base_common,
        **class_common,
        dependencies=tuple(),
        identity=context.declaration,
    )
