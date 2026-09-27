from enum import StrEnum

from pydantic import BaseModel

from .structure import LiteralValue


class ExpressionKind(StrEnum):
    """Defines kinds of Python expressions for AST analysis.

    Defines kinds of Python expressions for AST analysis.
    """

    NAME = "name"
    """The name member.

    The name member.
    """
    GENERIC = "generic"
    """The generic member.

    The generic member.
    """
    UNION = "union"
    """The union member.

    The union member.
    """
    LITERAL = "literal"
    """The literal member.

    The literal member.
    """
    CALLABLE = "callable"
    """The callable member.

    The callable member.
    """
    NONE = "none"
    """The none member.

    The none member.
    """
    UNKNOWN = "unknown"
    """The unknown member.

    The unknown member.
    """
    ATTRIBUTE = "attribute"
    """The attribute member.

    The attribute member.
    """
    TUPLE = "tuple"
    """The tuple member.

    The tuple member.
    """
    LIST = "list"
    """The list member.

    The list member.
    """
    DICTIONARY = "dictionary"
    """The dictionary member.

    The dictionary member.
    """
    SET = "set"
    """The set member.

    The set member.
    """
    KEYWORD = "keyword"
    """The keyword member.

    The keyword member.
    """
    CALL = "call"
    """The call member.

    The call member.
    """
    ELLIPSIS = "ellipsis"
    """The ellipsis member.

    The ellipsis member.
    """
    JOINEDSTR = "joinedstr"
    """The joinedstr member.

    The joinedstr member.
    """
    BINOP = "binop"
    """The binop member.

    The binop member.
    """
    SUBSCRIPT = "subscript"
    """The subscript member.

    The subscript member.
    """
    BOOLOP = "boolop"
    """The boolop member.

    The boolop member.
    """
    FORMATTEDVALUE = "formatted_value"
    """The formatted_value member.

    The formatted_value member.
    """
    COMPARE = "compare"
    """The compare member.

    The compare member.
    """
    AWAIT = "await"
    """The await member.

    The await member.
    """
    DICTIONARYCOMPARE = "dict_compare"
    """The dict_compare member.

    The dict_compare member.
    """
    LISTCOMPARE = "list_compare"
    """The list_compare member.

    The list_compare member.
    """
    STARRED = "starred"
    """The starred member.

    The starred member.
    """
    LAMBDA = "lambda"
    """The lambda member.

    The lambda member.
    """
    YIELDFROM = "yield_from"
    """The yield_from member.

    The yield_from member.
    """
    YIELD = "yield"
    """The yield member.

    The yield member.
    """
    IFEXP = "if_exp"
    """The if_exp member.

    The if_exp member.
    """
    GENERATOREXP = "generator_exp"
    """The generator_exp member.

    The generator_exp member.
    """
    SLICE = "slice"
    """The slice member.

    The slice member.
    """
    NAMED = "named"
    """The named member.

    The named member.
    """
    SETCOMPARE = "set_compare"
    """The set_compare member.

    The set_compare member.
    """
    UNARYOP = "unaryop"


class UnknownExpressionAnalysis(BaseModel):
    """Represents an analysis of an unknown expression.

    Represents an analysis of an unknown expression.
    """

    kind: ExpressionKind = ExpressionKind.UNKNOWN
    """The kind field.

    The kind field.
    """


class NoneExpressionAnalysis(BaseModel):
    """Represents an analysis of a none expression.

    Represents an analysis of a none expression.
    """

    kind: ExpressionKind = ExpressionKind.NONE
    """The kind field.

    The kind field.
    """


class NameExpressionAnalysis(BaseModel):
    """Represents an analysis of a name expression.

    Represents an analysis of a name expression.
    """

    kind: ExpressionKind = ExpressionKind.NAME
    """The kind field.

    The kind field.
    """
    name: str
    """The name field.

    The name field.
    """


class EllipsisExpressionAnalysis(BaseModel):
    """Represents an analysis of an ellipsis expression.

    Represents an analysis of an ellipsis expression.
    """

    kind: ExpressionKind = ExpressionKind.ELLIPSIS
    """The kind field.

    The kind field.
    """


