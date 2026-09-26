from enum import StrEnum

from pydantic import BaseModel

from .structure import LiteralValue


class ExpressionKind(StrEnum):
    NAME = "name"
    GENERIC = "generic"
    UNION = "union"
    LITERAL = "literal"
    CALLABLE = "callable"
    NONE = "none"
    UNKNOWN = "unknown"
    ATTRIBUTE = "attribute"
    TUPLE = "tuple"
    LIST = "list"
    DICTIONARY = "dictionary"
    SET = "set"
    KEYWORD = "keyword"
    CALL = "call"
    ELLIPSIS = "ellipsis"
    JOINEDSTR = "joinedstr"
    BINOP = "binop"
    SUBSCRIPT = "subscript"
    BOOLOP = "boolop"
    FORMATTEDVALUE = "formatted_value"
    COMPARE = "compare"
    AWAIT = "await"
    DICTIONARYCOMPARE = "dict_compare"
    LISTCOMPARE = "list_compare"
    STARRED = "starred"
    LAMBDA = "lambda"
    YIELDFROM = "yield_from"
    YIELD = "yield"
    IFEXP = "if_exp"
    GENERATOREXP = "generator_exp"
    SLICE = "slice"
    NAMED = "named"
    SETCOMPARE = "set_compare"


class UnknownExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.UNKNOWN


class NoneExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.NONE


class NameExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.NAME
    name: str


class EllipsisExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.ELLIPSIS


class BinaryOperator(StrEnum):
    ADD = "+"
    SUB = "-"
    MULT = "*"
    MAT_MULT = "@"
    DIV = "/"
    MOD = "%"
    POW = "**"
    L_SHIFT = "<<"
    R_SHIFT = ">>"
    BIT_OR = "|"
    BIT_XOR = "^"
    BIT_AND = "&"
    FLOOR_DIV = "//"


class BoolOperator(StrEnum):
    AND = "&&"
    OR = "||"


class CompareOperator(StrEnum):
    EQ = "=="
    NOT_EQ = "!="
    LT = "<"
    LT_E = "<="
    GT = ">"
    GT_E = ">="
    IS = "is"
    IS_NOT = "is not"
    IN = "in"
    NOT_IN = "not in"


class UnaryOperator(StrEnum):
    INVERT = "~"
    NOT = "not"
    U_ADD = "+"
    U_SUB = "-"


class FormattedConversion(StrEnum):
    STR = "str"
    REPR = "repr"
    ASCII = "ascii"
    NONE = "n/a"


