from unittest.mock import MagicMock

import pytest
from gyomu_config.manager import ConfigManager
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    PackageModelDefaults,
    PrimitiveDefault,
)
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.defaults.load import (
    load_primitive_parameter_default_config,
    load_symbol_parameter_default_config,
)
from gyomu_test.helper.defaults.resolution import (
    PrimitiveDefaultConfigContext,
    SymbolDefaultConfigContext,
)
from returns.result import Failure, Success


class TestLoadPrimitiveParameterDefaultConfig:
    @pytest.fixture
    def context(self) -> PrimitiveDefaultConfigContext:
        return MagicMock(spec=PrimitiveDefaultConfigContext)

    @pytest.fixture
    def config_manager(self) -> MagicMock:
        return MagicMock(spec=ConfigManager)

    def test_returns_loaded_config(
        self,
        context: PrimitiveDefaultConfigContext,
        config_manager: MagicMock,
    ) -> None:
        expected = MagicMock(spec=PrimitiveDefault)
        config_manager.retrieve_extracted_config.return_value = Success(expected)

        result = load_primitive_parameter_default_config(
            context=context,
            config_manager=config_manager,
        )

        assert result == Success(expected)
        config_manager.retrieve_extracted_config.assert_called_once()

        request = config_manager.retrieve_extracted_config.call_args.args[0]
        assert request.config_type is PackageModelDefaults
        assert request.context is context
        assert request.default_value is None
        assert request.paths_resolver is request.extractor

    def test_returns_none_when_config_is_not_found(
        self,
        context: PrimitiveDefaultConfigContext,
        config_manager: MagicMock,
    ) -> None:
        config_manager.retrieve_extracted_config.return_value = Success(None)

        result = load_primitive_parameter_default_config(
            context=context,
            config_manager=config_manager,
        )

        assert result == Success(None)

    def test_wraps_error(
        self,
        context: PrimitiveDefaultConfigContext,
        config_manager: MagicMock,
    ) -> None:
        source_error = GyomuTestError("Source error")
        config_manager.retrieve_extracted_config.return_value = Failure(source_error)

        result = load_primitive_parameter_default_config(
            context=context,
            config_manager=config_manager,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, GyomuTestError)
        assert str(error).startswith(
            "Failed to load primitive parameter default config"
        )


class TestLoadSymbolParameterDefaultConfig:
    @pytest.fixture
    def context(self) -> SymbolDefaultConfigContext:
        return MagicMock(spec=SymbolDefaultConfigContext)

    @pytest.fixture
    def config_manager(self) -> MagicMock:
        return MagicMock(spec=ConfigManager)

    def test_returns_loaded_config(
        self,
        context: SymbolDefaultConfigContext,
        config_manager: MagicMock,
    ) -> None:
        expected = MagicMock(spec=ModelDefault)
        config_manager.retrieve_extracted_config.return_value = Success(expected)

        result = load_symbol_parameter_default_config(
            context=context,
            config_manager=config_manager,
        )

        assert result == Success(expected)
        config_manager.retrieve_extracted_config.assert_called_once()

        request = config_manager.retrieve_extracted_config.call_args.args[0]
        assert request.config_type is PackageModelDefaults
        assert request.context is context
        assert request.default_value is None
        assert request.paths_resolver is request.extractor

    def test_returns_none_when_config_is_not_found(
        self,
        context: SymbolDefaultConfigContext,
        config_manager: MagicMock,
    ) -> None:
        config_manager.retrieve_extracted_config.return_value = Success(None)

        result = load_symbol_parameter_default_config(
            context=context,
            config_manager=config_manager,
        )

        assert result == Success(None)

    def test_wraps_error(
        self,
        context: SymbolDefaultConfigContext,
        config_manager: MagicMock,
    ) -> None:
        source_error = GyomuTestError("Source error")
        config_manager.retrieve_extracted_config.return_value = Failure(source_error)

        result = load_symbol_parameter_default_config(
            context=context,
            config_manager=config_manager,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, GyomuTestError)
        assert str(error).startswith("Failed to load symbol parameter default config")
