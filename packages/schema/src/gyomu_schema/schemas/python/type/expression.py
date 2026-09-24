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
    ARRAY = "array"
    DICTIONARY = "dictionary"
    SET = "set"
    KEYWORD = "keyword"
    CALL = "call"
    ELLIPSIS = "ellipsis"


class UnknownExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.UNKNOWN


class NoneExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.NONE


class NameExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.NAME
    name: str


class EllipsisExpressionAnalysis(BaseModel):
    kind: ExpressionKind = ExpressionKind.ELLIPSIS


type ExpressionAnalysis = (
    LiteralValue
    | UnknownExpressionAnalysis
    | NameExpressionAnalysis
    | NoneExpressionAnalysis
    | EllipsisExpressionAnalysis
    | ListExpressionAnalysis
    | DictionaryExpressionAnalysis
)


class ListExpressionAnalysis(BaseModel):
    elements: tuple[ExpressionAnalysis, ...]


class DictionaryEntryAnalysis(BaseModel):
    key: ExpressionAnalysis
    value: ExpressionAnalysis


class DictionaryExpressionAnalysis(BaseModel):
    entries: tuple[DictionaryEntryAnalysis, ...]


class StatementKind(StrEnum):
    ASSIGN = "assign"
    EXPRESSION = "expression"
    RETURN = "return"
    UNKNOWN = "unknown"


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


type StatementAnalysis = (
    AssignStatementAnalysis
    | ExpressionStatementAnalysis
    | UnknownStatementAnalysis
    | ReturnStatementAnalysis
)
