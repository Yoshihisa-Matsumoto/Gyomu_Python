from pathlib import Path
from unittest.mock import Mock

import pytest
from gyomu_config.manager import ConfigManager
from gyomu_config.request import (
    ComplexConfigExtractorRequest,
    ComplexConfigRequest,
    ConfigExtractor,
    MergePolicy,
)
from pydantic import BaseModel
from returns.result import Failure, Success

from packages.schema.test_support.helpers import create_config_error


class SampleConfig(BaseModel):
    name: str


class SampleExtractedConfig(BaseModel):
    value: str


class SampleContainerConfig(BaseModel):
    name: str


@pytest.fixture
def config() -> SampleConfig:
    return SampleConfig(name="loaded")


@pytest.fixture
def default_config() -> SampleConfig:
    return SampleConfig(name="default")


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
        default: SampleConfig | None = None,
    ) -> ComplexConfigRequest[SampleConfig, str]:
        resolver.get_paths.return_value = Success(paths)

        return ComplexConfigRequest(
            config_type=SampleConfig,
            context="test-context",
            paths_resolver=resolver,
            default_value=default,
            merge_policy=merge_policy,
        )

    return _make_request


@pytest.fixture
def extracted_config() -> SampleExtractedConfig:
    return SampleExtractedConfig(value="loaded")


@pytest.fixture
def extractor():
    return Mock(spec=ConfigExtractor)


@pytest.fixture
def make_extracted_request(resolver, merge_policy, extractor):
    def _make_request(
        paths: tuple[Path, ...],
        default: SampleExtractedConfig | None = None,
    ) -> ComplexConfigExtractorRequest[
        SampleContainerConfig,
        SampleExtractedConfig,
        str,
    ]:
        resolver.get_paths.return_value = Success(paths)

        return ComplexConfigExtractorRequest(
            config_type=SampleContainerConfig,
            context="test-context",
            paths_resolver=resolver,
            default_value=default,
            extractor=extractor,
            merge_policy=merge_policy,
        )

    return _make_request


class TestConfigManager:
    class TestRetrieveComplexConfig:
        def test_loads_and_caches_config(
            self,
            manager: ConfigManager,
            config: SampleConfig,
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

        def test_uses_cache_on_second_call(
            self,
            manager: ConfigManager,
            config: SampleConfig,
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

        def test_skips_missing_config(
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

        def test_propagates_path_resolution_error(
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

        def test_propagates_cache_error(
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

        def test_propagates_retrieve_error(
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

        def test_propagates_cache_add_error(
            self,
            manager: ConfigManager,
            config: SampleConfig,
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

        def test_propagates_merge_error(
            self,
            manager: ConfigManager,
            config: SampleConfig,
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

    class TestRetrieveExtractedConfig:
        def test_extracts_configs_in_order_and_merges_results(
            self,
            manager: ConfigManager,
            extracted_config: SampleExtractedConfig,
            make_extracted_request,
            extractor,
            merge_policy,
            mocker,
        ):
            first_config = SampleContainerConfig(name="first")
            second_config = SampleContainerConfig(name="second")
            third_config = SampleContainerConfig(name="third")
            another_extracted_config = SampleExtractedConfig(
                value="another",
            )

            mocker.patch.object(
                manager,
                "_retrieve_configs",
                return_value=Success(
                    (first_config, second_config, third_config),
                ),
            )
            extractor.extract.side_effect = [
                Success(None),
                Success(extracted_config),
                Success(another_extracted_config),
            ]
            merge_policy.merge.return_value = Success(extracted_config)

            request = make_extracted_request(())

            result = manager.retrieve_extracted_config(request)

            assert result == Success(extracted_config)
            assert extractor.extract.call_args_list == [
                mocker.call(first_config, context="test-context"),
                mocker.call(second_config, context="test-context"),
                mocker.call(third_config, context="test-context"),
            ]
            merge_policy.merge.assert_called_once_with(
                configs=(
                    extracted_config,
                    another_extracted_config,
                ),
                default=None,
            )

        def test_uses_default_when_no_config_is_extracted(
            self,
            manager: ConfigManager,
            default_config: SampleConfig,
            make_extracted_request,
            extractor,
            merge_policy,
            mocker,
        ):
            default_extracted_config = SampleExtractedConfig(
                value="default",
            )
            first_config = SampleContainerConfig(name="first")
            second_config = SampleContainerConfig(name="second")

            mocker.patch.object(
                manager,
                "_retrieve_configs",
                return_value=Success((first_config, second_config)),
            )
            extractor.extract.side_effect = [
                Success(None),
                Success(None),
            ]
            merge_policy.merge.return_value = Success(
                default_extracted_config,
            )

            request = make_extracted_request(
                (),
                default=default_extracted_config,
            )

            result = manager.retrieve_extracted_config(request)

            assert result == Success(default_extracted_config)
            merge_policy.merge.assert_called_once_with(
                configs=(),
                default=default_extracted_config,
            )

        def test_propagates_retrieve_configs_error(
            self,
            manager: ConfigManager,
            make_extracted_request,
            extractor,
            merge_policy,
            mocker,
        ):
            config_error = create_config_error()

            mocker.patch.object(
                manager,
                "_retrieve_configs",
                return_value=Failure(config_error),
            )

            request = make_extracted_request(())

            result = manager.retrieve_extracted_config(request)

            assert result == Failure(config_error)
            extractor.extract.assert_not_called()
            merge_policy.merge.assert_not_called()

        def test_propagates_extractor_error(
            self,
            manager: ConfigManager,
            make_extracted_request,
            extractor,
            merge_policy,
            mocker,
        ):
            config_error = create_config_error()
            first_config = SampleContainerConfig(name="first")
            second_config = SampleContainerConfig(name="second")

            mocker.patch.object(
                manager,
                "_retrieve_configs",
                return_value=Success((first_config, second_config)),
            )
            extractor.extract.side_effect = [
                Success(None),
                Failure(config_error),
            ]

            request = make_extracted_request(())

            result = manager.retrieve_extracted_config(request)

            assert result == Failure(config_error)
            assert extractor.extract.call_count == 2
            merge_policy.merge.assert_not_called()

        def test_propagates_merge_error(
            self,
            manager: ConfigManager,
            extracted_config: SampleExtractedConfig,
            make_extracted_request,
            extractor,
            merge_policy,
            mocker,
        ):
            config_error = create_config_error()
            container_config = SampleContainerConfig(name="first")

            mocker.patch.object(
                manager,
                "_retrieve_configs",
                return_value=Success((container_config,)),
            )
            extractor.extract.return_value = Success(extracted_config)
            merge_policy.merge.return_value = Failure(config_error)

            request = make_extracted_request(())

            result = manager.retrieve_extracted_config(request)

            assert result == Failure(config_error)
            merge_policy.merge.assert_called_once_with(
                configs=(extracted_config,),
                default=None,
            )
