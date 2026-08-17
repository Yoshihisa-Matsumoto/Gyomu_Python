from datetime import date
from uuid import uuid4

from gyomu_infra.repository.market_holiday import MarketHolidayRepository
from gyomu_infra.service.market_holiday import MarketHolidayService
from gyomu_schema.market_holiday import MarketHoliday


class DummyMarketHolidayRepository:
    def __init__(self, holidays: list[MarketHoliday]) -> None:
        self._holidays = holidays

    def find_by_market(
        self,
        market: str,
    ) -> list[MarketHoliday]:
        return [
            holiday
            for holiday in self._holidays
            if holiday.market == market
        ]


def test_find_by_market() -> None:
    holidays = [
        MarketHoliday(
            id=uuid4(),
            market="JP",
            holiday=date(2026, 1, 1),
        ),
        MarketHoliday(
            id=uuid4(),
            market="JP",
            holiday=date(2026, 1, 2),
        ),
        MarketHoliday(
            id=uuid4(),
            market="US",
            holiday=date(2026, 7, 4),
        ),
    ]

    repository: MarketHolidayRepository = DummyMarketHolidayRepository(
        holidays
    )

    service = MarketHolidayService(repository)

    result = service.find_by_market("JP")

    assert result == holidays[:2]
