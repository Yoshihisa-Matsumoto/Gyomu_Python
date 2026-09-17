from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from gyomu_ai_compiler.pipelines.docstring_update.context.file_context import (
    DocstringRetryOption,
)
from gyomu_docstring.update.internal.build_update_plan import (
    build_docstring_update_plan_with_retry,
    override_docstring_update_plan,
)
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiOperation,
)
from gyomu_schema.option.retry import RetryOption
from gyomu_schema.option.update import UpdateDebugInfoOption, UpdateOption
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.ai_compiler.ai_compiler_test_support.helper import (
    create_declaration_info_from_declaration_identity,
    create_docstring_declaration_context,
    create_docstring_file_context,
    create_docstring_update_entry,
    create_docstring_update_plan,
)
from packages.schema.schema_test_support.helpers import (
    create_class_analysis,
    create_declaration_identity,
    create_file_analysis_context,
    create_location,
)


@pytest.mark.asyncio
async def test_build_docstring_update_plan_with_retry_returns_plan_when_first_attempt_is_valid(
    mocker: MockerFixture,
) -> None:
    foo = create_declaration_identity("foo")
    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info_from_declaration_identity(foo),
                foo,
            ),
        )
    )
    file_context = create_file_analysis_context(
        create_class_analysis(indent=0, location=create_location(), identity=foo)
    )

    plan = create_docstring_update_plan(
        entries=(
            create_docstring_update_entry(
                identity=foo,
            ),
        )
    )

    generate_mock = mocker.patch(
        "gyomu_docstring.update.internal.build_update_plan.generate_docstring_update_plan",
        new_callable=AsyncMock,
        return_value=Success(plan),
    )

    result = await build_docstring_update_plan_with_retry(
        context,
        file_context,
    )
    generate_mock.assert_awaited_once()
    assert result == Success(plan)
    generate_mock.assert_awaited_once_with(context, None)


@pytest.mark.asyncio
async def test_build_docstring_update_plan_with_retry_dumps_plan_to_file(
    mocker: MockerFixture,
) -> None:
    foo = create_declaration_identity("foo")
    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info_from_declaration_identity(foo),
                foo,
            ),
        )
    )
    file_context = create_file_analysis_context(
        create_class_analysis(indent=0, location=create_location(), identity=foo)
    )
    plan = create_docstring_update_plan(
        entries=(
            create_docstring_update_entry(
                identity=foo,
            ),
        )
    )

    generate_mock = mocker.patch(
        "gyomu_docstring.update.internal.build_update_plan.generate_docstring_update_plan",
        new_callable=AsyncMock,
        return_value=Success(plan),
    )

    write_json = mocker.patch(
        "gyomu_docstring.update.internal.build_update_plan.write_json",
    )

    option = UpdateOption(
        debug_info=UpdateDebugInfoOption(
            docstring_update_plan=True,
            dump_to_file=True,
        ),
    )

    result = await build_docstring_update_plan_with_retry(
        context,
        file_context,
        option,
    )

    assert isinstance(result, Success)
    write_json.assert_called_once_with(
        Path("log") / "DocstringUpdatePlan.json",
        plan,
    )


@pytest.mark.asyncio
async def test_build_docstring_update_plan_with_retry_does_not_dump_plan_by_default(
    mocker: MockerFixture,
) -> None:
    foo = create_declaration_identity("foo")
    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info_from_declaration_identity(foo),
                foo,
            ),
        )
    )
    file_context = create_file_analysis_context(
        create_class_analysis(indent=0, location=create_location(), identity=foo)
    )
    plan = create_docstring_update_plan(
        entries=(
            create_docstring_update_entry(
                identity=foo,
            ),
        )
    )

    mocker.patch(
        "gyomu_docstring.update.internal.build_update_plan.generate_docstring_update_plan",
        new_callable=AsyncMock,
        return_value=Success(plan),
    )
    write_json = mocker.patch(
        "gyomu_docstring.update.internal.build_update_plan.write_json",
    )

    result = await build_docstring_update_plan_with_retry(
        context,
        file_context,
    )

    assert isinstance(result, Success)
    write_json.assert_not_called()


@pytest.mark.asyncio
async def test_build_docstring_update_plan_with_retry_passes_retry_option_to_generator(
    mocker: MockerFixture,
) -> None:
    foo = create_declaration_identity("foo")
    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info_from_declaration_identity(foo),
                foo,
            ),
        )
    )
    file_context = create_file_analysis_context(
        create_class_analysis(indent=0, location=create_location(), identity=foo)
    )
    plan = create_docstring_update_plan(
        entries=(
            create_docstring_update_entry(
                identity=foo,
            ),
        )
    )

    retry_option = RetryOption(max_attempts=2, observer=None)

    option = UpdateOption(
        retry_option=retry_option,
    )

    generate_mock = mocker.patch(
        "gyomu_docstring.update.internal.build_update_plan.generate_docstring_update_plan",
        new_callable=AsyncMock,
        return_value=Success(plan),
    )

    result = await build_docstring_update_plan_with_retry(
        context,
        file_context,
        option,
    )

    assert result == Success(plan)
    generate_mock.assert_awaited_once_with(
        context,
        retry_option,
    )


