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
)


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


class CallExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.CALL
    func: ExpressionAnalysis
    args: tuple[ExpressionAnalysis, ...]
    keywords: tuple[KeywordAnalysis, ...]


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


class AnnotationAssignStatementAnalysis(BaseModel):
    target: ExpressionAnalysis
    annotation: ExpressionAnalysis
    value: ExpressionAnalysis
    simple: bool


class RaiseStatementAnalysis(BaseModel):
    kind: StatementKind = StatementKind.RAISE
    exc: ExpressionAnalysis
    cause: ExpressionAnalysis


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
)


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
