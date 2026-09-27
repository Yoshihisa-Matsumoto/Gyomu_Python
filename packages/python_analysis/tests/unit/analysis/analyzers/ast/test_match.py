import ast

from gyomu_python_analysis.analysis.analyzers.ast.statement import analyze_statement
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_schema.schemas.python.type.expression import (
    CompareExpressionAnalysis,
    CompareOperator,
    MatchAs,
    MatchClass,
    MatchMapping,
    MatchOr,
    MatchSequence,
    MatchStatementAnalysis,
    MatchValue,
    NameExpressionAnalysis,
    NoneExpressionAnalysis,
    PatternAnalysis,
    ReturnStatementAnalysis,
    StatementKind,
)
from gyomu_schema.schemas.python.type.structure import LiteralValue

from packages.python_analysis.tests.unit.analysis.analyzers.ast.helper import (
    assert_expression_type,
    find_function,
)


def analyze_match_functions(
    context: SymbolContext,
    function_name: str,
) -> list[MatchStatementAnalysis]:
    function = find_function("match", function_name)
    target_statements: list[MatchStatementAnalysis] = []
    for stmt in function.body:
        if isinstance(stmt, ast.Match):
            result = analyze_statement(stmt, context, None, False)
            assert isinstance(result, MatchStatementAnalysis)
            target_statements.append(result)

    return target_statements


def assert_case_mattern[T: PatternAnalysis](
    expression: PatternAnalysis,
    expected_type: type[T],
) -> T:
    assert isinstance(expression, expected_type)
    return expression


def test_simple_match(
    context: SymbolContext,
) -> None:
    results = analyze_match_functions(context, "simple_match")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.MATCH

    result.subject = assert_expression_type(
        result.subject,
        NameExpressionAnalysis,
    )
    assert result.subject.name == "value"

    assert len(result.cases) == 3

    case = result.cases[0]
    pattern = assert_case_mattern(case.pattern, MatchValue)
    pattern.value = assert_expression_type(
        pattern.value,
        LiteralValue,
    )
    assert pattern.value.value == 0
    assert isinstance(case.guard, NoneExpressionAnalysis)

    assert len(case.body) == 1
    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "zero"

    case = result.cases[1]
    pattern = assert_case_mattern(case.pattern, MatchValue)
    pattern.value = assert_expression_type(
        pattern.value,
        LiteralValue,
    )
    assert pattern.value.value == 1
    assert isinstance(case.guard, NoneExpressionAnalysis)

    assert len(case.body) == 1
    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "one"

    case = result.cases[2]
    pattern = assert_case_mattern(case.pattern, MatchAs)
    assert pattern.name is None
    assert pattern.pattern is None
    assert isinstance(case.guard, NoneExpressionAnalysis)

    assert len(case.body) == 1
    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "other"


def test_match_with_guard(
    context: SymbolContext,
) -> None:
    results = analyze_match_functions(context, "match_with_guard")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.MATCH

    result.subject = assert_expression_type(
        result.subject,
        NameExpressionAnalysis,
    )
    assert result.subject.name == "value"

    assert len(result.cases) == 3

    case = result.cases[0]
    pattern = assert_case_mattern(case.pattern, MatchAs)
    assert pattern.name == "number"
    assert pattern.pattern is None

    case.guard = assert_expression_type(
        case.guard,
        CompareExpressionAnalysis,
    )
    case.guard.left = assert_expression_type(
        case.guard.left,
        NameExpressionAnalysis,
    )
    assert case.guard.left.name == "number"
    assert case.guard.ops == (CompareOperator.GT,)
    assert len(case.guard.comparators) == 1
    comparator = assert_expression_type(
        case.guard.comparators[0],
        LiteralValue,
    )
    assert comparator.value == 0

    assert len(case.body) == 1
    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "positive"

    case = result.cases[1]
    pattern = assert_case_mattern(case.pattern, MatchAs)
    assert pattern.name == "number"
    assert pattern.pattern is None

    case.guard = assert_expression_type(
        case.guard,
        CompareExpressionAnalysis,
    )
    case.guard.left = assert_expression_type(
        case.guard.left,
        NameExpressionAnalysis,
    )
    assert case.guard.left.name == "number"
    assert case.guard.ops == (CompareOperator.LT,)
    assert len(case.guard.comparators) == 1
    comparator = assert_expression_type(
        case.guard.comparators[0],
        LiteralValue,
    )
    assert comparator.value == 0

    assert len(case.body) == 1
    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "negative"

    case = result.cases[2]
    pattern = assert_case_mattern(case.pattern, MatchAs)
    assert pattern.name is None
    assert pattern.pattern is None
    assert isinstance(case.guard, NoneExpressionAnalysis)

    assert len(case.body) == 1
    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "zero"


