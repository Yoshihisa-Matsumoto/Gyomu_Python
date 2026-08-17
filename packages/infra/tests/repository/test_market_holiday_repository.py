from datetime import date
from uuid import uuid4
from unittest.mock import MagicMock

from gyomu_infra.db.model.market_holiday import GyomuMarketHoliday
from gyomu_infra.repository.sqlalchemy_market_holiday import (
    SqlAlchemyMarketHolidayRepository,
)
from gyomu_schema.market_holiday import MarketHoliday


def test_find_by_market() -> None:
    id_1 = uuid4()
    id_2 = uuid4()

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

    assert result == [
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

    assert result == []

def test_find_by_market_uses_market_filter() -> None:
    session = MagicMock()
    session.scalars.return_value.all.return_value = []

    repository = SqlAlchemyMarketHolidayRepository(session)

    repository.find_by_market("JP")

    session.scalars.assert_called_once()

    statement = session.scalars.call_args.args[0]

    compiled = str(statement)

    assert "gyomu_market_holiday.market" in compiled