class BinaryOperator(StrEnum):
    """Defines binary operators for expressions.

    Defines binary operators for expressions.
    """

    ADD = "+"
    """The ADD member.

    The ADD member.
    """
    SUB = "-"
    """The SUB member.

    The SUB member.
    """
    MULT = "*"
    """The MULT member.

    The MULT member.
    """
    MAT_MULT = "@"
    """The MAT_MULT member.

    The MAT_MULT member.
    """
    DIV = "/"
    """The DIV member.

    The DIV member.
    """
    MOD = "%"
    """The MOD member.

    The MOD member.
    """
    POW = "**"
    """The POW member.

    The POW member.
    """
    L_SHIFT = "<<"
    """The L_SHIFT member.

    The L_SHIFT member.
    """
    R_SHIFT = ">>"
    """The R_SHIFT member.

    The R_SHIFT member.
    """
    BIT_OR = "|"
    """The BIT_OR member.

    The BIT_OR member.
    """
    BIT_XOR = "^"
    """The BIT_XOR member.

    The BIT_XOR member.
    """
    BIT_AND = "&"
    """The BIT_AND member.

    The BIT_AND member.
    """
    FLOOR_DIV = "//"
    """The FLOOR_DIV member.

    The FLOOR_DIV member.
    """


class BoolOperator(StrEnum):
    """Defines boolean operators for expressions.

    Defines boolean operators for expressions.
    """

    AND = "&&"
    """The AND member.

    The AND member.
    """
    OR = "||"
    """The OR member.

    The OR member.
    """


class CompareOperator(StrEnum):
    """Defines comparison operators for expressions.

    Defines comparison operators for expressions.
    """

    EQ = "=="
    """The EQ member.

    The EQ member.
    """
    NOT_EQ = "!="
    """The NOT_EQ member.

    The NOT_EQ member.
    """
    LT = "<"
    """The LT member.

    The LT member.
    """
    LT_E = "<="
    """The LT_E member.

    The LT_E member.
    """
    GT = ">"
    """The GT member.

    The GT member.
    """
    GT_E = ">="
    """The GT_E member.

    The GT_E member.
    """
    IS = "is"
    """The IS member.

    The IS member.
    """
    IS_NOT = "is not"
    """The IS_NOT member.

    The IS_NOT member.
    """
    IN = "in"
    """The IN member.

    The IN member.
    """
    NOT_IN = "not in"
    """The NOT_IN member.

    The NOT_IN member.
    """


class UnaryOperator(StrEnum):
    """Defines unary operators for expressions.

    Defines unary operators for expressions.
    """

    INVERT = "~"
    """The INVERT member.

    The INVERT member.
    """
    NOT = "not"
    """The NOT member.

    The NOT member.
    """
    U_ADD = "+"
    """The U_ADD member.

    The U_ADD member.
    """
    U_SUB = "-"
    """The U_SUB member.

    The U_SUB member.
    """


class FormattedConversion(StrEnum):
    """Defines formatted string conversion flags.

    Defines formatted string conversion flags.
    """

    STR = "str"
    """The STR member.

    The STR member.
    """
    REPR = "repr"
    """The REPR member.

    The REPR member.
    """
    ASCII = "ascii"
    """The ASCII member.

    The ASCII member.
    """
    NONE = "n/a"
    """The NONE member.

    The NONE member.
    """


type ExpressionWithoutConstant = (
    UnknownExpressionAnalysis
    | NameExpressionAnalysis
    | NoneExpressionAnalysis
    | EllipsisExpressionAnalysis
    | ListExpressionAnalysis
    | DictionaryExpressionAnalysis
    | CallExpressionAnalysis
    | AttributeExpressionAnalysis
    | JoinedStrExpressionAnalysis
    | TupleExpressionAnalysis
    | BinOpExpressionAnalysis
    | SubscriptExpressionAnalysis
    | BoolOpExpressionAnalysis
    | FormattedValueExpressionAnalysis
    | CompareExpressionAnalysis
    | AwaitExpressionAnalysis
    | DictionaryCompareExpressionAnalysis
    | ListCompareExpressionAnalysis
    | UnaryOpExpressionAnalysis
    | StarredExpressionAnalysis
    | SetExpressionAnalysis
    | LambdaExpressionAnalysis
    | YieldExpressionAnalysis
    | YieldFromExpressionAnalysis
    | IfExpressionAnalysis
    | GeneratorExpressionAnalysis
    | SliceExpressionAnalysis
    | NamedExpressionAnalysis
    | SetCompareExpressionAnalysis
)

type ExpressionAnalysis = LiteralValue | ExpressionWithoutConstant
"""Union type representing any supported expression analysis model.

Union type representing any supported expression analysis model.
"""


