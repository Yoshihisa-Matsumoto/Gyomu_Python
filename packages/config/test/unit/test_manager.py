from pathlib import Path
from unittest.mock import Mock

import pytest
from gyomu_config.manager import ConfigManager
from gyomu_config.request import (
    ComplexConfigRequest,
    MergePolicy,
)
from pydantic import BaseModel
from returns.result import Failure, Success

from packages.schema.test_support.helpers import create_config_error


class TestConfig(BaseModel):
    name: str


@pytest.fixture
def config() -> TestConfig:
    return TestConfig(name="loaded")


@pytest.fixture
def default_config() -> TestConfig:
    return TestConfig(name="default")


@pytest.fixture
def resolver():
    return Mock()


@pytest.fixture
def merge_policy():
    return Mock(spec=MergePolicy)


@pytest.fixture
def manager() -> ConfigManager:
    return ConfigManager()


@pytest.fixture
def make_request(resolver, merge_policy):
    def _make_request(
        paths: tuple[Path, ...],
        default: TestConfig | None = None,
    ) -> ComplexConfigRequest[TestConfig, str]:
        resolver.get_paths.return_value = Success(paths)

        return ComplexConfigRequest(
            config_type=TestConfig,
            context="test-context",
            paths_resolver=resolver,
            default_value=default,
            merge_policy=merge_policy,
        )

    return _make_request


class TestConfigManager:
    def test_retrieve_complex_config_loads_and_caches_config(
        self,
        manager: ConfigManager,
        config: TestConfig,
        make_request,
        merge_policy,
        mocker,
        tmp_path,
    ):
        path = tmp_path / "config.json"
        path.write_text("{}", encoding="utf-8")

        retrieve_mock = mocker.patch(
            "gyomu_config.manager.retrieve_single_config",
            return_value=Success(config),
        )
        merge_policy.merge.return_value = Success(config)

        request = make_request((path,))

        result = manager.retrieve_complex_config(request)

        assert result == Success(config)
        retrieve_mock.assert_called_once()

        merge_policy.merge.assert_called_once_with(
            configs=(config,),
            default=None,
        )

    def test_retrieve_complex_config_uses_cache_on_second_call(
        self,
        manager: ConfigManager,
        config: TestConfig,
        make_request,
        merge_policy,
        mocker,
        tmp_path,
    ):
        path = tmp_path / "config.json"
        path.write_text("{}", encoding="utf-8")

        retrieve_mock = mocker.patch(
            "gyomu_config.manager.retrieve_single_config",
            return_value=Success(config),
        )
        merge_policy.merge.return_value = Success(config)

        request = make_request((path,))

        first_result = manager.retrieve_complex_config(request)
        second_result = manager.retrieve_complex_config(request)

        assert first_result == Success(config)
        assert second_result == Success(config)

        retrieve_mock.assert_called_once()
        assert merge_policy.merge.call_count == 2

    def test_retrieve_complex_config_skips_missing_config(
        self,
        manager: ConfigManager,
        make_request,
        merge_policy,
        mocker,
        tmp_path,
        default_config,
    ):
        path = tmp_path / "missing.json"

        retrieve_mock = mocker.patch(
            "gyomu_config.manager.retrieve_single_config",
            return_value=Success(None),
        )
        merge_policy.merge.return_value = Success(default_config)

        request = make_request((path,), default=default_config)

        result = manager.retrieve_complex_config(request)

        assert result == Success(default_config)

        retrieve_mock.assert_called_once()
        merge_policy.merge.assert_called_once_with(
            configs=(),
            default=default_config,
        )

    def test_retrieve_complex_config_propagates_path_resolution_error(
        self,
        manager: ConfigManager,
        resolver,
        merge_policy,
        mocker,
        make_request,
    ):
        config_error = create_config_error()
        retrieve_mock = mocker.patch(
            "gyomu_config.manager.retrieve_single_config",
        )

        request = make_request(())
        resolver.get_paths.return_value = Failure(config_error)

        result = manager.retrieve_complex_config(request)

        assert result == Failure(config_error)
        retrieve_mock.assert_not_called()
        merge_policy.merge.assert_not_called()

    def test_retrieve_complex_config_propagates_cache_error(
        self,
        manager: ConfigManager,
        make_request,
        merge_policy,
        mocker,
        tmp_path,
    ):
        config_error = create_config_error()
        path = tmp_path / "config.json"
        path.write_text("{}", encoding="utf-8")

        mocker.patch.object(
            manager._cache,
            "get",
            return_value=Failure(config_error),
        )
        retrieve_mock = mocker.patch(
            "gyomu_config.manager.retrieve_single_config",
        )

        request = make_request((path,))

        result = manager.retrieve_complex_config(request)

        assert result == Failure(config_error)
        retrieve_mock.assert_not_called()
        merge_policy.merge.assert_not_called()

    def test_retrieve_complex_config_propagates_retrieve_error(
        self,
        manager: ConfigManager,
        make_request,
        merge_policy,
        mocker,
        tmp_path,
    ):
        config_error = create_config_error()
        path = tmp_path / "config.json"
        path.write_text("{}", encoding="utf-8")

        retrieve_mock = mocker.patch(
            "gyomu_config.manager.retrieve_single_config",
            return_value=Failure(config_error),
        )

        request = make_request((path,))

        result = manager.retrieve_complex_config(request)

        assert result == Failure(config_error)
        retrieve_mock.assert_called_once()
        merge_policy.merge.assert_not_called()

    def test_retrieve_complex_config_propagates_cache_add_error(
        self,
        manager: ConfigManager,
        config: TestConfig,
        make_request,
        merge_policy,
        mocker,
        tmp_path,
    ):
        config_error = create_config_error()
        path = tmp_path / "config.json"
        path.write_text("{}", encoding="utf-8")

        mocker.patch(
            "gyomu_config.manager.retrieve_single_config",
            return_value=Success(config),
        )
        mocker.patch.object(
            manager._cache,
            "add_with_current_state",
            return_value=Failure(config_error),
        )

        request = make_request((path,))

        result = manager.retrieve_complex_config(request)

        assert result == Failure(config_error)
        merge_policy.merge.assert_not_called()

    def test_retrieve_complex_config_propagates_merge_error(
        self,
        manager: ConfigManager,
        config: TestConfig,
        make_request,
        merge_policy,
        mocker,
        tmp_path,
    ):
        config_error = create_config_error()
        path = tmp_path / "config.json"
        path.write_text("{}", encoding="utf-8")

        mocker.patch(
            "gyomu_config.manager.retrieve_single_config",
            return_value=Success(config),
        )
        merge_policy.merge.return_value = Failure(config_error)

        request = make_request((path,))

        result = manager.retrieve_complex_config(request)

        assert result == Failure(config_error)
        merge_policy.merge.assert_called_once_with(
            configs=(config,),
            default=None,
        )
