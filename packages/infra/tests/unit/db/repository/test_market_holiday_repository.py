from datetime import date
from unittest.mock import MagicMock

import pytest
from gyomu_schema.error import DatabaseError
from gyomu_schema.market_holiday import MarketHoliday
from returns.result import Failure, Success
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import uuid7

from gyomu_infra.db.model.generated.models import GyomuMarketHoliday
from gyomu_infra.db.repository.sqlalchemy_market_holiday import (
    SqlAlchemyMarketHolidayRepository,
)


def test_find_by_market() -> None:
    id_1 = uuid7()
    id_2 = uuid7()

    models = [
        GyomuMarketHoliday(
            id=id_1,
            market="JP",
            year=2026,
            holiday="2026-01-01",
        ),
        GyomuMarketHoliday(
            id=id_2,
            market="JP",
            year=2026,
            holiday="2026-01-12",
        ),
    ]

    session = MagicMock()
    session.scalars.return_value.all.return_value = models

    repository = SqlAlchemyMarketHolidayRepository(session)

    result = repository.find_by_market("JP")
    assert isinstance(result, Success)
    assert result.unwrap() == [
        MarketHoliday(
            id=id_1,
            market="JP",
            holiday=date(2026, 1, 1),
        ),
        MarketHoliday(
            id=id_2,
            market="JP",
            holiday=date(2026, 1, 12),
        ),
    ]


def test_find_by_market_returns_empty_list_when_no_data() -> None:
    session = MagicMock()
    session.scalars.return_value.all.return_value = []

    repository = SqlAlchemyMarketHolidayRepository(session)

    result = repository.find_by_market("JP")

    assert result == Success([])


def test_find_by_market_uses_market_filter() -> None:
    session = MagicMock()
    session.scalars.return_value.all.return_value = []

    repository = SqlAlchemyMarketHolidayRepository(session)

    repository.find_by_market("JP")

    session.scalars.assert_called_once()

    statement = session.scalars.call_args.args[0]

    compiled = str(statement)

    assert "gyomu_market_holiday.market" in compiled


def test_find_by_market_uses_market_filtecheck_dberror() -> None:
    session = MagicMock()
    session.scalars.side_effect = SQLAlchemyError("database error")

    repository = SqlAlchemyMarketHolidayRepository(session)

    result = repository.find_by_market("#TEST")

    assert isinstance(result, Failure)
    assert isinstance(result.failure(), DatabaseError)


def test_find_by_market_uses_market_filtecheck_othererror() -> None:
    session = MagicMock()
    session.scalars.side_effect = ValueError("unexpected error")

    repository = SqlAlchemyMarketHolidayRepository(session)

    with pytest.raises(ValueError, match="unexpected error"):
        repository.find_by_market("#TEST")


def test_get_supported_market_success() -> None:
    session = MagicMock()
    session.scalars.return_value.all.return_value = ["JP", "US"]

    repository = SqlAlchemyMarketHolidayRepository(session)

    result = repository.get_supported_market()
    assert isinstance(result, Success)
    assert result.unwrap() == ["JP", "US"]