class NamedExpressionAnalysis(BaseModel):
    """Represents an analysis of a named (walrus) expression.

    Represents an analysis of a named (walrus) expression.
    """

    kind: ExpressionKind = ExpressionKind.NAMED
    """The kind field.

    The kind field.
    """
    target: NameExpressionAnalysis
    """The target field.

    The target field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class StarredExpressionAnalysis(BaseModel):
    """Represents an analysis of a starred expression.

    Represents an analysis of a starred expression.
    """

    kind: ExpressionKind = ExpressionKind.STARRED
    """The kind field.

    The kind field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class KeywordAnalysis(BaseModel):
    """Represents an analysis of a function call keyword argument.

    Represents an analysis of a function call keyword argument.
    """

    arg: str | None
    """The arg field.

    The arg field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class ComparehensionAnalysis(BaseModel):
    """Represents an analysis of a comprehension clause.

    Represents an analysis of a comprehension clause.
    """

    target: ExpressionAnalysis
    """The target field.

    The target field.
    """
    iter: ExpressionAnalysis
    """The iter field.

    The iter field.
    """
    ifs: tuple[ExpressionAnalysis, ...]
    """The ifs field.

    The ifs field.
    """
    is_async: bool
    """The is_async field.

    The is_async field.
    """


class ListCompareExpressionAnalysis(BaseModel):
    """Represents an analysis of a list comprehension expression.

    Represents an analysis of a list comprehension expression.
    """

    kind: ExpressionKind = ExpressionKind.LISTCOMPARE
    """The kind field.

    The kind field.
    """
    element: ExpressionAnalysis
    """The element field.

    The element field.
    """
    generators: tuple[ComparehensionAnalysis, ...]
    """The generators field.

    The generators field.
    """


class DictionaryCompareExpressionAnalysis(BaseModel):
    """Represents an analysis of a dictionary comprehension expression.

    Represents an analysis of a dictionary comprehension expression.
    """

    kind: ExpressionKind = ExpressionKind.DICTIONARYCOMPARE
    """The kind field.

    The kind field.
    """
    key: ExpressionAnalysis
    """The key field.

    The key field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """
    generators: tuple[ComparehensionAnalysis, ...]
    """The generators field.

    The generators field.
    """


class SetCompareExpressionAnalysis(BaseModel):
    """Represents an analysis of a set comprehension expression.

    Represents an analysis of a set comprehension expression.
    """

    kind: ExpressionKind = ExpressionKind.SETCOMPARE
    """The kind field.

    The kind field.
    """
    elt: ExpressionAnalysis
    """The elt field.

    The elt field.
    """
    generators: tuple[ComparehensionAnalysis, ...]
    """The generators field.

    The generators field.
    """


class CompareExpressionAnalysis(BaseModel):
    """Represents an analysis of a comparison expression.

    Represents an analysis of a comparison expression.
    """

    kind: ExpressionKind = ExpressionKind.COMPARE
    """The kind field.

    The kind field.
    """
    left: ExpressionAnalysis
    """The left field.

    The left field.
    """
    ops: tuple[CompareOperator, ...]
    """The ops field.

    The ops field.
    """
    comparators: tuple[ExpressionAnalysis, ...]
    """The comparators field.

    The comparators field.
    """


class FormattedValueExpressionAnalysis(BaseModel):
    """Represents an analysis of a formatted value expression in an f-string.

    Represents an analysis of a formatted value expression in an f-string.
    """

    kind: ExpressionKind = ExpressionKind.FORMATTEDVALUE
    """The kind field.

    The kind field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """
    conversion: FormattedConversion
    """The conversion field.

    The conversion field.
    """
    format_spec: ExpressionAnalysis
    """The format_spec field.

    The format_spec field.
    """


class SubscriptExpressionAnalysis(BaseModel):
    """Represents an analysis of a subscript expression.

    Represents an analysis of a subscript expression.
    """

    kind: ExpressionKind = ExpressionKind.SUBSCRIPT
    """The kind field.

    The kind field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """
    slice: ExpressionAnalysis
    """The slice field.

    The slice field.
    """


class AwaitExpressionAnalysis(BaseModel):
    """Represents an analysis of an await expression.

    Represents an analysis of an await expression.
    """

    kind: ExpressionKind = ExpressionKind.AWAIT
    """The kind field.

    The kind field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class UnaryOpExpressionAnalysis(BaseModel):
    """Represents an analysis of a unary operation expression.

    Represents an analysis of a unary operation expression.
    """

    kind: ExpressionKind = ExpressionKind.UNARYOP

    op: UnaryOperator
    """The op field.

    The op field.
    """
    operand: ExpressionAnalysis
    """The operand field.

    The operand field.
    """


class BoolOpExpressionAnalysis(BaseModel):
    """Represents an analysis of a boolean operation expression.

    Represents an analysis of a boolean operation expression.
    """

    kind: ExpressionKind = ExpressionKind.BOOLOP
    """The kind field.

    The kind field.
    """
    op: BoolOperator
    """The op field.

    The op field.
    """
    values: tuple[ExpressionAnalysis, ...]
    """The values field.

    The values field.
    """


