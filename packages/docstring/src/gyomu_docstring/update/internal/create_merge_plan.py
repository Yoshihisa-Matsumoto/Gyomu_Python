from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DocstringUpdateEntry,
    DocstringUpdatePlan,
    ParamActionValue,
    ParamUpdateAction,
    ParamUpdatePlan,
    ParamUpdateReplaceAction,
    RaiseActionValue,
    RaiseUpdateAction,
    RaiseUpdatePlan,
    RaiseUpdateReplaceAction,
    ReturnActionValue,
    ReturnUpdateAction,
    ReturnUpdatePlan,
    ReturnUpdateReplaceAction,
    UpdateDeleteAction,
    UpdatePreserveAction,
    UpdateReplaceAction,
)

from gyomu_docstring.update.docstring.merge_plan import (
    MergeAction,
    MergeDeleteAction,
    MergePlan,
    MergePreserveAction,
    MergeReplaceAction,
    ParamMergePlan,
    RaiseMergePlan,
)


def create_merge_plan(plans: DocstringUpdatePlan) -> list[MergePlan]:
    merge_plans = [_create_merge_plan(entry) for entry in plans.entries]

    return merge_plans


def _convert_action(
    action: UpdateReplaceAction | UpdatePreserveAction | UpdateDeleteAction,
) -> MergeAction[str]:
    if isinstance(action, UpdateReplaceAction):
        return MergeReplaceAction(value=action.value)

    if isinstance(action, UpdatePreserveAction):
        return MergePreserveAction()

    return MergeDeleteAction()


def _convert_param_action(
    action: ParamUpdateAction,
) -> MergeAction[ParamActionValue]:
    if isinstance(action, ParamUpdateReplaceAction):
        return MergeReplaceAction(
            value=action.value,
        )

    if isinstance(action, UpdatePreserveAction):
        return MergePreserveAction()

    return MergeDeleteAction()


def _create_param_merge_plan(
    plan: ParamUpdatePlan,
) -> ParamMergePlan:
    return ParamMergePlan(
        name=plan.name,
        sort_order=plan.sort_order,
        action=_convert_param_action(plan.action),
    )


def _convert_raise_action(
    action: RaiseUpdateAction,
) -> MergeAction[RaiseActionValue]:
    if isinstance(action, RaiseUpdateReplaceAction):
        return MergeReplaceAction(
            value=action.value,
        )

    if isinstance(action, UpdatePreserveAction):
        return MergePreserveAction()

    return MergeDeleteAction()


def _create_raise_merge_plan(
    plan: RaiseUpdatePlan,
) -> RaiseMergePlan:
    return RaiseMergePlan(
        exception_type=plan.error_type,
        action=_convert_raise_action(plan.action),
    )


def _convert_return_action(
    action: ReturnUpdateAction,
) -> MergeAction[ReturnActionValue]:
    if isinstance(action, ReturnUpdateReplaceAction):
        return MergeReplaceAction(
            value=action.value,
        )

    if isinstance(action, UpdatePreserveAction):
        return MergePreserveAction()

    return MergeDeleteAction()


def _create_return_merge_plan(
    plan: ReturnUpdatePlan,
) -> MergeAction[ReturnActionValue]:
    return _convert_return_action(plan.action)


def _create_merge_plan(
    entry: DocstringUpdateEntry,
) -> MergePlan:

    return MergePlan(
        identity=entry.identity,
        summary=_convert_action(entry.summary.action),
        description=_convert_action(entry.description.action),
        params=tuple(_create_param_merge_plan(param) for param in entry.params),
        returns=_create_return_merge_plan(entry.returns),
        raises=tuple(
            _create_raise_merge_plan(raise_plan) for raise_plan in entry.raises
        ),
    )