type ExpressionAnalysis = (
    LiteralValue
    | UnknownExpressionAnalysis
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


class NamedExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.NAMED
    target: NameExpressionAnalysis
    value: ExpressionAnalysis


class StarredExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.STARRED
    value: ExpressionAnalysis


class KeywordAnalysis(BaseModel):
    arg: str | None
    value: ExpressionAnalysis


class ComparehensionAnalysis(BaseModel):
    target: ExpressionAnalysis
    iter: ExpressionAnalysis
    ifs: tuple[ExpressionAnalysis, ...]
    is_async: bool


class ListCompareExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.LISTCOMPARE
    element: ExpressionAnalysis
    generators: tuple[ComparehensionAnalysis, ...]


class DictionaryCompareExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.DICTIONARYCOMPARE
    key: ExpressionAnalysis
    value: ExpressionAnalysis
    generators: tuple[ComparehensionAnalysis, ...]


class SetCompareExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.SETCOMPARE
    elt: ExpressionAnalysis
    generators: tuple[ComparehensionAnalysis, ...]


class CompareExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.COMPARE
    left: ExpressionAnalysis
    ops: tuple[CompareOperator, ...]
    comparators: tuple[ExpressionAnalysis, ...]


class FormattedValueExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.FORMATTEDVALUE
    value: ExpressionAnalysis
    conversion: FormattedConversion
    format_spec: ExpressionAnalysis


class SubscriptExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.SUBSCRIPT
    value: ExpressionAnalysis
    slice: ExpressionAnalysis


class AwaitExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.AWAIT
    value: ExpressionAnalysis


class UnaryOpExpressionAnalysis(BaseModel):
    op: UnaryOperator
    operand: ExpressionAnalysis


class BoolOpExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.BOOLOP
    op: BoolOperator
    values: tuple[ExpressionAnalysis, ...]


class BinOpExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.BINOP
    left: ExpressionAnalysis
    op: BinaryOperator
    right: ExpressionAnalysis


class JoinedStrExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.JOINEDSTR
    values: tuple[ExpressionAnalysis, ...]


class AttributeExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.ATTRIBUTE
    value: ExpressionAnalysis
    attribute: str


class TupleExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.TUPLE
    elements: tuple[ExpressionAnalysis, ...]


class ListExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.LIST
    elements: tuple[ExpressionAnalysis, ...]


class DictionaryEntryAnalysis(BaseModel):
    key: ExpressionAnalysis
    value: ExpressionAnalysis


class DictionaryExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.DICTIONARY
    entries: tuple[DictionaryEntryAnalysis, ...]


class SetExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.SET
    elts: tuple[ExpressionAnalysis, ...]


class CallExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.CALL
    func: ExpressionAnalysis
    args: tuple[ExpressionAnalysis, ...]
    keywords: tuple[KeywordAnalysis, ...]


class ArgumentAnalysis(BaseModel):
    arg: str
    annotation: ExpressionAnalysis
    type_comment: str | None


class ArgumentsAnalysis(BaseModel):
    posonlyargs: tuple[ArgumentAnalysis, ...]
    args: tuple[ArgumentAnalysis, ...]
    vararg: ArgumentAnalysis | None
    kwonlyargs: tuple[ArgumentAnalysis, ...]
    kw_defaults: tuple[ExpressionAnalysis, ...]
    kwarg: ArgumentAnalysis | None
    defaults: tuple[ExpressionAnalysis, ...]


class LambdaExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.LAMBDA
    args: ArgumentsAnalysis
    body: ExpressionAnalysis


class IfExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.IFEXP
    test: ExpressionAnalysis
    body: ExpressionAnalysis
    orelse: ExpressionAnalysis


class YieldFromExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.YIELDFROM
    value: ExpressionAnalysis


class YieldExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.YIELD
    value: ExpressionAnalysis


class ComprehensionAnalysis(BaseModel):
    target: ExpressionAnalysis
    iter: ExpressionAnalysis
    ifs: tuple[ExpressionAnalysis, ...]
    is_async: bool


class GeneratorExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.GENERATOREXP
    elt: ExpressionAnalysis
    generators: tuple[ComprehensionAnalysis, ...]


class SliceExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.SLICE
    lower: ExpressionAnalysis
    upper: ExpressionAnalysis
    step: ExpressionAnalysis


class StatementKind(StrEnum):
    ASSIGN = "assign"
    EXPRESSION = "expression"
    RETURN = "return"
    UNKNOWN = "unknown"
    WHILE = "while"
    TRY = "try"
    IF = "if"
    ASSERT = "assert"
    RAISE = "raise"
    FOR = "for"
    WITH = "with"
    PASS = "pass"
    AUGASSIGN = "augassign"
    MATCH = "match"
    BREAK = "break"
    CONTINUE = "continue"
    FUNCTIONDEF = "functiondef"
    GLOBAL = "global"


class GlobalStatementAnalysis(BaseModel):
    names: tuple[str, ...]


class AnnotationAssignStatementAnalysis(BaseModel):
    target: ExpressionAnalysis
    annotation: ExpressionAnalysis
    value: ExpressionAnalysis
    simple: bool


class RaiseStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.RAISE
    exc: ExpressionAnalysis
    cause: ExpressionAnalysis


class AugAssignStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.AUGASSIGN
    target: ExpressionAnalysis
    op: BinaryOperator
    value: ExpressionAnalysis


class AssignStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.ASSIGN
    targets: tuple[ExpressionAnalysis, ...]
    value: ExpressionAnalysis


class ReturnStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.RETURN
    value: ExpressionAnalysis


class ExpressionStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.EXPRESSION
    value: ExpressionAnalysis


class UnknownStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.UNKNOWN


class PassStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.PASS


class ContinueStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.CONTINUE


class BreakStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.BREAK


class AssertStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.ASSERT
    test: ExpressionAnalysis
    message: ExpressionAnalysis


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

type TypeParameter = TypeVarAnalysis | ParamSpecAnalysis | TypeVarTupleAnalysis


class TypeVarAnalysis(BaseModel):
    name: str
    bound: ExpressionAnalysis
    default_value: ExpressionAnalysis


class ParamSpecAnalysis(BaseModel):
    name: str
    default_value: ExpressionAnalysis


class TypeVarTupleAnalysis(BaseModel):
    name: str
    default_value: ExpressionAnalysis


class FunctionDefStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.FUNCTIONDEF
    name: str
    args: ArgumentsAnalysis
    body: tuple[StatementAnalysis, ...]
    decorator_list: tuple[ExpressionAnalysis, ...]
    returns: ExpressionAnalysis
    type_comment: str | None
    type_params: tuple[TypeParameter, ...]
    is_async: bool


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


class MatchValue(BaseModel):
    value: ExpressionAnalysis


class MatchSingleton(BaseModel):
    value: bool | None


class MatchSequence(BaseModel):
    patterns: tuple[PatternAnalysis, ...]


class MatchMapping(BaseModel):
    keys: tuple[ExpressionAnalysis, ...]
    patterns: tuple[PatternAnalysis, ...]
    rest: str | None


class MatchClass(BaseModel):
    cls: ExpressionAnalysis
    patterns: tuple[PatternAnalysis, ...]
    kwd_attrs: tuple[str, ...]
    kwd_patterns: tuple[PatternAnalysis, ...]


class MatchStar(BaseModel):
    name: str | None


class MatchAs(BaseModel):
    pattern: PatternAnalysis | None
    name: str | None


class MatchOr(BaseModel):
    patterns: tuple[PatternAnalysis, ...]


class MatchCaseAnalysis(BaseModel):
    pattern: PatternAnalysis
    guard: ExpressionAnalysis
    body: tuple[StatementAnalysis, ...]


class MatchStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.MATCH
    subject: ExpressionAnalysis
    cases: tuple[MatchCaseAnalysis, ...]


class ForStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.FOR
    target: ExpressionAnalysis
    iter: ExpressionAnalysis
    body: tuple[StatementAnalysis, ...]
    orelse: tuple[StatementAnalysis, ...]
    type_comment: str | None


class WithItemAnalysis(BaseModel):
    context_expr: ExpressionAnalysis
    optional_vars: ExpressionAnalysis


class WithStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.WITH
    items: tuple[WithItemAnalysis, ...]
    body: tuple[StatementAnalysis, ...]
    type_comment: str | None


class IfStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.IF
    test: ExpressionAnalysis
    body: tuple[StatementAnalysis, ...]
    orelse: tuple[StatementAnalysis, ...]


class WhileStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.WHILE
    test: ExpressionAnalysis
    body: tuple[StatementAnalysis, ...]
    orelse: tuple[StatementAnalysis, ...]


class ExceptionStatementAnalysis(BaseModel):
    exception_type: ExpressionAnalysis
    name: str | None
    body: tuple[StatementAnalysis, ...]


class TryStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.TRY
    body: tuple[StatementAnalysis, ...]
    orelse: tuple[StatementAnalysis, ...]
    finalbody: tuple[StatementAnalysis, ...]
    handlers: tuple[ExceptionStatementAnalysis, ...]