class BinOpExpressionAnalysis(BaseModel):
    """Represents an analysis of a binary operation expression.

    Represents an analysis of a binary operation expression.
    """

    kind: ExpressionKind = ExpressionKind.BINOP
    """The kind field.

    The kind field.
    """
    left: ExpressionAnalysis
    """The left field.

    The left field.
    """
    op: BinaryOperator
    """The op field.

    The op field.
    """
    right: ExpressionAnalysis
    """The right field.

    The right field.
    """


class JoinedStrExpressionAnalysis(BaseModel):
    """Represents an analysis of an f-string joined string expression.

    Represents an analysis of an f-string joined string expression.
    """

    kind: ExpressionKind = ExpressionKind.JOINEDSTR
    """The kind field.

    The kind field.
    """
    values: tuple[ExpressionAnalysis, ...]
    """The values field.

    The values field.
    """


class AttributeExpressionAnalysis(BaseModel):
    """Represents an analysis of an attribute access expression.

    Represents an analysis of an attribute access expression.
    """

    kind: ExpressionKind = ExpressionKind.ATTRIBUTE
    """The kind field.

    The kind field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """
    attribute: str
    """The attribute field.

    The attribute field.
    """


class TupleExpressionAnalysis(BaseModel):
    """Represents an analysis of a tuple expression.

    Represents an analysis of a tuple expression.
    """

    kind: ExpressionKind = ExpressionKind.TUPLE
    """The kind field.

    The kind field.
    """
    elements: tuple[ExpressionAnalysis, ...]
    """The elements field.

    The elements field.
    """


class ListExpressionAnalysis(BaseModel):
    """Represents an analysis of a list expression.

    Represents an analysis of a list expression.
    """

    kind: ExpressionKind = ExpressionKind.LIST
    """The kind field.

    The kind field.
    """
    elements: tuple[ExpressionAnalysis, ...]
    """The elements field.

    The elements field.
    """


