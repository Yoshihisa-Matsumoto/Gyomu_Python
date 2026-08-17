from typing import Protocol

from gyomu_schema.error import GyomuIOError
from gyomu_schema.market_holiday import MarketHoliday
from returns.result import Result


class MarketHolidayRepository(Protocol):
    def find_by_market(
        self,
        market: str,
    ) -> Result[list[MarketHoliday], GyomuIOError]: ...