def test_match_with_or_pattern(
    context: SymbolContext,
) -> None:
    results = analyze_match_functions(context, "match_with_or_pattern")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.MATCH

    result.subject = assert_expression_type(
        result.subject,
        NameExpressionAnalysis,
    )
    assert result.subject.name == "value"

    assert len(result.cases) == 3

    case = result.cases[0]
    pattern = assert_case_mattern(case.pattern, MatchOr)
    assert len(pattern.patterns) == 2

    value_pattern = assert_case_mattern(
        pattern.patterns[0],
        MatchValue,
    )
    value_pattern.value = assert_expression_type(
        value_pattern.value,
        LiteralValue,
    )
    assert value_pattern.value.value == 0

    value_pattern = assert_case_mattern(
        pattern.patterns[1],
        MatchValue,
    )
    value_pattern.value = assert_expression_type(
        value_pattern.value,
        LiteralValue,
    )
    assert value_pattern.value.value == 1

    assert isinstance(case.guard, NoneExpressionAnalysis)

    assert len(case.body) == 1
    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "small"

    case = result.cases[1]
    pattern = assert_case_mattern(case.pattern, MatchOr)
    assert len(pattern.patterns) == 2

    value_pattern = assert_case_mattern(
        pattern.patterns[0],
        MatchValue,
    )
    value_pattern.value = assert_expression_type(
        value_pattern.value,
        LiteralValue,
    )
    assert value_pattern.value.value == 2

    value_pattern = assert_case_mattern(
        pattern.patterns[1],
        MatchValue,
    )
    value_pattern.value = assert_expression_type(
        value_pattern.value,
        LiteralValue,
    )
    assert value_pattern.value.value == 3

    assert isinstance(case.guard, NoneExpressionAnalysis)

    assert len(case.body) == 1
    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "medium"

    case = result.cases[2]
    pattern = assert_case_mattern(case.pattern, MatchAs)
    assert pattern.name is None
    assert pattern.pattern is None
    assert isinstance(case.guard, NoneExpressionAnalysis)

    assert len(case.body) == 1
    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "large"


def test_match_sequence(
    context: SymbolContext,
) -> None:
    results = analyze_match_functions(context, "match_sequence")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.MATCH

    result.subject = assert_expression_type(
        result.subject,
        NameExpressionAnalysis,
    )
    assert result.subject.name == "value"

    assert len(result.cases) == 4

    case = result.cases[0]
    pattern = assert_case_mattern(case.pattern, MatchSequence)
    assert pattern.patterns == ()
    assert isinstance(case.guard, NoneExpressionAnalysis)

    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
    statement.value = assert_expression_type(
        statement.value,
        LiteralValue,
    )
    assert statement.value.value == "empty"

    case = result.cases[1]
    pattern = assert_case_mattern(case.pattern, MatchSequence)
    assert len(pattern.patterns) == 1

    item_pattern = assert_case_mattern(
        pattern.patterns[0],
        MatchAs,
    )
    assert item_pattern.name == "first"
    assert item_pattern.pattern is None
    assert isinstance(case.guard, NoneExpressionAnalysis)

    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    case = result.cases[2]
    pattern = assert_case_mattern(case.pattern, MatchSequence)
    assert len(pattern.patterns) == 2

    item_pattern = assert_case_mattern(
        pattern.patterns[0],
        MatchAs,
    )
    assert item_pattern.name == "first"
    assert item_pattern.pattern is None

    item_pattern = assert_case_mattern(
        pattern.patterns[1],
        MatchAs,
    )
    assert item_pattern.name == "second"
    assert item_pattern.pattern is None

    assert isinstance(case.guard, NoneExpressionAnalysis)

    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    case = result.cases[3]
    pattern = assert_case_mattern(case.pattern, MatchAs)
    assert pattern.name is None
    assert pattern.pattern is None
    assert isinstance(case.guard, NoneExpressionAnalysis)

    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)