class DictionaryEntryAnalysis(BaseModel):
    """Represents an analysis of a dictionary key-value entry.

    Represents an analysis of a dictionary key-value entry.
    """

    key: ExpressionAnalysis
    """The key field.

    The key field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class DictionaryExpressionAnalysis(BaseModel):
    """Represents an analysis of a dictionary expression.

    Represents an analysis of a dictionary expression.
    """

    kind: ExpressionKind = ExpressionKind.DICTIONARY
    """The kind field.

    The kind field.
    """
    entries: tuple[DictionaryEntryAnalysis, ...]
    """The entries field.

    The entries field.
    """


class SetExpressionAnalysis(BaseModel):
    """Represents an analysis of a set expression.

    Represents an analysis of a set expression.
    """

    kind: ExpressionKind = ExpressionKind.SET
    """The kind field.

    The kind field.
    """
    elts: tuple[ExpressionAnalysis, ...]
    """The elts field.

    The elts field.
    """


class CallExpressionAnalysis(BaseModel):
    """Represents an analysis of a function call expression.

    Represents an analysis of a function call expression.
    """

    kind: ExpressionKind = ExpressionKind.CALL
    """The kind field.

    The kind field.
    """
    func: ExpressionAnalysis
    """The func field.

    The func field.
    """
    args: tuple[ExpressionAnalysis, ...]
    """The args field.

    The args field.
    """
    keywords: tuple[KeywordAnalysis, ...]
    """The keywords field.

    The keywords field.
    """


class ArgumentAnalysis(BaseModel):
    """Represents an analysis of a function parameter argument.

    Represents an analysis of a function parameter argument.
    """

    arg: str
    """The arg field.

    The arg field.
    """
    annotation: ExpressionAnalysis
    """The annotation field.

    The annotation field.
    """
    type_comment: str | None
    """The type_comment field.

    The type_comment field.
    """


class ArgumentsAnalysis(BaseModel):
    """Represents an analysis of a function argument definitions collection.

    Represents an analysis of a function argument definitions collection.
    """

    posonlyargs: tuple[ArgumentAnalysis, ...]
    """The posonlyargs field.

    The posonlyargs field.
    """
    args: tuple[ArgumentAnalysis, ...]
    """The args field.

    The args field.
    """
    vararg: ArgumentAnalysis | None
    """The vararg field.

    The vararg field.
    """
    kwonlyargs: tuple[ArgumentAnalysis, ...]
    """The kwonlyargs field.

    The kwonlyargs field.
    """
    kw_defaults: tuple[ExpressionAnalysis, ...]
    """The kw_defaults field.

    The kw_defaults field.
    """
    kwarg: ArgumentAnalysis | None
    """The kwarg field.

    The kwarg field.
    """
    defaults: tuple[ExpressionAnalysis, ...]
    """The defaults field.

    The defaults field.
    """


class LambdaExpressionAnalysis(BaseModel):
    """Represents an analysis of a lambda expression.

    Represents an analysis of a lambda expression.
    """

    kind: ExpressionKind = ExpressionKind.LAMBDA
    """The kind field.

    The kind field.
    """
    args: ArgumentsAnalysis
    """The args field.

    The args field.
    """
    body: ExpressionAnalysis
    """The body field.

    The body field.
    """


class IfExpressionAnalysis(BaseModel):
    """Represents an analysis of an inline if-else conditional expression.

    Represents an analysis of an inline if-else conditional expression.
    """

    kind: ExpressionKind = ExpressionKind.IFEXP
    """The kind field.

    The kind field.
    """
    test: ExpressionAnalysis
    """The test field.

    The test field.
    """
    body: ExpressionAnalysis
    """The body field.

    The body field.
    """
    orelse: ExpressionAnalysis
    """The orelse field.

    The orelse field.
    """


class YieldFromExpressionAnalysis(BaseModel):
    """Represents an analysis of a yield-from expression.

    Represents an analysis of a yield-from expression.
    """

    kind: ExpressionKind = ExpressionKind.YIELDFROM
    """The kind field.

    The kind field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class YieldExpressionAnalysis(BaseModel):
    """Represents an analysis of a yield expression.

    Represents an analysis of a yield expression.
    """

    kind: ExpressionKind = ExpressionKind.YIELD
    """The kind field.

    The kind field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class ComprehensionAnalysis(BaseModel):
    """Represents an analysis of a comprehension clause.

    Represents an analysis of a comprehension clause.
    """

    target: ExpressionAnalysis
    """The target field.

    The target field.
    """
    iter: ExpressionAnalysis
    """The iter field.

    The iter field.
    """
    ifs: tuple[ExpressionAnalysis, ...]
    """The ifs field.

    The ifs field.
    """
    is_async: bool
    """The is_async field.

    The is_async field.
    """


class GeneratorExpressionAnalysis(BaseModel):
    """Represents an analysis of a generator expression.

    Represents an analysis of a generator expression.
    """

    kind: ExpressionKind = ExpressionKind.GENERATOREXP
    """The kind field.

    The kind field.
    """
    elt: ExpressionAnalysis
    """The elt field.

    The elt field.
    """
    generators: tuple[ComprehensionAnalysis, ...]
    """The generators field.

    The generators field.
    """


class SliceExpressionAnalysis(BaseModel):
    """Represents an analysis of a slice expression.

    Represents an analysis of a slice expression.
    """

    kind: ExpressionKind = ExpressionKind.SLICE
    """The kind field.

    The kind field.
    """
    lower: ExpressionAnalysis
    """The lower field.

    The lower field.
    """
    upper: ExpressionAnalysis
    """The upper field.

    The upper field.
    """
    step: ExpressionAnalysis
    """The step field.

    The step field.
    """


class StatementKind(StrEnum):
    """Defines kinds of Python statements for AST analysis.

    Defines kinds of Python statements for AST analysis.
    """

    ASSIGN = "assign"
    """The ASSIGN member.

    The ASSIGN member.
    """
    EXPRESSION = "expression"
    """The EXPRESSION member.

    The EXPRESSION member.
    """
    RETURN = "return"
    """The RETURN member.

    The RETURN member.
    """
    UNKNOWN = "unknown"
    """The UNKNOWN member.

    The UNKNOWN member.
    """
    WHILE = "while"
    """The WHILE member.

    The WHILE member.
    """
    TRY = "try"
    """The TRY member.

    The TRY member.
    """
    IF = "if"
    """The IF member.

    The IF member.
    """
    ASSERT = "assert"
    """The ASSERT member.

    The ASSERT member.
    """
    RAISE = "raise"
    """The RAISE member.

    The RAISE member.
    """
    FOR = "for"
    """The FOR member.

    The FOR member.
    """
    WITH = "with"
    """The WITH member.

    The WITH member.
    """
    PASS = "pass"
    """The PASS member.

    The PASS member.
    """
    AUGASSIGN = "augassign"
    """The AUGASSIGN member.

    The AUGASSIGN member.
    """
    MATCH = "match"
    """The MATCH member.

    The MATCH member.
    """
    BREAK = "break"
    """The BREAK member.

    The BREAK member.
    """
    CONTINUE = "continue"
    """The CONTINUE member.

    The CONTINUE member.
    """
    FUNCTIONDEF = "functiondef"
    """The FUNCTIONDEF member.

    The FUNCTIONDEF member.
    """
    GLOBAL = "global"
    """The GLOBAL member.

    The GLOBAL member.
    """
    ANNASSIGN = "annassign"


class GlobalStatementAnalysis(BaseModel):
    """Represents an analysis of a global statement.

    Represents an analysis of a global statement.
    """

    kind: StatementKind = StatementKind.GLOBAL

    names: tuple[str, ...]
    """The names field.

    The names field.
    """


class AnnotationAssignStatementAnalysis(BaseModel):
    """Represents an analysis of an annotated assignment statement.

    Represents an analysis of an annotated assignment statement.
    """

    kind: StatementKind = StatementKind.ANNASSIGN

    target: ExpressionAnalysis
    """The target field.

    The target field.
    """
    annotation: ExpressionAnalysis
    """The annotation field.

    The annotation field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """
    simple: bool
    """The simple field.

    The simple field.
    """


class RaiseStatementAnalysis(BaseModel):
    """Represents an analysis of a raise statement.

    Represents an analysis of a raise statement.
    """

    kind: StatementKind = StatementKind.RAISE
    """The kind field.

    The kind field.
    """
    exc: ExpressionAnalysis
    """The exc field.

    The exc field.
    """
    cause: ExpressionAnalysis
    """The cause field.

    The cause field.
    """


class AugAssignStatementAnalysis(BaseModel):
    """Represents an analysis of an augmented assignment statement.

    Represents an analysis of an augmented assignment statement.
    """

    kind: StatementKind = StatementKind.AUGASSIGN
    """The kind field.

    The kind field.
    """
    target: ExpressionAnalysis
    """The target field.

    The target field.
    """
    op: BinaryOperator
    """The op field.

    The op field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class AssignStatementAnalysis(BaseModel):
    """Represents an analysis of an assignment statement.

    Represents an analysis of an assignment statement.
    """

    kind: StatementKind = StatementKind.ASSIGN
    """The kind field.

    The kind field.
    """
    targets: tuple[ExpressionAnalysis, ...]
    """The targets field.

    The targets field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class ReturnStatementAnalysis(BaseModel):
    """Represents an analysis of a return statement.

    Represents an analysis of a return statement.
    """

    kind: StatementKind = StatementKind.RETURN
    """The kind field.

    The kind field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class ExpressionStatementAnalysis(BaseModel):
    """Represents an analysis of an expression statement.

    Represents an analysis of an expression statement.
    """

    kind: StatementKind = StatementKind.EXPRESSION
    """The kind field.

    The kind field.
    """
    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class UnknownStatementAnalysis(BaseModel):
    """Represents an analysis of an unknown statement.

    Represents an analysis of an unknown statement.
    """

    kind: StatementKind = StatementKind.UNKNOWN
    """The kind field.

    The kind field.
    """


