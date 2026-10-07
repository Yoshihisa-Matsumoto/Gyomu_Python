from gyomu_schema.schemas.document.validation import ValidationResult
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import (
    create_validation_issue,
    create_validation_result,
)


class TestValidationResult:
    def test(self) -> None:
        _assert_json_round_trip(
            ValidationResult,
            create_validation_result(
                issues=(
                    create_validation_issue(code="CODE1", message="Issue 1"),
                    create_validation_issue(code="CODE2", message="Issue 2"),
                ),
            ),
        )
