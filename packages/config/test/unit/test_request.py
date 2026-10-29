from gyomu_config.request import FirstAvailableStrategy, MergePolicy, MergeStrategy
from pydantic import BaseModel
from pytest_mock import MockerFixture
from returns.result import Success


class SampleConfig(BaseModel):
    value: str


class TestFirstAvailableStrategy:
    def test_returns_first_config_when_multiple_configs_exist(
        self,
    ) -> None:
        first = SampleConfig(value="first")
        second = SampleConfig(value="second")
        default = SampleConfig(value="default")

        strategy = FirstAvailableStrategy[SampleConfig]()

        result = strategy.apply(
            configs=(first, second),
            default=default,
        )

        assert result == Success(first)

    def test_returns_config_when_single_config_exists(
        self,
    ) -> None:
        config = SampleConfig(value="config")
        default = SampleConfig(value="default")

        strategy = FirstAvailableStrategy[SampleConfig]()

        result = strategy.apply(
            configs=(config,),
            default=default,
        )

        assert result == Success(config)

    def test_returns_default_when_no_configs_exist(
        self,
    ) -> None:
        default = SampleConfig(value="default")

        strategy = FirstAvailableStrategy[SampleConfig]()

        result = strategy.apply(
            configs=(),
            default=default,
        )

        assert result == Success(default)

    def test_returns_none_when_no_configs_and_no_default_exist(
        self,
    ) -> None:
        strategy = FirstAvailableStrategy[SampleConfig]()

        result = strategy.apply(
            configs=(),
            default=None,
        )

        assert result == Success(None)


class TestMergePolicy:
    def test_delegates_to_strategy(
        self,
        mocker: MockerFixture,
    ) -> None:
        config = SampleConfig(value="config")
        default = SampleConfig(value="default")
        expected = Success(config)

        strategy = mocker.create_autospec(
            MergeStrategy,
            instance=True,
        )
        strategy.apply.return_value = expected

        policy = MergePolicy[SampleConfig](strategy=strategy)

        result = policy.merge(
            configs=(config,),
            default=default,
        )

        assert result == expected
        strategy.apply.assert_called_once_with(
            (config,),
            default,
        )
