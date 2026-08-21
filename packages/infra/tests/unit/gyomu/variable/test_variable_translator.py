from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from gyomu_schema.error.database import DatabaseError
from returns.result import Failure, Success

from gyomu_infra.gyomu.date.business_calendar import BusinessCalendarService
from gyomu_infra.gyomu.variable.variable_translator import VariableTranslatorImpl


@pytest.fixture
def market_holiday() -> MagicMock:
    return MagicMock()


@pytest.fixture
def parameter_master() -> MagicMock:
    return MagicMock()


class TestVariableTranslator_ParseDate:
    def test_returns_today(
        self, market_holiday: MagicMock, parameter_master: MagicMock
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        access = VariableTranslatorImpl(market_holiday, parameter_master)

        target_date = date(2026, 8, 21)

        result = access.parse_date("TODAY", target_date)

        assert result == Success(target_date)

    def test_returns_next_day(
        self, market_holiday: MagicMock, parameter_master: MagicMock
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        access = VariableTranslatorImpl(market_holiday, parameter_master)

        target_date = date(2026, 8, 21)

        result = access.parse_date("NEXTDAY", target_date)

        assert result == Success(date(2026, 8, 22))

    def test_returns_previous_day(
        self, market_holiday: MagicMock, parameter_master: MagicMock
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        access = VariableTranslatorImpl(market_holiday, parameter_master)

        target_date = date(2026, 8, 21)

        result = access.parse_date("PREVDAY", target_date)

        assert result == Success(date(2026, 8, 20))

    def test_returns_date_with_factor(
        self, market_holiday: MagicMock, parameter_master: MagicMock
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        access = VariableTranslatorImpl(market_holiday, parameter_master)

        target_date = date(2026, 8, 21)

        result = access.parse_date("3$NEXTDAY", target_date)

        assert result == Success(date(2026, 8, 24))

    @pytest.mark.parametrize(
        ("keyword", "expected"),
        [
            ("JP$TODAY", date(2026, 8, 21)),
            ("JP$BOM", date(2026, 8, 1)),
            ("JP$2$BOM", date(2026, 8, 2)),
            ("JP$EOM", date(2026, 8, 31)),
            ("JP$2$EOM", date(2026, 8, 30)),
            ("JP$NEXTDAY", date(2026, 8, 22)),
            ("JP$3$NEXTDAY", date(2026, 8, 24)),
            ("JP$PREVDAY", date(2026, 8, 20)),
            ("JP$3$PREVDAY", date(2026, 8, 18)),
            ("JP$EOY", date(2026, 12, 31)),
            ("JP$2$EOY", date(2026, 12, 30)),
            ("JP$BOY", date(2026, 1, 1)),
            ("JP$2$BOY", date(2026, 1, 2)),
        ],
    )
    def test_returns_calendar_independent_date(
        self,
        keyword: str,
        expected: date,
        market_holiday: MagicMock,
        parameter_master: MagicMock,
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        access = VariableTranslatorImpl(market_holiday, parameter_master)

        target_date = date(2026, 8, 21)

        result = access.parse_date(keyword, target_date)

        assert result == Success(expected)

    @pytest.mark.parametrize(
        ("keyword", "method_name", "expected"),
        [
            (
                "BBOM",
                "business_day_of_beginning_month_with_offset",
                date(2026, 8, 3),
            ),
            (
                "NEXTBBOM",
                "business_day_of_beginning_of_next_month_with_offset",
                date(2026, 9, 1),
            ),
            (
                "BEOM",
                "business_day_of_beginning_of_next_month_with_offset",
                date(2026, 8, 31),
            ),
            (
                "NEXTBEOM",
                "business_day_of_beginning_month_with_offset",
                date(2026, 9, 30),
            ),
            (
                "PREVBEOM",
                "business_day",
                date(2026, 7, 31),
            ),
            (
                "NEXTBUS",
                "business_day",
                date(2026, 8, 24),
            ),
            (
                "PREVBUS",
                "business_day",
                date(2026, 8, 20),
            ),
            (
                "BEOY",
                "business_day",
                date(2026, 12, 31),
            ),
            (
                "BBOY",
                "business_day",
                date(2026, 1, 2),
            ),
        ],
    )
    def test_returns_business_calendar_date(
        self,
        keyword: str,
        method_name: str,
        expected: date,
        market_holiday: MagicMock,
        parameter_master: MagicMock,
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        business_calendar = MagicMock()
        getattr(business_calendar, method_name).return_value = expected

        # BBOYは is_business_day() も使う
        if keyword == "BBOY":
            business_calendar.is_business_day.return_value = False

        with patch.object(
            BusinessCalendarService,
            "get",
            return_value=Success(business_calendar),
        ):
            access = VariableTranslatorImpl(market_holiday, parameter_master)

            result = access.parse_date(
                keyword,
                date(2026, 8, 21),
            )

        assert result == Success(expected)

    def test_bbom_passes_factor_index(
        self,
        market_holiday: MagicMock,
        parameter_master: MagicMock,
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        business_calendar = MagicMock()
        expected = date(2026, 8, 5)
        business_calendar.business_day_of_beginning_month_with_offset.return_value = (
            expected
        )

        with patch.object(
            BusinessCalendarService,
            "get",
            return_value=Success(business_calendar),
        ):
            access = VariableTranslatorImpl(market_holiday, parameter_master)

            result = access.parse_date(
                "JP$3$BBOM",
                date(2026, 8, 21),
            )

        assert result == Success(expected)

        business_calendar.business_day_of_beginning_month_with_offset.assert_called_once_with(
            date(2026, 8, 21),
            3,
        )


class TestVariableTranslator_Parse:
    def test_returns_input_when_no_variable_exists(
        self, market_holiday: MagicMock, parameter_master: MagicMock
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        access = VariableTranslatorImpl(market_holiday, parameter_master)

        result = access.parse(
            "hello world",
            date(2026, 8, 21),
        )

        assert result == Success("hello world")

    def test_translates_single_variable(
        self, market_holiday: MagicMock, parameter_master: MagicMock
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        access = VariableTranslatorImpl(market_holiday, parameter_master)

        result = access.parse(
            "Today is {%JP$TODAY$yyyyMMdd%}",
            date(2026, 8, 21),
        )

        assert result == Success("Today is 20260821")

    def test_translates_multiple_variables(
        self, market_holiday: MagicMock, parameter_master: MagicMock
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        access = VariableTranslatorImpl(market_holiday, parameter_master)

        result = access.parse(
            "{%JP$TODAY$yyyyMMdd%} / {%JP$NEXTDAY$yyyyMMdd%}",
            date(2026, 8, 21),
        )

        assert result == Success("20260821 / 20260822")

    def test_translates_variable_embedded_in_string(
        self, market_holiday: MagicMock, parameter_master: MagicMock
    ) -> None:
        market_holiday.get_supported_market.return_value = Success(["JP"])

        access = VariableTranslatorImpl(market_holiday, parameter_master)

        result = access.parse(
            "prefix-{%JP$TODAY$yyyyMMdd%}-suffix",
            date(2026, 8, 21),
        )

        assert result == Success("prefix-20260821-suffix")

    def test_propagates_supported_market_failure(
        self, market_holiday: MagicMock, parameter_master: MagicMock
    ) -> None:
        error = DatabaseError(message="Database error")
        market_holiday.get_supported_market.return_value = Failure(error)

        access = VariableTranslatorImpl(market_holiday, parameter_master)

        result = access.parse(
            "{%TODAY$yyyyMMdd%}",
            date(2026, 8, 21),
        )

        assert result == Failure(error)
