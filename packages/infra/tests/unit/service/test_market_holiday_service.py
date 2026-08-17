from datetime import date
from uuid import uuid4

from gyomu_infra.db.repository.market_holiday import MarketHolidayRepository
from gyomu_infra.service.market_holiday import MarketHolidayService
from gyomu_schema.error import GyomuIOError
from gyomu_schema.market_holiday import MarketHoliday
from returns.result import Failure, Result, Success


class DummyMarketHolidayRepository:
    def __init__(self, holidays: list[MarketHoliday]) -> None:
        self._holidays = holidays

    def find_by_market(
        self,
        market: str,
    ) -> Result[list[MarketHoliday], GyomuIOError]:
        return Success([
            holiday
            for holiday in self._holidays
            if holiday.market == market
        ])

class DummyFailureMarketHolidayRepository:
    def find_by_market(
        self,
        market: str,
    ) -> Result[list[MarketHoliday], GyomuIOError]:
        return Failure(
            GyomuIOError("failed to find market holidays")
        )

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

    assert result == Success(holidays[:2])

def test_find_by_market_failure() -> None:
    error = GyomuIOError("failed to find market holidays")

    class DummyFailureMarketHolidayRepository:
        def find_by_market(
            self,
            market: str,
        ) -> Result[list[MarketHoliday], GyomuIOError]:
            return Failure(error)

    repository: MarketHolidayRepository = (
        DummyFailureMarketHolidayRepository()
    )

    service = MarketHolidayService(repository)

    result = service.find_by_market("JP")

    assert result == Failure(error)