class PassStatementAnalysis(BaseModel):
    """Represents an analysis of a pass statement.

    Represents an analysis of a pass statement.
    """

    kind: StatementKind = StatementKind.PASS
    """The kind field.

    The kind field.
    """


class ContinueStatementAnalysis(BaseModel):
    """Represents an analysis of a continue statement.

    Represents an analysis of a continue statement.
    """

    kind: StatementKind = StatementKind.CONTINUE
    """The kind field.

    The kind field.
    """


class BreakStatementAnalysis(BaseModel):
    """Represents an analysis of a break statement.

    Represents an analysis of a break statement.
    """

    kind: StatementKind = StatementKind.BREAK
    """The kind field.

    The kind field.
    """


class AssertStatementAnalysis(BaseModel):
    """Represents an analysis of an assert statement.

    Represents an analysis of an assert statement.
    """

    kind: StatementKind = StatementKind.ASSERT
    """The kind field.

    The kind field.
    """
    test: ExpressionAnalysis
    """The test field.

    The test field.
    """
    message: ExpressionAnalysis
    """The message field.

    The message field.
    """


type StatementAnalysis = (
    AssignStatementAnalysis
    | ExpressionStatementAnalysis
    | UnknownStatementAnalysis
    | ReturnStatementAnalysis
    | IfStatementAnalysis
    | WhileStatementAnalysis
    | TryStatementAnalysis
    | AssertStatementAnalysis
    | RaiseStatementAnalysis
    | AnnotationAssignStatementAnalysis
    | WithStatementAnalysis
    | ForStatementAnalysis
    | PassStatementAnalysis
    | ContinueStatementAnalysis
    | BreakStatementAnalysis
    | MatchStatementAnalysis
    | AugAssignStatementAnalysis
    | FunctionDefStatementAnalysis
    | GlobalStatementAnalysis
)
"""Union type representing any supported statement analysis model.

Union type representing any supported statement analysis model.
"""

