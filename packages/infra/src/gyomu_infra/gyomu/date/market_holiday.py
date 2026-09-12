from gyomu_schema.error.database import DatabaseError
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
    ) -> Result[list[MarketHoliday], DatabaseError]:
        return self._repository.find_by_market(market)

    def get_supported_market(self) -> Result[list[str], DatabaseError]:
        return self._repository.get_supported_market()