@pytest.mark.asyncio
async def test_build_docstring_update_plan_with_retry_combines_original_and_retry_plan(
    mocker: MockerFixture,
) -> None:
    foo = create_declaration_identity("foo")
    bar = create_declaration_identity("bar")
    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info_from_declaration_identity(foo),
                foo,
            ),
            create_docstring_declaration_context(
                create_declaration_info_from_declaration_identity(bar),
                bar,
            ),
        )
    )
    file_context = create_file_analysis_context(
        create_class_analysis(indent=0, location=create_location(), identity=foo),
        create_class_analysis(indent=0, location=create_location(), identity=bar),
    )

    foo_entry = create_docstring_update_entry(identity=foo)
    bar_entry = create_docstring_update_entry(identity=bar)

    first_plan = create_docstring_update_plan(
        entries=(foo_entry,),
    )
    second_plan = create_docstring_update_plan(
        entries=(bar_entry,),
    )
    expected_plan = create_docstring_update_plan(
        entries=(foo_entry, bar_entry),
    )

    generate_mock = mocker.patch(
        "gyomu_docstring.update.internal.build_update_plan.generate_docstring_update_plan",
        new_callable=AsyncMock,
        side_effect=[
            Success(first_plan),
            Success(second_plan),
        ],
    )

    result = await build_docstring_update_plan_with_retry(
        context,
        file_context,
    )

    assert result == Success(expected_plan)
    assert generate_mock.await_count == 2

    second_context = generate_mock.await_args_list[1].args[0]

    assert second_context.retry == DocstringRetryOption(
        attempt=1,
        missing_identity=(bar,),
    )


@pytest.mark.asyncio
async def test_build_docstring_update_plan_with_retry_fails_after_five_attempts(
    mocker: MockerFixture,
) -> None:
    foo = create_declaration_identity("foo")
    bar = create_declaration_identity("bar")
    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info_from_declaration_identity(foo),
                foo,
            ),
            create_docstring_declaration_context(
                create_declaration_info_from_declaration_identity(bar),
                bar,
            ),
        )
    )
    file_context = create_file_analysis_context(
        create_class_analysis(indent=0, location=create_location(), identity=foo),
        create_class_analysis(indent=0, location=create_location(), identity=bar),
    )

    foo_entry = create_docstring_update_entry(identity=foo)
    bar_entry = create_docstring_update_entry(identity=bar)

    incomplete_plan = create_docstring_update_plan(
        entries=(foo_entry,),
    )

    generate_mock = mocker.patch(
        "gyomu_docstring.update.internal.build_update_plan.generate_docstring_update_plan",
        new_callable=AsyncMock,
        return_value=Success(incomplete_plan),
    )

    result = await build_docstring_update_plan_with_retry(
        context,
        file_context,
    )

    assert result is not None
    assert isinstance(result, Failure)
    assert generate_mock.await_count == 5


@pytest.mark.asyncio
async def test_build_docstring_update_plan_with_retry_returns_failure_when_generation_fails(
    mocker: MockerFixture,
) -> None:
    foo = create_declaration_identity("foo")
    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info_from_declaration_identity(foo),
                foo,
            ),
        )
    )
    file_context = create_file_analysis_context(
        create_class_analysis(indent=0, location=create_location(), identity=foo)
    )

    cause = AiError(
        message="test error",
        operation=AiOperation.GENERATE,
        model=None,
        model_key=None,
        phase=AiErrorPhase.REQUEST,
        resolution=AiFailResolution(),
    )

    generate_mock = mocker.patch(
        "gyomu_docstring.update.internal.build_update_plan.generate_docstring_update_plan",
        new_callable=AsyncMock,
        return_value=Failure(cause),
    )

    result = await build_docstring_update_plan_with_retry(
        context,
        file_context,
    )

    assert isinstance(result, Failure)
    assert generate_mock.await_count == 1

    error = result.failure()

    assert error.message == "fail to retrieve correct Docstring with maximum retry"
    assert error.phase == "merge-plan"