type TypeParameter = TypeVarAnalysis | ParamSpecAnalysis | TypeVarTupleAnalysis
"""Union type representing any supported type parameter analysis.

Union type representing any supported type parameter analysis.
"""


class TypeVarAnalysis(BaseModel):
    """Represents an analysis of a TypeVar type parameter definition.

    Represents an analysis of a TypeVar type parameter definition.
    """

    name: str
    """The name field.

    The name field.
    """
    bound: ExpressionAnalysis
    """The bound field.

    The bound field.
    """
    default_value: ExpressionAnalysis
    """The default_value field.

    The default_value field.
    """


class ParamSpecAnalysis(BaseModel):
    """Represents an analysis of a ParamSpec type parameter definition.

    Represents an analysis of a ParamSpec type parameter definition.
    """

    name: str
    """The name field.

    The name field.
    """
    default_value: ExpressionAnalysis
    """The default_value field.

    The default_value field.
    """


class TypeVarTupleAnalysis(BaseModel):
    """Represents an analysis of a TypeVarTuple type parameter definition.

    Represents an analysis of a TypeVarTuple type parameter definition.
    """

    name: str
    """The name field.

    The name field.
    """
    default_value: ExpressionAnalysis
    """The default_value field.

    The default_value field.
    """


class FunctionDefStatementAnalysis(BaseModel):
    """Represents an analysis of a function definition statement.

    Represents an analysis of a function definition statement.
    """

    kind: StatementKind = StatementKind.FUNCTIONDEF
    """The kind field.

    The kind field.
    """
    name: str
    """The name field.

    The name field.
    """
    args: ArgumentsAnalysis
    """The args field.

    The args field.
    """
    body: tuple[StatementAnalysis, ...]
    """The body field.

    The body field.
    """
    decorator_list: tuple[ExpressionAnalysis, ...]
    """The decorator_list field.

    The decorator_list field.
    """
    returns: ExpressionAnalysis
    """The returns field.

    The returns field.
    """
    type_comment: str | None
    """The type_comment field.

    The type_comment field.
    """
    type_params: tuple[TypeParameter, ...]
    """The type_params field.

    The type_params field.
    """
    is_async: bool
    """The is_async field.

    The is_async field.
    """


type PatternAnalysis = (
    MatchValue
    | MatchSingleton
    | MatchSequence
    | MatchMapping
    | MatchClass
    | MatchStar
    | MatchAs
    | MatchOr
)
"""Union type representing any supported pattern analysis model for pattern matching.

Union type representing any supported pattern analysis model for pattern matching.
"""


class MatchValue(BaseModel):
    """Represents an analysis of a match value pattern.

    Represents an analysis of a match value pattern.
    """

    value: ExpressionAnalysis
    """The value field.

    The value field.
    """


class MatchSingleton(BaseModel):
    """Represents an analysis of a match singleton pattern.

    Represents an analysis of a match singleton pattern.
    """

    value: bool | None
    """The value field.

    The value field.
    """


class MatchSequence(BaseModel):
    """Represents an analysis of a match sequence pattern.

    Represents an analysis of a match sequence pattern.
    """

    patterns: tuple[PatternAnalysis, ...]
    """The patterns field.

    The patterns field.
    """


class MatchMapping(BaseModel):
    """Represents an analysis of a match mapping pattern.

    Represents an analysis of a match mapping pattern.
    """

    keys: tuple[ExpressionAnalysis, ...]
    """The keys field.

    The keys field.
    """
    patterns: tuple[PatternAnalysis, ...]
    """The patterns field.

    The patterns field.
    """
    rest: str | None
    """The rest field.

    The rest field.
    """


class MatchClass(BaseModel):
    """Represents an analysis of a match class pattern.

    Represents an analysis of a match class pattern.
    """

    cls: ExpressionAnalysis
    """The cls field.

    The cls field.
    """
    patterns: tuple[PatternAnalysis, ...]
    """The patterns field.

    The patterns field.
    """
    kwd_attrs: tuple[str, ...]
    """The kwd_attrs field.

    The kwd_attrs field.
    """
    kwd_patterns: tuple[PatternAnalysis, ...]
    """The kwd_patterns field.

    The kwd_patterns field.
    """


class MatchStar(BaseModel):
    """Represents an analysis of a match star pattern.

    Represents an analysis of a match star pattern.
    """

    name: str | None
    """The name field.

    The name field.
    """


class MatchAs(BaseModel):
    """Represents an analysis of a match capture or AS pattern.

    Represents an analysis of a match capture or AS pattern.
    """

    pattern: PatternAnalysis | None
    """The pattern field.

    The pattern field.
    """
    name: str | None
    """The name field.

    The name field.
    """


