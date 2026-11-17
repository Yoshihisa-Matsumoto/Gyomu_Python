from pathlib import Path
from unittest.mock import MagicMock

import pytest
from gyomu_config.file.internal.retrieve import _ResolvedPathRequest
from gyomu_config.file.retrieve_complex import retrieve_complex_config
from gyomu_config.request import ComplexConfigRequest
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class SampleConfig(BaseModel):
    value: str


class TestRetrieveComlexConfig:
    @pytest.fixture
    def config_type(self) -> type[SampleConfig]:
        return SampleConfig

    @pytest.fixture
    def context(self) -> str:
        return "test-context"

    @pytest.fixture
    def default_value(self) -> SampleConfig:
        return SampleConfig(value="default")

    @pytest.fixture
    def paths_resolver(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def merge_policy(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def complex_request(
        self,
        config_type: type[SampleConfig],
        context: str,
        paths_resolver: MagicMock,
        merge_policy: MagicMock,
        default_value: SampleConfig,
    ) -> ComplexConfigRequest[SampleConfig, str]:
        return ComplexConfigRequest(
            config_type=config_type,
            context=context,
            paths_resolver=paths_resolver,
            merge_policy=merge_policy,
            default_value=default_value,
        )

    def test_returns_failure_when_path_resolution_fails(
        self,
        complex_request: ComplexConfigRequest[SampleConfig, str],
        paths_resolver: MagicMock,
        merge_policy: MagicMock,
    ) -> None:
        error = ConfigError(
            source="json",
            message="failed to resolve paths",
            phase="path-resolve",
        )
        paths_resolver.get_paths.return_value = Failure(error)
        complex_request.merge_policy = merge_policy
        result = retrieve_complex_config(complex_request)

        assert result == Failure(error)
        paths_resolver.get_paths.assert_called_once_with(complex_request.context)
        complex_request.merge_policy.merge.assert_not_called()

    def test_returns_failure_when_config_retrieval_fails(
        self,
        complex_request: ComplexConfigRequest[SampleConfig, str],
        paths_resolver: MagicMock,
        mocker: MockerFixture,
        merge_policy: MagicMock,
    ) -> None:
        path = Path("config.json")
        error = ConfigError(
            source="json",
            message="failed to retrieve config",
            phase="load",
        )
        paths_resolver.get_paths.return_value = Success((path,))

        retrieve_mock = mocker.patch(
            "gyomu_config.file.retrieve_complex.retrieve_single_config",
            return_value=Failure(error),
        )
        complex_request.merge_policy = merge_policy
        result = retrieve_complex_config(complex_request)

        assert result == Failure(error)
        retrieve_mock.assert_called_once()

        actual_request = retrieve_mock.call_args.kwargs["request"]

        assert isinstance(actual_request, _ResolvedPathRequest)
        assert actual_request.config_type is complex_request.config_type
        assert actual_request.path == path
        complex_request.merge_policy.merge.assert_not_called()

    def test_merges_retrieved_configs_in_path_order(
        self,
        complex_request: ComplexConfigRequest[SampleConfig, str],
        paths_resolver: MagicMock,
        default_value: SampleConfig,
        mocker: MockerFixture,
        merge_policy: MagicMock,
    ) -> None:
        first_path = Path("first.json")
        missing_path = Path("missing.json")
        third_path = Path("third.json")

        first_config = SampleConfig(value="first")
        third_config = SampleConfig(value="third")
        merged_config = SampleConfig(value="merged")

        paths_resolver.get_paths.return_value = Success(
            (first_path, missing_path, third_path)
        )

        retrieve_mock = mocker.patch(
            "gyomu_config.file.retrieve_complex.retrieve_single_config",
            side_effect=[
                Success(first_config),
                Success(None),
                Success(third_config),
            ],
        )
        complex_request.merge_policy = merge_policy
        complex_request.merge_policy.merge.return_value = Success(merged_config)

        result = retrieve_complex_config(complex_request)

        assert result == Success(merged_config)
        assert retrieve_mock.call_count == 3

        actual_requests = [
            call.kwargs["request"] for call in retrieve_mock.call_args_list
        ]

        assert [(request.config_type, request.path) for request in actual_requests] == [
            (complex_request.config_type, first_path),
            (complex_request.config_type, missing_path),
            (complex_request.config_type, third_path),
        ]
        complex_request.merge_policy.merge.assert_called_once_with(
            configs=(first_config, third_config),
            default=default_value,
        )

    def test_uses_default_when_all_configs_are_missing(
        self,
        complex_request: ComplexConfigRequest[SampleConfig, str],
        paths_resolver: MagicMock,
        default_value: SampleConfig,
        mocker: MockerFixture,
        merge_policy: MagicMock,
    ) -> None:
        paths = (Path("first.json"), Path("second.json"))
        paths_resolver.get_paths.return_value = Success(paths)

        mocker.patch(
            "gyomu_config.file.retrieve_complex.retrieve_single_config",
            side_effect=[Success(None), Success(None)],
        )
        complex_request.merge_policy = merge_policy
        complex_request.merge_policy.merge.return_value = Success(default_value)

        result = retrieve_complex_config(complex_request)

        assert result == Success(default_value)
        complex_request.merge_policy.merge.assert_called_once_with(
            configs=(),
            default=default_value,
        )

    def test_uses_default_when_no_paths_are_resolved(
        self,
        complex_request: ComplexConfigRequest[SampleConfig, str],
        paths_resolver: MagicMock,
        default_value: SampleConfig,
        merge_policy: MagicMock,
    ) -> None:
        paths_resolver.get_paths.return_value = Success(())
        complex_request.merge_policy = merge_policy
        complex_request.merge_policy.merge.return_value = Success(default_value)

        result = retrieve_complex_config(complex_request)

        assert result == Success(default_value)
        complex_request.merge_policy.merge.assert_called_once_with(
            configs=(),
            default=default_value,
        )
