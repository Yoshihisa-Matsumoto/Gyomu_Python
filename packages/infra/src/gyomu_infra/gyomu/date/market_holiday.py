from gyomu_schema.error import GyomuIOError
from gyomu_schema.market_holiday import MarketHoliday
from returns.result import Result

from gyomu_infra.db.repository.market_holiday import MarketHolidayRepository


class MarketHolidayService:
    def __init__(
        self,
        repository: MarketHolidayRepository,
    ) -> None:
        self._repository = repository

    def find_by_market(
        self,
        market: str,
    ) -> Result[list[MarketHoliday], GyomuIOError]:
        return self._repository.find_by_market(market)