class MatchOr(BaseModel):
    """Represents an analysis of a match OR pattern.

    Represents an analysis of a match OR pattern.
    """

    patterns: tuple[PatternAnalysis, ...]
    """The patterns field.

    The patterns field.
    """


class MatchCaseAnalysis(BaseModel):
    """Represents an analysis of a match case branch.

    Represents an analysis of a match case branch.
    """

    pattern: PatternAnalysis
    """The pattern field.

    The pattern field.
    """
    guard: ExpressionAnalysis
    """The guard field.

    The guard field.
    """
    body: tuple[StatementAnalysis, ...]
    """The body field.

    The body field.
    """


class MatchStatementAnalysis(BaseModel):
    """Represents an analysis of a match statement.

    Represents an analysis of a match statement.
    """

    kind: StatementKind = StatementKind.MATCH
    """The kind field.

    The kind field.
    """
    subject: ExpressionAnalysis
    """The subject field.

    The subject field.
    """
    cases: tuple[MatchCaseAnalysis, ...]
    """The cases field.

    The cases field.
    """


class ForStatementAnalysis(BaseModel):
    """Represents an analysis of a for loop statement.

    Represents an analysis of a for loop statement.
    """

    kind: StatementKind = StatementKind.FOR
    """The kind field.

    The kind field.
    """
    target: ExpressionAnalysis
    """The target field.

    The target field.
    """
    iter: ExpressionAnalysis
    """The iter field.

    The iter field.
    """
    body: tuple[StatementAnalysis, ...]
    """The body field.

    The body field.
    """
    orelse: tuple[StatementAnalysis, ...]
    """The orelse field.

    The orelse field.
    """
    type_comment: str | None
    """The type_comment field.

    The type_comment field.
    """


class WithItemAnalysis(BaseModel):
    """Represents an analysis of a with statement context item.

    Represents an analysis of a with statement context item.
    """

    context_expr: ExpressionAnalysis
    """The context_expr field.

    The context_expr field.
    """
    optional_vars: ExpressionAnalysis
    """The optional_vars field.

    The optional_vars field.
    """


class WithStatementAnalysis(BaseModel):
    """Represents an analysis of a with statement.

    Represents an analysis of a with statement.
    """

    kind: StatementKind = StatementKind.WITH
    """The kind field.

    The kind field.
    """
    items: tuple[WithItemAnalysis, ...]
    """The items field.

    The items field.
    """
    body: tuple[StatementAnalysis, ...]
    """The body field.

    The body field.
    """
    type_comment: str | None
    """The type_comment field.

    The type_comment field.
    """


class IfStatementAnalysis(BaseModel):
    """Represents an analysis of an if statement.

    Represents an analysis of an if statement.
    """

    kind: StatementKind = StatementKind.IF
    """The kind field.

    The kind field.
    """
    test: ExpressionAnalysis
    """The test field.

    The test field.
    """
    body: tuple[StatementAnalysis, ...]
    """The body field.

    The body field.
    """
    orelse: tuple[StatementAnalysis, ...]
    """The orelse field.

    The orelse field.
    """


class WhileStatementAnalysis(BaseModel):
    """Represents an analysis of a while loop statement.

    Represents an analysis of a while loop statement.
    """

    kind: StatementKind = StatementKind.WHILE
    """The kind field.

    The kind field.
    """
    test: ExpressionAnalysis
    """The test field.

    The test field.
    """
    body: tuple[StatementAnalysis, ...]
    """The body field.

    The body field.
    """
    orelse: tuple[StatementAnalysis, ...]
    """The orelse field.

    The orelse field.
    """


class ExceptionStatementAnalysis(BaseModel):
    """Represents an analysis of an exception handler clause.

    Represents an analysis of an exception handler clause.
    """

    exception_type: ExpressionAnalysis
    """The exception_type field.

    The exception_type field.
    """
    name: str | None
    """The name field.

    The name field.
    """
    body: tuple[StatementAnalysis, ...]
    """The body field.

    The body field.
    """


class TryStatementAnalysis(BaseModel):
    """Represents an analysis of a try-except-finally statement.

    Represents an analysis of a try-except-finally statement.
    """

    kind: StatementKind = StatementKind.TRY
    """The kind field.

    The kind field.
    """
    body: tuple[StatementAnalysis, ...]
    """The body field.

    The body field.
    """
    orelse: tuple[StatementAnalysis, ...]
    """The orelse field.

    The orelse field.
    """
    finalbody: tuple[StatementAnalysis, ...]
    """The finalbody field.

    The finalbody field.
    """
    handlers: tuple[ExceptionStatementAnalysis, ...]
    """The handlers field.

    The handlers field.
    """
