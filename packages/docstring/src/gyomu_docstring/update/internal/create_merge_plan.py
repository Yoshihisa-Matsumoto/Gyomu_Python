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
    """Create merge plans from a docstring update plan."""

    merge_plans = [_create_merge_plan(entry) for entry in plans.entries]

    return merge_plans


def _convert_description_action(
    action: UpdateReplaceAction | UpdatePreserveAction | UpdateDeleteAction | None,
) -> MergeAction[str] | None:
    """Convert an optional description action to a merge action."""

    if action is None:
        return None
    if isinstance(action, UpdateReplaceAction):
        return MergeReplaceAction(value=action.value)

    if isinstance(action, UpdatePreserveAction):
        return MergePreserveAction()

    return MergeDeleteAction()


def _convert_action(
    action: UpdateReplaceAction | UpdatePreserveAction | UpdateDeleteAction,
) -> MergeAction[str]:
    """Convert a update action to a merge action."""

    if isinstance(action, UpdateReplaceAction):
        return MergeReplaceAction(value=action.value)

    if isinstance(action, UpdatePreserveAction):
        return MergePreserveAction()

    return MergeDeleteAction()


def _convert_param_action(
    action: ParamUpdateAction,
) -> MergeAction[ParamActionValue]:
    """Convert a parameter update action to a merge action."""

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
    """Create a parameter merge plan from a parameter update plan."""

    return ParamMergePlan(
        name=plan.name,
        sort_order=plan.sort_order,
        action=_convert_param_action(plan.action),
    )


def _convert_raise_action(
    action: RaiseUpdateAction,
) -> MergeAction[RaiseActionValue]:
    """Convert a raise update action to a merge action."""

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
    """Create a raise merge plan from a raise update plan."""

    return RaiseMergePlan(
        exception_type=plan.error_type,
        action=_convert_raise_action(plan.action),
    )


def _convert_return_action(
    action: ReturnUpdateAction,
) -> MergeAction[ReturnActionValue]:
    """Convert a return update action to a merge action."""

    if isinstance(action, ReturnUpdateReplaceAction):
        return MergeReplaceAction(
            value=action.value,
        )

    if isinstance(action, UpdatePreserveAction):
        return MergePreserveAction()

    return MergeDeleteAction()


def _create_return_merge_plan(
    plan: ReturnUpdatePlan | None,
) -> MergeAction[ReturnActionValue] | None:
    """Create a return merge plan from an optional return update plan."""

    if plan is None:
        return None
    return _convert_return_action(plan.action)


def _create_merge_plan(
    entry: DocstringUpdateEntry,
) -> MergePlan:
    """Create a merge plan from a docstring update entry."""

    return MergePlan(
        identity=entry.identity,
        summary=_convert_action(entry.summary.action),
        description=_convert_description_action(
            entry.description.action if entry.description else None
        ),
        params=tuple(_create_param_merge_plan(param) for param in entry.params),
        returns=_create_return_merge_plan(entry.returns),
        raises=tuple(
            _create_raise_merge_plan(raise_plan) for raise_plan in entry.raises
        ),
    )
