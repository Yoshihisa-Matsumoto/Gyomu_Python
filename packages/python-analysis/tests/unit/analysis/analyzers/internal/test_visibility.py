import pytest
from gyomu_python_analysis.analysis.analyzers.internal.visibility import (
    calculate_visibility,
)
from gyomu_schema.schemas.python.visibility import Visibility


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("__all__", Visibility.SPECIAL),
        ("__name__", Visibility.SPECIAL),
        ("__file__", Visibility.SPECIAL),
        ("__doc__", Visibility.SPECIAL),
        ("_internal", Visibility.PRIVATE),
        ("__internal", Visibility.PRIVATE),
        ("VERSION", Visibility.PUBLIC),
        ("version", Visibility.PUBLIC),
    ],
)
def test_calculate_visibility(
    name: str,
    expected: Visibility,
) -> None:
    assert calculate_visibility(name) == expected
