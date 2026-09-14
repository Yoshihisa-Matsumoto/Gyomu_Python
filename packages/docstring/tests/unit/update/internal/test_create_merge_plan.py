import pytest
from docstring_test_support.helpers import create_declaration_identity
from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DescriptionPlan,
    DocstringUpdateEntry,
    DocstringUpdatePlan,
    ParamActionValue,
    ParamUpdatePlan,
    ParamUpdateReplaceAction,
    RaiseActionValue,
    RaiseUpdatePlan,
    RaiseUpdateReplaceAction,
    Reasoning,
    ReturnActionValue,
    ReturnUpdatePlan,
    ReturnUpdateReplaceAction,
    Risk,
    SummaryPlan,
    UpdateDeleteAction,
    UpdatePreserveAction,
    UpdateReplaceAction,
)
from gyomu_docstring.update.docstring.merge_plan import (
    MergeDeleteAction,
    MergePlan,
    MergePreserveAction,
    MergeReplaceAction,
    ParamMergePlan,
    RaiseMergePlan,
)
from gyomu_docstring.update.internal.create_merge_plan import create_merge_plan
from gyomu_schema.schemas.confidence import Confidence
from gyomu_schema.schemas.python.types import DeclarationIdentity


class TestCreateMergePlan:
    @staticmethod
    def _identity() -> DeclarationIdentity:
        return create_declaration_identity("example::Example")

    @staticmethod
    def _confidence() -> Confidence:
        return 0.9

    @classmethod
    def _summary(
        cls,
        action: UpdateReplaceAction | UpdatePreserveAction | UpdateDeleteAction,
    ) -> SummaryPlan:
        return SummaryPlan(
            action=action,
            confidence=cls._confidence(),
        )

    @classmethod
    def _description(
        cls,
        action: UpdateReplaceAction | UpdatePreserveAction | UpdateDeleteAction,
    ) -> DescriptionPlan:
        return DescriptionPlan(
            action=action,
            confidence=cls._confidence(),
        )

    @classmethod
    def _entry(
        cls,
        *,
        summary_action: UpdateReplaceAction | UpdatePreserveAction | UpdateDeleteAction,
        description_action: UpdateReplaceAction
        | UpdatePreserveAction
        | UpdateDeleteAction,
        params: tuple[ParamUpdatePlan, ...] = (),
        raises: tuple[RaiseUpdatePlan, ...] = (),
        returns: ReturnUpdatePlan,
    ) -> DocstringUpdateEntry:
        return DocstringUpdateEntry(
            identity=cls._identity(),
            summary=cls._summary(summary_action),
            description=cls._description(description_action),
            params=params,
            raises=raises,
            returns=returns,
            reasoning=Reasoning(
                summary="summary",
                param_mapping="params",
                return_mapping="returns",
            ),
            risk=Risk(
                has_human_conflict=False,
                risk_level="low",
            ),
        )

    def test_replace_summary(self) -> None:
        entry = self._entry(
            summary_action=UpdateReplaceAction(value="New summary"),
            description_action=UpdatePreserveAction(),
            returns=ReturnUpdatePlan(
                action=UpdatePreserveAction(),
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry,)),
        )

        assert result == [
            MergePlan(
                identity=self._identity(),
                summary=MergeReplaceAction(value="New summary"),
                description=MergePreserveAction(),
                params=(),
                returns=MergePreserveAction(),
                raises=(),
            ),
        ]

    def test_preserve_description(self) -> None:
        entry = self._entry(
            summary_action=UpdatePreserveAction(),
            description_action=UpdatePreserveAction(),
            returns=ReturnUpdatePlan(
                action=UpdatePreserveAction(),
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry,)),
        )

        assert result[0].description == MergePreserveAction()

    def test_delete_summary(self) -> None:
        entry = self._entry(
            summary_action=UpdateDeleteAction(),
            description_action=UpdatePreserveAction(),
            returns=ReturnUpdatePlan(
                action=UpdatePreserveAction(),
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry,)),
        )

        assert result[0].summary == MergeDeleteAction()

    def test_param_replace(self) -> None:
        value = ParamActionValue(
            type="str",
            description="User name.",
        )

        entry = self._entry(
            summary_action=UpdatePreserveAction(),
            description_action=UpdatePreserveAction(),
            params=(
                ParamUpdatePlan(
                    name="name",
                    sort_order=0,
                    action=ParamUpdateReplaceAction(value=value),
                    confidence=self._confidence(),
                ),
            ),
            returns=ReturnUpdatePlan(
                action=UpdatePreserveAction(),
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry,)),
        )

        assert result[0].params == (
            ParamMergePlan(
                name="name",
                sort_order=0,
                action=MergeReplaceAction(value=value),
            ),
        )

    @pytest.mark.parametrize(
        ("action", "expected"),
        [
            (
                UpdatePreserveAction(),
                MergePreserveAction(),
            ),
            (
                UpdateDeleteAction(),
                MergeDeleteAction(),
            ),
        ],
    )
    def test_param_action(
        self,
        action: UpdatePreserveAction | UpdateDeleteAction,
        expected: MergePreserveAction | MergeDeleteAction,
    ) -> None:
        entry = self._entry(
            summary_action=UpdatePreserveAction(),
            description_action=UpdatePreserveAction(),
            params=(
                ParamUpdatePlan(
                    name="name",
                    sort_order=1,
                    action=action,
                    confidence=self._confidence(),
                ),
            ),
            returns=ReturnUpdatePlan(
                action=UpdatePreserveAction(),
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry,)),
        )

        assert result[0].params[0].action == expected

    def test_return_replace(self) -> None:
        value = ReturnActionValue(
            return_type="str",
            description="The generated name.",
        )

        entry = self._entry(
            summary_action=UpdatePreserveAction(),
            description_action=UpdatePreserveAction(),
            returns=ReturnUpdatePlan(
                action=ReturnUpdateReplaceAction(value=value),
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry,)),
        )

        assert result[0].returns == MergeReplaceAction(value=value)

    @pytest.mark.parametrize(
        ("action", "expected"),
        [
            (
                UpdatePreserveAction(),
                MergePreserveAction(),
            ),
            (
                UpdateDeleteAction(),
                MergeDeleteAction(),
            ),
        ],
    )
    def test_return_action(
        self,
        action: UpdatePreserveAction | UpdateDeleteAction,
        expected: MergePreserveAction | MergeDeleteAction,
    ) -> None:
        entry = self._entry(
            summary_action=UpdatePreserveAction(),
            description_action=UpdatePreserveAction(),
            returns=ReturnUpdatePlan(
                action=action,
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry,)),
        )

        assert result[0].returns == expected

    def test_raise_replace(self) -> None:
        value = RaiseActionValue(
            error_type="ValueError",
            description="Raised when the value is invalid.",
        )

        entry = self._entry(
            summary_action=UpdatePreserveAction(),
            description_action=UpdatePreserveAction(),
            raises=(
                RaiseUpdatePlan(
                    error_type="ValueError",
                    action=RaiseUpdateReplaceAction(value=value),
                    confidence=self._confidence(),
                ),
            ),
            returns=ReturnUpdatePlan(
                action=UpdatePreserveAction(),
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry,)),
        )

        assert result[0].raises == (
            RaiseMergePlan(
                exception_type="ValueError",
                action=MergeReplaceAction(value=value),
            ),
        )

    @pytest.mark.parametrize(
        ("action", "expected"),
        [
            (
                UpdatePreserveAction(),
                MergePreserveAction(),
            ),
            (
                UpdateDeleteAction(),
                MergeDeleteAction(),
            ),
        ],
    )
    def test_raise_action(
        self,
        action: UpdatePreserveAction | UpdateDeleteAction,
        expected: MergePreserveAction | MergeDeleteAction,
    ) -> None:
        entry = self._entry(
            summary_action=UpdatePreserveAction(),
            description_action=UpdatePreserveAction(),
            raises=(
                RaiseUpdatePlan(
                    error_type="ValueError",
                    action=action,
                    confidence=self._confidence(),
                ),
            ),
            returns=ReturnUpdatePlan(
                action=UpdatePreserveAction(),
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry,)),
        )

        assert result[0].raises[0].action == expected

    def test_create_complete_merge_plan(self) -> None:
        param_value = ParamActionValue(
            type="str",
            description="User name.",
        )
        return_value = ReturnActionValue(
            return_type="str",
            description="Generated name.",
        )
        raise_value = RaiseActionValue(
            error_type="ValueError",
            description="Raised when the value is invalid.",
        )

        entry = self._entry(
            summary_action=UpdateReplaceAction(value="Summary"),
            description_action=UpdateDeleteAction(),
            params=(
                ParamUpdatePlan(
                    name="name",
                    sort_order=0,
                    action=ParamUpdateReplaceAction(value=param_value),
                    confidence=self._confidence(),
                ),
            ),
            raises=(
                RaiseUpdatePlan(
                    error_type="ValueError",
                    action=RaiseUpdateReplaceAction(value=raise_value),
                    confidence=self._confidence(),
                ),
            ),
            returns=ReturnUpdatePlan(
                action=ReturnUpdateReplaceAction(value=return_value),
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry,)),
        )

        assert result == [
            MergePlan(
                identity=self._identity(),
                summary=MergeReplaceAction(value="Summary"),
                description=MergeDeleteAction(),
                params=(
                    ParamMergePlan(
                        name="name",
                        sort_order=0,
                        action=MergeReplaceAction(value=param_value),
                    ),
                ),
                returns=MergeReplaceAction(value=return_value),
                raises=(
                    RaiseMergePlan(
                        exception_type="ValueError",
                        action=MergeReplaceAction(value=raise_value),
                    ),
                ),
            ),
        ]

    def test_create_multiple_merge_plans(self) -> None:
        entry1 = self._entry(
            summary_action=UpdateReplaceAction(value="First"),
            description_action=UpdatePreserveAction(),
            returns=ReturnUpdatePlan(
                action=UpdatePreserveAction(),
                confidence=self._confidence(),
            ),
        )

        entry2 = self._entry(
            summary_action=UpdateReplaceAction(value="Second"),
            description_action=UpdateDeleteAction(),
            returns=ReturnUpdatePlan(
                action=UpdateDeleteAction(),
                confidence=self._confidence(),
            ),
        )

        result = create_merge_plan(
            DocstringUpdatePlan(entries=(entry1, entry2)),
        )

        assert len(result) == 2
        assert result[0].summary == MergeReplaceAction(value="First")
        assert result[1].summary == MergeReplaceAction(value="Second")
        assert result[1].description == MergeDeleteAction()
        assert result[1].returns == MergeDeleteAction()

    def test_empty_plan(self) -> None:
        assert (
            create_merge_plan(
                DocstringUpdatePlan(entries=()),
            )
            == []
        )