def test_match_mapping(
    context: SymbolContext,
) -> None:
    results = analyze_match_functions(context, "match_mapping")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.MATCH

    result.subject = assert_expression_type(
        result.subject,
        NameExpressionAnalysis,
    )
    assert result.subject.name == "value"

    assert len(result.cases) == 3

    case = result.cases[0]
    pattern = assert_case_mattern(case.pattern, MatchMapping)

    assert len(pattern.keys) == 2
    assert len(pattern.patterns) == 2

    key = assert_expression_type(pattern.keys[0], LiteralValue)
    assert key.value == "name"

    item_pattern = assert_case_mattern(
        pattern.patterns[0],
        MatchAs,
    )
    assert item_pattern.name == "name"
    assert item_pattern.pattern is None

    key = assert_expression_type(pattern.keys[1], LiteralValue)
    assert key.value == "age"

    item_pattern = assert_case_mattern(
        pattern.patterns[1],
        MatchAs,
    )
    assert item_pattern.name == "age"
    assert item_pattern.pattern is None

    assert isinstance(case.guard, NoneExpressionAnalysis)

    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    case = result.cases[1]
    pattern = assert_case_mattern(case.pattern, MatchMapping)

    assert len(pattern.keys) == 1
    assert len(pattern.patterns) == 1

    key = assert_expression_type(pattern.keys[0], LiteralValue)
    assert key.value == "name"

    item_pattern = assert_case_mattern(
        pattern.patterns[0],
        MatchAs,
    )
    assert item_pattern.name == "name"
    assert item_pattern.pattern is None

    assert isinstance(case.guard, NoneExpressionAnalysis)

    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    case = result.cases[2]
    pattern = assert_case_mattern(case.pattern, MatchAs)
    assert pattern.name is None
    assert pattern.pattern is None
    assert isinstance(case.guard, NoneExpressionAnalysis)

    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)


def test_match_class(
    context: SymbolContext,
) -> None:
    results = analyze_match_functions(context, "match_class")

    assert len(results) == 1
    result = results[0]

    assert result.kind == StatementKind.MATCH

    result.subject = assert_expression_type(
        result.subject,
        NameExpressionAnalysis,
    )
    assert result.subject.name == "value"

    assert len(result.cases) == 3

    case = result.cases[0]
    pattern = assert_case_mattern(case.pattern, MatchClass)

    pattern.cls = assert_expression_type(
        pattern.cls,
        NameExpressionAnalysis,
    )
    assert pattern.cls.name == "int"

    assert len(pattern.patterns) == 1
    item_pattern = assert_case_mattern(
        pattern.patterns[0],
        MatchAs,
    )
    assert item_pattern.name == "number"
    assert item_pattern.pattern is None

    assert pattern.kwd_attrs == ()
    assert pattern.kwd_patterns == ()

    assert isinstance(case.guard, NoneExpressionAnalysis)

    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    case = result.cases[1]
    pattern = assert_case_mattern(case.pattern, MatchClass)

    pattern.cls = assert_expression_type(
        pattern.cls,
        NameExpressionAnalysis,
    )
    assert pattern.cls.name == "str"

    assert len(pattern.patterns) == 1
    item_pattern = assert_case_mattern(
        pattern.patterns[0],
        MatchAs,
    )
    assert item_pattern.name == "text"
    assert item_pattern.pattern is None

    assert pattern.kwd_attrs == ()
    assert pattern.kwd_patterns == ()

    assert isinstance(case.guard, NoneExpressionAnalysis)

    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)

    case = result.cases[2]
    pattern = assert_case_mattern(case.pattern, MatchAs)
    assert pattern.name is None
    assert pattern.pattern is None
    assert isinstance(case.guard, NoneExpressionAnalysis)

    statement = case.body[0]
    assert statement.kind == StatementKind.RETURN
    assert isinstance(statement, ReturnStatementAnalysis)
