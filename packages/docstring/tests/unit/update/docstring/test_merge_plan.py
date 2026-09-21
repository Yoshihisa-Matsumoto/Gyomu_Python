from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    ParamActionValue,
    RaiseActionValue,
)
from gyomu_docstring.update.docstring.merge_plan import (
    ConflictType,
    MergeConflict,
    MergeDeleteAction,
    MergePlan,
    MergePreserveAction,
    MergeReplaceAction,
    ParamMergePlan,
    RaiseMergePlan,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_declaration_identity,
)


class TestMergeReplaceAction:
    def test(self) -> None:
        _assert_json_round_trip(
            MergeReplaceAction, MergeReplaceAction(value="ABCDEFG#")
        )


class TestMergeDeleteAction:
    def test(self) -> None:
        _assert_json_round_trip(MergeDeleteAction, MergeDeleteAction())


class TestMergePreserveAction:
    def test(self) -> None:
        _assert_json_round_trip(MergePreserveAction, MergePreserveAction())


class TestRaiseMergePlan:
    def test(self) -> None:
        _assert_json_round_trip(
            RaiseMergePlan,
            RaiseMergePlan(
                exception_type="ValueException",
                action=MergeReplaceAction(
                    value=RaiseActionValue(
                        error_type="ValueException", description="Error"
                    )
                ),
            ),
        )


class TestParamMergePlan:
    def test(self) -> None:
        _assert_json_round_trip(
            ParamMergePlan,
            ParamMergePlan(
                name="Param1",
                sort_order=3,
                action=MergeReplaceAction(
                    value=ParamActionValue(type="ParamType", description="Error")
                ),
            ),
        )


class TestMergeConflict:
    def test(self) -> None:
        _assert_json_round_trip(
            MergeConflict,
            MergeConflict(
                symbol="ABC", type=ConflictType.HUMAN_EDITED, message="ABC#DF"
            ),
        )


class TestMergePlan:
    def test(self) -> None:
        _assert_json_round_trip(
            MergePlan,
            MergePlan(
                identity=create_declaration_identity("ID1"),
                summary=MergePreserveAction(),
                description=MergeDeleteAction(),
                params=(
                    (
                        ParamMergePlan(
                            name="Param1", sort_order=1, action=MergePreserveAction()
                        ),
                        ParamMergePlan(
                            name="Param2", sort_order=2, action=MergeDeleteAction()
                        ),
                    )
                ),
                returns=MergePreserveAction(),
                raises=(
                    (
                        RaiseMergePlan(
                            exception_type="ValueError", action=MergePreserveAction()
                        ),
                        RaiseMergePlan(
                            exception_type="ValidationError", action=MergeDeleteAction()
                        ),
                    )
                ),
            ),
        )