class TestOverrideDocstringUpdatePlan:
    def test_override_docstring_update_plan_filters_entries_not_in_context(
        self,
    ) -> None:
        foo = create_declaration_identity("foo")
        unknown = create_declaration_identity("unknown")
        foo_entry = create_docstring_update_entry(identity=foo)
        unknown_entry = create_docstring_update_entry(identity=unknown)

        context = create_docstring_file_context(
            symbols=(
                create_docstring_declaration_context(
                    create_declaration_info_from_declaration_identity(foo),
                    foo,
                ),
            )
        )
        plan = create_docstring_update_plan(
            entries=(foo_entry, unknown_entry),
        )

        result = override_docstring_update_plan(
            context=context,
            plan=plan,
            original_plan=None,
        )

        assert result == create_docstring_update_plan(
            entries=(foo_entry,),
        )

    def test_override_docstring_update_plan_filters_entries_when_retry_is_none(
        self,
    ) -> None:
        foo = create_declaration_identity("foo")
        unknown = create_declaration_identity("unknown")
        foo_entry = create_docstring_update_entry(identity=foo)
        unknown_entry = create_docstring_update_entry(identity=unknown)

        context = create_docstring_file_context(
            symbols=(
                create_docstring_declaration_context(
                    create_declaration_info_from_declaration_identity(foo),
                    foo,
                ),
            )
        )
        plan = create_docstring_update_plan(
            entries=(foo_entry, unknown_entry),
        )
        original_plan = create_docstring_update_plan(
            entries=(foo_entry,),
        )

        result = override_docstring_update_plan(
            context=context,
            plan=plan,
            original_plan=original_plan,
        )

        assert result == create_docstring_update_plan(
            entries=(foo_entry,),
        )

    def test_override_docstring_update_plan_adds_missing_entries_to_original_plan(
        self,
    ) -> None:
        foo = create_declaration_identity("foo")
        bar = create_declaration_identity("bar")
        foo_entry = create_docstring_update_entry(identity=foo)
        bar_entry = create_docstring_update_entry(identity=bar)

        context = create_docstring_file_context(
            symbols=(
                create_docstring_declaration_context(
                    create_declaration_info_from_declaration_identity(foo),
                    foo,
                ),
                create_docstring_declaration_context(
                    create_declaration_info_from_declaration_identity(bar),
                    bar,
                ),
            ),
            retry=DocstringRetryOption(
                attempt=1,
                missing_identity=(bar,),
            ),
        )

        original_plan = create_docstring_update_plan(
            entries=(foo_entry,),
        )
        plan = create_docstring_update_plan(
            entries=(bar_entry,),
        )

        result = override_docstring_update_plan(
            context=context,
            plan=plan,
            original_plan=original_plan,
        )

        assert result == create_docstring_update_plan(
            entries=(foo_entry, bar_entry),
        )

    def test_override_docstring_update_plan_keeps_original_when_missing_entry_is_not_in_plan(
        self,
    ) -> None:
        foo = create_declaration_identity("foo")
        bar = create_declaration_identity("bar")
        foo_entry = create_docstring_update_entry(identity=foo)
        bar_entry = create_docstring_update_entry(identity=bar)

        context = create_docstring_file_context(
            symbols=(
                create_docstring_declaration_context(
                    create_declaration_info_from_declaration_identity(foo),
                    foo,
                ),
                create_docstring_declaration_context(
                    create_declaration_info_from_declaration_identity(bar),
                    bar,
                ),
            ),
            retry=DocstringRetryOption(
                attempt=1,
                missing_identity=(bar,),
            ),
        )

        original_plan = create_docstring_update_plan(
            entries=(foo_entry,),
        )
        plan = create_docstring_update_plan(
            entries=(),
        )

        result = override_docstring_update_plan(
            context=context,
            plan=plan,
            original_plan=original_plan,
        )

        assert result == original_plan

    def test_override_docstring_update_plan_only_adds_entries_for_missing_identities(
        self,
    ) -> None:
        foo = create_declaration_identity("foo")
        bar = create_declaration_identity("bar")
        baz = create_declaration_identity("baz")
        foo_entry = create_docstring_update_entry(identity=foo)
        bar_entry = create_docstring_update_entry(identity=bar)
        baz_entry = create_docstring_update_entry(identity=baz)

        context = create_docstring_file_context(
            symbols=(
                create_docstring_declaration_context(
                    create_declaration_info_from_declaration_identity(foo),
                    foo,
                ),
                create_docstring_declaration_context(
                    create_declaration_info_from_declaration_identity(bar),
                    bar,
                ),
                create_docstring_declaration_context(
                    create_declaration_info_from_declaration_identity(baz),
                    baz,
                ),
            ),
            retry=DocstringRetryOption(
                attempt=1,
                missing_identity=(bar,),
            ),
        )

        original_plan = create_docstring_update_plan(
            entries=(foo_entry,),
        )
        plan = create_docstring_update_plan(
            entries=(bar_entry, baz_entry),
        )

        result = override_docstring_update_plan(
            context=context,
            plan=plan,
            original_plan=original_plan,
        )

        assert result == create_docstring_update_plan(
            entries=(foo_entry, bar_entry),
        )
