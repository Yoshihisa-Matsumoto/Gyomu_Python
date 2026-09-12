from typing import Protocol

from gyomu_schema.error.database import DatabaseError
from gyomu_schema.market_holiday import MarketHoliday
from returns.result import Result


class MarketHolidayRepository(Protocol):
    def find_by_market(
        self,
        market: str,
    ) -> Result[list[MarketHoliday], DatabaseError]: ...

    def get_supported_market(self) -> Result[list[str], DatabaseError]: ...
